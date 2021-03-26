.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install: build/nodename
	mkdir -p /etc/sbas /var/sbas
	cp build/nodes.json build/nodename /etc/sbas
	rm -rf /lib/sbas; mkdir /lib/sbas
	cp -r src /lib/sbas/src	
	cp -r docker /lib/sbas/docker	
	ln -fs /lib/sbas/src/main.py /usr/bin/sbas
	cp etc/sig.toml ${SCION}
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	sbas configure
	systemctl enable --now sbas

build/nodename:
	@ echo "Please run ./configure first."
	@ exit 1
