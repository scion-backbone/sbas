.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install: build/client.json
	systemctl stop bird || true
	systemctl stop sbas || true
	mkdir -p /etc/sbas
	cp build/client.json /etc/sbas
	rm -rf /lib/sbas; mkdir /lib/sbas
	cp -r src /lib/sbas
	ln -fs /lib/sbas/src/main.py /usr/bin/sbas
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	systemctl enable sbas
	systemctl start sbas
	systemctl start bird

build/client.json:
	@ echo "Please run ./configure first."
	@ exit 1
