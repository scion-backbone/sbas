import subprocess

DOCKER_PATH = "/lib/sbas/docker"

def build():
    print("Building Docker container...")
    subprocess.run("docker-compose build", shell=True, cwd=DOCKER_PATH).check_returncode()

def up():
    subprocess.run("docker-compose up -d", shell=True, cwd=DOCKER_PATH).check_returncode()
    subprocess.run(["iptables", "-I", "FORWARD", "-s", "0.0.0.0/0", "-j", "ACCEPT"]).check_returncode()

def down():
    subprocess.run("docker-compose down", shell=True, cwd=DOCKER_PATH).check_returncode()
