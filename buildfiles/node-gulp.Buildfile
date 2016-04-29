#
# This buildfile expects a gulpfile and Dockerfile in the base directory
# It will run the gulp build, and then run the Docker build
#
steps:
- name: webfatorial/docker-gulp:0.2.3
  args:
  - gulp
  - build
- name: gcr.io/cloud-builders/dockerizer
  args:
  - $ContainerImageName
