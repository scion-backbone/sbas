.PHONY: install

SCION=/etc/scion
SYSTEMD=/lib/systemd/system

install:
	mkdir -p /etc/sbas /var/sbas
	rm -rf /lib/sbas; cp -r src /lib/sbas	
	ln -fs /lib/sbas/main.py /usr/bin/sbas
	cp etc/sig.toml ${SCION}
	cp etc/sbas.service ${SYSTEMD}/sbas.service
	systemctl daemon-reload
	systemctl enable --now sbas