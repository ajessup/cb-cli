# cb-cli - An Unofficial CLI tool for Google Cloud Container Builder

[Google Cloud Container Builder](https://cloud.google.com/container-builder/docs/)
is a powerful tool for building Container Images quickly and efficiently from source 
and storing them in Google Container Registry (GCR). While Container Builder
supports Dockerfiles to configure builds it also supports other methods of 
building images more safely and efficiently.

This CLI provides a handy mechanism for accessing the API for building Container
images from local source, and introduces Buildfiles for describing Container
Builder configurations.

## Installation

The recommended way to install this tool is from pypy via pip.

 `pip install cbcli`

## Authentication

This tool uses Application Default Credentials to authenticate to the Google
Cloud Platform. To use these, download the Google Cloud SDK and run:

 `gcloud beta auth application-default login`

prior to running the script. Read more on Google's
[documentation](https://developers.google.com/identity/protocols/application-default-credentials#whentouse)

You might also want to set your project ID for the tool to use if you don't want to keep passing it on the command line each time. You can do that with:

 `export GCP_PROJECT_ID=your-project-id`

## Basic Usage

To build a Container Image from source, add a Buildfile to the base directory
of the application's source tree, then run the Container Builder CLI.

 `cbcli gcr.io/your-project-id/image-name`

The Buildfile describes how your source code should be transformed into a Docker
image, and is run remotely using the Cloud Container Builder service.

## Buildfiles

Buildfiles describe a set of *build steps* that are run in serial against your
source tree to produce a Docker image.

To help get you started, here are some useful Buildfiles.

* Build any Docker container from a Dockerfile [Buildfile](buildfiles/docker.Buildfile)
* Build a lean Spring Boot application from source using a Maven pom.xml file [Buildfile](buildfiles/springboot.Buildfile)
* Build a Node.js application from a Gulp configuration file [Buildfile](buildfiles/node-gulp.Buildfile)

A build step is itself simply a Docker image within which your
source will be transiently mounted in a special directory. You can customize
the arguments, environment variables and parameters used to invoke a build step,
making them easy to configure.

## TODOs

* Add Stacksmith integration
* Better build/poll UI
* Add automatic creation of buildfiles
