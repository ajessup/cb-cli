#
# This buildfile expects a Maven pom.xml and Dockerfile in the base directory
# It will build the default Maven artifact, and then run the Docker build
#
steps:
- name: maven:3-jdk-7
  args:
  - mvn
  - package
- name: gcr.io/cloud-builders/dockerizer
  args:
  - $ContainerImageName
