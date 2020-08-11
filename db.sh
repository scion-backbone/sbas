cd $(dirname $0)

cmd=""

if [ $1 = '-n' ]; then # list all nodes
    cmd="print('\n'.join(db.keys()))"
elif [ $1 = '-k' ]; then # list value for key over all nodes
    cmd="print('\n'.join(db[n]['$2'] for n in db))"
else # output single value
    cmd="print(db['$1']['$2'])"
fi

python3 -c "\
import json;\
f = open('nodes.json', 'r');\
db = json.load(f);\
f.close();\
$cmd\
"
