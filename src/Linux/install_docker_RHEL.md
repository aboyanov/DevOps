# FIX Installing Docker on AWS Linux 2 AMI<a name="installing-docker"></a>

This simple guide is to show how to install docker on CentOs 7 and avoid errors due the installation.
I had this problem, when trying to install docker on AWS Linux 2 AMI.


**Below I am listing steps to install docker-ce on RHEL.**

1. First install yum utils\.

   ```
   sudo yum install -y yum-utils
   ```

1. Add the docker repository\.

   ```
   sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
   ```

1. Make cache fast\.

   ```
   sudo yum makecache fast
   ```
   
**Important**  
To avoid Errors during the installation run following commands before that\.

1. To avoid Error: “Requires: container-selinux >= 2.9”\.

   ```
   sudo yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.42-1.gitad8f0f7.el7.noarch.rpm
   ```
   
1. To avoid Error: “libtool-ltdl-2.4.2-22.el7_3.x8 FAILED”\.

   ```
   sudo yum install http://mirror.centos.org/centos/7/os/x86_64/Packages/libtool-ltdl-2.4.2-22.el7_3.x86_64.rpm
   ```
   
1. To avoid Error: Package: docker-ce-18.03.1.ce-1.el7.centos.x86_64 (docker-ce-stable) Requires: pigz\.

   ```
   sudo yum install yum install http://mirror.centos.org/centos/7/extras/x86_64/Packages/pigz-2.3.3-1.el7.centos.x86_64.rpm
   ```
   
**Now continue with the installation of docker**

   ```
   sudo yum -y install docker-ce
   ```
   
**Test if docker is running with command**

   ```
   sudo systemctl start docker
   ```
