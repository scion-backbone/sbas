import subprocess

DOCKER_PATH = "/lib/sbas/docker"

def build(docker_env):
    print("Building Docker container...")
    subprocess.run("docker-compose build", shell=True, cwd=DOCKER_PATH, env=docker_env)

def up(docker_env):
    subprocess.run("docker-compose up -d", shell=True, cwd=DOCKER_PATH, env=docker_env)
    subprocess.run("iptables", "rule", "iptables", "-I", "FORWARD", "-s", "0.0.0.0/0", "-j", "ACCEPT")

def down():
    subprocess.run("docker-compose down", shell=True, cwd=DOCKER_PATH)
