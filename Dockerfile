# - build with `docker build --tag sbas-client .`
# - start the container with `docker run -d --name sbas-client --privileged --cap-add=NET_ADMIN --cap-add=SYS_MODULE -v /sys/fs/cgroup:/sys/fs/cgroup:ro sbas-client`
# - get a shell in the container with `docker exec -it sbas-client /bin/bash`
# - in the container run `./configure`, if required adapt ./build/client.json, and then run `make` to run sbas. Restart the sbas service with `systemctl restart sbas.service` when ever making configuration changes.

FROM ubuntu:jammy

RUN apt-get update && apt-get install -y \
    bird2 \
    git \
    iproute2 \
    python3 \
    python3-pip \
    systemd \
    vim \
    wireguard \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install mrtparse pyroute2


# systemd
# Based on: https://developers.redhat.com/blog/2014/05/05/running-systemd-within-docker-container/
#  - converted to ubuntu, i.e. fixed some paths and removed unnecessary cleanup
#  - keep systemd-user-sessions.service, to allow login through SSH (login disabled on startup until this is run)
ENV container docker
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i = systemd-tmpfiles-setup.service ] || rm -f $i; done); \
(cd /lib/systemd/system/multi-user.target.wants/; for i in *; do [ $i = systemd-user-sessions.service ] || rm -f $i; done); \
rm -f /etc/systemd/system/*.wants/*; \
rm -f /lib/systemd/system/local-fs.target.wants/*; \
rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
rm -f /lib/systemd/system/basic.target.wants/*;
VOLUME [ "/sys/fs/cgroup" ]
# Follow instructions from: https://developers.redhat.com/blog/2016/09/13/running-systemd-in-a-non-privileged-container
# to drop the requirement of running the container as privileged.


WORKDIR sbas-client
RUN git init -q && git remote add origin https://github.com/scion-backbone/sbas.git
RUN git fetch -q --depth 1 origin HEAD && git checkout -q FETCH_HEAD -- client
WORKDIR /sbas-client/client
CMD ["/bin/systemd"]