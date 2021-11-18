.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install: build/nodename
	systemctl stop sbas || true
	mkdir -p /etc/sbas /var/sbas
	mkdir -p /var/sbas/bird_log_mrt
	chmod 777 /var/sbas/bird_log_mrt
	cp build/nodes.json build/clients.json build/nodename build/topology.json /etc/sbas
	cp build/topology.json /etc/scion
	rm -rf /lib/sbas; mkdir /lib/sbas
	cp -r src /lib/sbas
	ln -fs /lib/sbas/src/main.py /usr/bin/sbas
	cp etc/sig.toml ${SCION}
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	systemctl start sbas
	sysctl -w net.ipv4.ip_forward=1

build/nodename:
	@ echo "Please run ./configure first."
	@ exit 1
