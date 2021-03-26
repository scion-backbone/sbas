import subprocess

def up(docker_env):
    subprocess.run("docker-compose -d", shell=True, env=docker_env)
    # TODO: Call docker-compose
    # TODO: Install iptables rule `iptables -I FORWARD -s 0.0.0.0/0 -j ACCEPT`
    raise NotImplementedError

def down():
    # TODO: Call docker-compose
    raise NotImplementedError