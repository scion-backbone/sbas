export SC=/etc/scion
export ISD=$(ls /etc/scion/gen/ | grep ISD | awk -F 'ISD' '{ print $2 }')
export AS=$(ls /etc/scion/gen/ISD${ISD}/ | grep AS | awk -F 'AS' '{ print $2 }')
export IA=${ISD}-${AS}

cd ~
git clone -b scionlab https://github.com/netsec-ethz/scion

sudo mkdir -p ${SC}/gen/ISD${ISD}/AS${AS}/sig${IA}-1/

cd ~/scion/go/sig
go install
go build -o ${GOPATH}/bin/sig ~/scion/go/sig/main.go

# Enable routing
sudo setcap cap_net_admin+eip ${GOPATH}/bin/sig
sudo sysctl net.ipv4.conf.default.rp_filter=0
sudo sysctl net.ipv4.conf.all.rp_filter=0
sudo sysctl net.ipv4.ip_forward=1
