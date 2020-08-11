cd $(dirname $0)

cmd=""

if [ $1 = '-n' ]; then # list all nodes
    cmd="print('\n'.join(db.keys()))"
elif [ $1 = '-r' ]; then # list values for key over all remote nodes
    cmd="print('\n'.join(db[n]['$2'] for n in db if n != '$SBAS_NODE'))"
else [ $1 = '-l' ]; # output single value for local node
    cmd="print(db['$SBAS_NODE']['$1'])"
fi

python3 -c "\
import json;\
f = open('nodes.json', 'r');\
db = json.load(f);\
f.close();\
$cmd\
"
