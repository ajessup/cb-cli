import click
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient.errors import HttpError
import json
import string
import tarfile
import tempfile
import time
import os
import yaml

from oauth2client.client import GoogleCredentials

@click.command()
@click.argument('image')
@click.argument('path', default='.', type=click.Path(exists=True))
@click.option('--buildfile', default=None,
              help='Path to the buildfile to use to configure the build')
@click.option('--bucket', default=None,
              help='Bucket to store source archive in. Defaults to \%projectname\%-cbstorage')
@click.option('--project-id', default=None,
              help='Cloud platform project ID. If not set, will look in the environment variable GCP_PROJECT_ID.')
def build(path, image, buildfile, project_id, bucket):
    path = os.path.join(os.getcwd(), path)

    if buildfile is None:
        buildfile = os.path.join(path, 'Buildfile')

    project_id = project_id or os.getenv('GCP_PROJECT_ID')
    if project_id is None:
        raise click.UsageError('No project ID specified. Pass option --project-id or set GCP_PROJECT_ID')

    if bucket is None:
        bucket = '%s-cbstorage' % project_id

    credentials = GoogleCredentials.get_application_default()

    buildfile = os.path.abspath(buildfile)
    if not os.path.exists(buildfile):
        raise click.UsageError('Could not find buildfile %s, please add one or use --buildfile to specify one' % buildfile)

    # Parse buildfile
    with open(buildfile, 'r') as stream:
        build_config_text=string.Template(stream.read()).substitute(ContainerImageName=image)

    build_config = yaml.load(build_config_text)

    cb_request_body = {
        "source": {
            "storageSource": {
                "bucket": bucket,
                "object": ''
            }
        },
        "steps": [],
        "images": [
            image
        ]
    }

    for step in build_config['steps']:
        step_name = str(step['name'])
        step_args = []
        if step['args'] and isinstance(step['args'], list):
            for arg in step['args']:
                step_args.append(str(arg))
        cb_request_body['steps'].append({
            'name': step_name,
            'args': step_args
        })

    click.echo('Building %s to %s with %s' % (path, image, buildfile))

    # Create temporary archive for the source directory
    archive = tempfile.NamedTemporaryFile(delete=False,suffix='.tar.gz')
    tar = tarfile.open(fileobj=archive, mode='w:gz')

    click.echo("Archiving %s to %s" % (path, archive.name))
    for spath, subdirs, files in os.walk(path):
        for name in files:
            print 'Adding %s' % os.path.relpath(os.path.join(spath, name),path)
            tar.add(os.path.join(spath, name), recursive=False,
                    arcname=os.path.relpath(os.path.join(spath, name),path))

    tar.close()
    archive.close()

    cb_request_body['source']['storageSource']['object'] = os.path.basename(archive.name)

    # Upload the source directory to GCS
    click.echo('Checking for bucket %s...' % bucket)
    gcs_service = discovery.build('storage', 'v1', credentials=credentials)
    req = gcs_service.buckets().get(bucket=bucket)
    try:
        req.execute()
    except HttpError, hell:
        if hell.resp.status == 404:
            click.echo('Bucket %s not found, attempting to create it...' % bucket)
            body = {
                'name': bucket,
            }
            req = gcs_service.buckets().insert(project=project_id, body=body)
            resp = req.execute()
        else:
            raise hell

    click.echo('Uploading %s to %s...' % (os.path.basename(archive.name), bucket))
    try:
        body = {
            'name': os.path.basename(archive.name),
        }
        media = http.MediaFileUpload(archive.name, mimetype='application/x-gzip', chunksize=4194304, resumable=True)
        req = gcs_service.objects().insert(
            bucket=bucket,
            name=os.path.basename(archive.name),
            media_body=media,
            body={"cacheControl": "public,max-age=31536000"}
        )
        resp = None
        while resp is None:
            status, resp = req.next_chunk()
            if status:
                print "Uploaded %d%%." % int(status.progress() * 100)
        click.echo('...done!')
    except HttpError, amy:
        if amy.resp.status == 403:
            raise click.UsageError('You don\'t have permission to write to GCS bucket %s. Fix this or specify a different bucket to use.' % bucket)
        else:
            raise amy

    # Invoke the container builder API
    ccb_service = discovery.build('cloudbuild', 'v1', credentials=credentials,
        discoveryServiceUrl="https://content-cloudbuild.googleapis.com/$discovery/rest?version=v1")

    req = ccb_service.projects().builds().create(
        projectId=project_id, body=cb_request_body)

    resp = req.execute()

    if resp['metadata']['build']['status'] == 'QUEUED':
        click.echo('Queued build %s' % resp['metadata']['build']['id'])

        operation_id = resp['name']
        while (resp['metadata']['build']['status'] == 'QUEUED' or
              resp['metadata']['build']['status'] == 'WORKING'):
            resp = ccb_service.operations().get(name=operation_id).execute()
            click.echo('Building... %s' % resp['metadata']['build']['status'])
            time.sleep(1)

    if resp['metadata']['build']['status'] == 'SUCCESS':
        resp = ccb_service.operations().get(name=operation_id).execute()
        for image in resp['metadata']['build']['results']['images']:
            click.echo('Built %s' % image['name'])
            click.echo('(Image digest: %s)' % image['digest'])
    else:
        click.echo('Build returned %s - check build ID %s' %
                   (resp['metadata']['build']['status'],
                    resp['metadata']['build']['id']))

if __name__ == '__main__':
    build()
