echo 'deb http://http.debian.net/debian wheezy-backports main' > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get -t wheezy-backports install "ansible"
