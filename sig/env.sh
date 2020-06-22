sudo apt-get install docker docker-compose

sudo apt-get install g++ unzip zip
wget https://github.com/bazelbuild/bazel/releases/download/1.2.0/bazel-1.2.0-installer-linux-x86_64.sh
bash ./bazel-1.2.0-installer-linux-x86_64.sh --user
rm ./bazel-1.2.0-installer-linux-x86_64.sh

cd ~
wget https://dl.google.com/go/go1.13.3.linux-amd64.tar.gz
tar -xvf go*.tar.gz
sudo mv go /usr/local
echo 'export GOPATH="$HOME/go"' >> ~/.profile
echo 'export GOROOT="/usr/local/go"' >> ~/.profile
echo 'export PATH="$HOME/.local/bin:$GOPATH/bin:$GOROOT:$PATH"' >> ~/.profile
source ~/.profile
mkdir -p "$GOPATH"

mkdir -p "$GOPATH/src/github.com/scionproto"
cd "$GOPATH/src/github.com/scionproto"
git clone https://github.com/netsec-ethz/scion
cd scion
pip3 install setuptools
./env/deps
./scion.sh test
