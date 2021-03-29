import subprocess

DOCKER_PATH = "/lib/sbas/docker"

def build(docker_env):
    print("Building Docker container...")
    subprocess.run("docker-compose build", shell=True, cwd=DOCKER_PATH, env=docker_env).check_returncode()

def up(docker_env):
    subprocess.run("docker-compose up -d", shell=True, cwd=DOCKER_PATH, env=docker_env).check_returncode()
    subprocess.run(["iptables", "-I", "FORWARD", "-s", "0.0.0.0/0", "-j", "ACCEPT"]).check_returncode()

def down():
    subprocess.run("docker-compose down", shell=True, cwd=DOCKER_PATH).check_returncode()
