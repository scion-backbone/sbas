FROM ubuntu
RUN apt-get -o APT::Sandbox::User=root update
RUN apt-get install git socat vim openvpn bird ppp -y
RUN git clone https://github.com/PEERINGTestbed/client.git
RUN sed -i '1s/^/router id 184.164.236.1; /' /client/configs/bird6/bird6.conf
RUN rm -r /client/certs
COPY certs/ /client/certs/
WORKDIR /client
RUN ip route add 184.164.236.0/24 via 172.16.0.2 dev eth0
