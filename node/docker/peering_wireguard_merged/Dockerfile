FROM debian:buster

RUN apt-get -o APT::Sandbox::User=root update
RUN apt-get install git socat vim openvpn bird ppp gettext-base -y
RUN git clone https://github.com/PEERINGTestbed/client.git
RUN sed -i '1s/^/router id 184.164.236.1; /' /client/configs/bird6/bird6.conf
RUN rm -r /client/certs
COPY certs/ /client/certs/
COPY prefixes.txt /client/
COPY prefixes6.txt /client/
WORKDIR /client

ARG SBAS_VPN_NET
ARG SBAS_VPN_SERVER_IP
ARG SBAS_VPN_SERVER_IP_NO_MASK
ARG SBAS_VPN_ROUTER_IP_NO_MASK
ARG SBAS_ROUTER_MUX
ARG SBAS_ROUTER_ANNOUNCE_PREFIX

# Add debian backports repo for wireguard packages
RUN echo "deb http://deb.debian.org/debian/ buster-backports main" > /etc/apt/sources.list.d/buster-backports.list

# Install wireguard packges
RUN apt-get update && \
 apt-get install -y --no-install-recommends \
   wireguard-tools iptables nano gettext-base net-tools procps openresolv && \
 apt-get clean

# Add main work dir to PATH
WORKDIR /scripts
ENV PATH="/scripts:${PATH}"

# Do not use iptables masquerade NAT rule
ENV IPTABLES_MASQ=0

# Copy scripts to containers
COPY scripts/install-module /scripts
COPY scripts/run /scripts
COPY scripts/genkeys /scripts
RUN chmod 755 /scripts/*

# Wireguard interface configs go in /etc/wireguard
#VOLUME /etc/wireguard
RUN mkdir /etc/wireguard-templates
COPY conf/wg0.conf /etc/wireguard-templates/

# This is now done at runtime instead
# RUN bash -c "envsubst < /etc/wireguard-templates/wg0.conf > /etc/wireguard/wg0.conf"

# Normal behavior is just to run wireguard with existing configs
CMD ["run"]
#RUN ../client/run.sh
