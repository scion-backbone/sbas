FROM debian:buster

ARG SBAS_VPN_NET

# Add debian backports repo for wireguard packages
RUN echo "deb http://deb.debian.org/debian/ buster-backports main" > /etc/apt/sources.list.d/buster-backports.list

# Install wireguard packges
RUN apt-get update && \
 apt-get install -y --no-install-recommends wireguard-tools iptables nano gettext-base net-tools procps openresolv && \
 apt-get clean

# Add main work dir to PATH
WORKDIR /scripts
ENV PATH="/scripts:${PATH}"

# Do not use iptables masquerade NAT rule
ENV IPTABLES_MASQ=0

# Copy scripts to containers
COPY install-module /scripts
COPY run /scripts
COPY genkeys /scripts
RUN chmod 755 /scripts/*


# Wirguard interface configs go in /etc/wireguard
#VOLUME /etc/wireguard
RUN mkdir /etc/wireguard-templates
COPY server/conf/wg0.conf /etc/wireguard-templates/
RUN bash -c "envsubst < /etc/wireguard-templates/wg0.conf > /etc/wireguard/wg0.conf"

# Normal behavior is just to run wireguard with existing configs
CMD ["run"]
