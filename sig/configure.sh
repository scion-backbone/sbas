export SC=/etc/scion
export LOG=/var/log/scion
export ISD=$(ls /etc/scion/gen/ | grep ISD | awk -F 'ISD' '{ print $2 }')
export AS=$(ls /etc/scion/gen/ISD${ISD}/ | grep AS | awk -F 'AS' '{ print $2 }')
export IA=${ISD}-${AS}
export IAd=$(echo $IA | sed 's/_/\:/g')
export sigID='sigSBAS'

export SIGCONF=${SC}/gen/ISD${ISD}/AS${AS}/sig${IA}-1/${sigID}.config
sudo cp sig.config $SIGCONF

# Replace variables in config file
for var in 'SC' 'LOG' 'ISD' 'AS' 'IA' 'IAd' 'sigID' 'sigIP'
do
    sudo sed -i "s/\${$var}/$var/g" $SIGCONF
done

# TODO: Generate traffic rules from SBAS node list (../nodes.json)
# TODO: Add SIG entry to topology files
