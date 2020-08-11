cd $(dirname $0)

cmd=""

if [ $1 = '-l' ]; then # local node
    cmd="print(db['$SBAS_NODE']['$2'])"
elif [ $1 = '-r' ]; then # remote nodes
    if [ -z "$2" ]; then # just list names
        cmd="print('\n'.join(n for n in db.keys() if n != '$SBAS_NODE'))"
    else # list values for key
        cmd="print('\n'.join(db[n]['$2'] for n in db if n != '$SBAS_NODE'))"
    fi
fi

python3 -c "\
import json;\
f = open('nodes.json', 'r');\
db = json.load(f);\
f.close();\
$cmd\
"
