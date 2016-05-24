#
# This Buildfile uses the sti-builder, which builds an image using RedHat's
# Source To Image technology (https://github.com/openshift/source-to-image)
#
# The builder takes two arguments. The first is the name of the STI builder,
# the second is the name of the final container image to produce.
#

steps:
- name: gcr.io/jessup-spinnaker-test/sti-builder:latest
  args:
  - openshift/ruby-20-centos7 # Change this to your preferred builder image
  - $ContainerImageName
