cd $(dirname $0)

cmd=""

if [ $1 = '-l' ]; then # local node
    cmd="print(db['$SBAS_NODE']['$2'])"
elif [ $1 = '-r' ]; then # remote nodes
    if [ $# = 1 ]; then # just list names
        cmd="print('\n'.join(n for n in db.keys() if n != '$SBAS_NODE'))"
    elif [ $# = 2 ]; then # get values for all remotes
        cmd="print('\n'.join(db[n]['$2'] for n in db if n != '$SBAS_NODE'))"
    else # get value for specific remote
        cmd="print(db['$2']['$3'])"
    fi
fi

python3 -c "\
import json;\
f = open('nodes.json', 'r');\
db = json.load(f);\
f.close();\
$cmd\
"
