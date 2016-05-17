#
# This buildfile expects a Maven pom.xml in the base directory
# The first step will build the maven artifact
# The second step will package the JAR into a Docker image that will run it with the right flags when started
#
steps:
- name: maven:3-jdk-7
  args:
  - mvn
  - package
- name: gcr.io/jessup-spinnaker-test/gcp-springboot:jdk8-nogcp
  args:
  - target/myproject-0.0.1-SNAPSHOT.jar
  - $ContainerImageName
