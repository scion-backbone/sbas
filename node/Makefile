.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install: build/nodename
	systemctl stop bird || true
	systemctl stop sbas || true
	systemctl stop wg-quick@wg0 || true
	mkdir /tmp/bird_log_mrt || true
	chmod 777 /tmp/bird_log_mrt
	mkdir -p /etc/sbas /var/sbas
	cp build/nodes.json build/clients.json build/nodename build/topology.json /etc/sbas
	cp build/topology.json /etc/scion
	rm -rf /lib/sbas; mkdir /lib/sbas
	cp -r src /lib/sbas
	ln -fs /lib/sbas/src/main.py /usr/bin/sbas
	cp etc/sig.toml ${SCION}
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	systemctl start sbas
	systemctl start wg-quick@wg0
	systemctl start bird

build/nodename:
	@ echo "Please run ./configure first."
	@ exit 1
