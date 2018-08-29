echo 'deb http://http.debian.net/debian-backports squeeze-backports(-sloppy) main' > /etc/apt/sources.list.d/backports.list
apt-get update
apt-get -t squeeze-backports install "ansible"
