#
# This buildfile expects a Dockerfile in the base directory
# It will run Docker build on the target directory
#
steps:
- name: gcr.io/cloud-builders/dockerizer
  args:
  - $ContainerImageName
