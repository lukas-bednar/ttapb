FROM centos:7
MAINTAINER Karim Boumedhel <karimboumedhel@gmail.com>

RUN yum -y install git epel-release && yum -y install python-pip && yum clean all && rm -rf /var/cache/yum
RUN pip install ttapb

ENTRYPOINT ["/usr/bin/ttapb"]
