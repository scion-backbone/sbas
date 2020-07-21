FROM ubuntu
RUN apt-get -o APT::Sandbox::User=root update
RUN apt-get install git socat vim openvpn bird ppp -y
RUN git clone https://github.com/PEERINGTestbed/client.git
RUN sed -i '1s/^/router id 184.164.236.1; /' /client/configs/bird6/bird6.conf
RUN rm -r /client/certs
COPY certs/ /client/certs/
COPY run.sh /client/
WORKDIR /client
