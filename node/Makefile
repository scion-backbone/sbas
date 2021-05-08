.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install: build/nodename
	systemctl stop sbas || true
	systemctl stop wg-quick@wg0 || true
	mkdir -p /etc/sbas /var/sbas
	cp build/nodes.json build/nodename build/topology.json /etc/sbas
	rm -rf /lib/sbas; mkdir /lib/sbas
	cp -r src docker /lib/sbas
	ln -fs /lib/sbas/src/main.py /usr/bin/sbas
	cp etc/sig.toml ${SCION}
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	systemctl enable sbas
	systemctl start sbas
	systemctl enable wg-quick@wg0
	systemctl start wg-quick@wg0

build/nodename:
	@ echo "Please run ./configure first."
	@ exit 1
