# cb-cli - An Unofficial CLI tool for Google Cloud Container Builder

Google Cloud Container Builder is a powerful tool for building Container Images
quickly and efficiently from source and storing them in Google Container
Registry (GCR). While Container Builder supports Dockerfiles to configure builds
it also supports other methods of building images more safely and efficiently.

This CLI provides a handy mechanism for accessing the API for building Container
images from local source, and introduces Buildfiles for describing Container
Builder configurations.

## Authentication

This tool uses Application Default Credentials to authenticate to the Google
Cloud Platform. To use these, download the Google Cloud SDK and run:

 `gcloud beta auth application-default login`

prior to running the script. Read more on Google's
[documentation](https://developers.google.com/identity/protocols/application-default-credentials#whentouse)

## Basic Usage

To build a Container Image from source, add a Buildfile to the base directory
of the application's source tree, then run the Container Builder CLI.

 `./cb-cli.py gcr.io/your-project-id/image-name`

The Buildfile describes how your source code should be transformed into a Docker
image, and is run remotely using the Cloud Container Builder service.

## Buildfiles (not yet supported)

Buildfiles describe a set of *build steps* that are run in serial against your
source tree to produce a Docker image.

To help get you started, here are some useful Buildfiles.

* Build any Docker container from a Dockerfile
* Build a lean Spring Boot application from source using a Maven pom.xml file
* Build a Node.js application from a Gulp configuration file

A build step is itself simply a Docker image within which your
source will be transiently mounted in a special directory. You can customize
the arguments, environment variables and parameters used to invoke a build step,
making them easy to configure.

## TODOs

* Add pip install support
* Better build/poll UI
* Add automatic creation of buildfiles
