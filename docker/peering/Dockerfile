FROM ubuntu
RUN apt-get -o APT::Sandbox::User=root update
RUN apt-get install git socat vim openvpn bird ppp gettext-base -y
RUN git clone https://github.com/PEERINGTestbed/client.git
RUN sed -i '1s/^/router id 184.164.236.1; /' /client/configs/bird6/bird6.conf
RUN rm -r /client/certs
COPY certs/ /client/certs/
COPY run.sh /client/run.sh.template
COPY prefixes.txt /client/
COPY prefixes6.txt /client/
WORKDIR /client

ARG SBAS_VPN_NET
ARG SBAS_VPN_NET_REMOTE
ARG SBAS_VPN_SERVER_IP
ARG SBAS_VPN_SERVER_IP_NO_MASK
ARG SBAS_ROUTER_MUX
ARG SBAS_ROUTER_ANNOUNCE_PREFIX
RUN bash -c "envsubst < run.sh.template > run.sh"
RUN chmod 755 run.sh