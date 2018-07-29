# Install Jenkins<a name="install-jenkins"></a>

This guide show how to install Jenkins as a standalone and under Apache Tomcat on CentOS 7\.

**Standalone** 
 
Here are the commands used in this lesson:

```
sudo yum -y install git java-1.8.0-openjdk
sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo
sudo rpm --import https://jenkins-ci.org/redhat/jenkins-ci.org.key
sudo yum -y install jenkins-2.89.4
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

You can check the Jenkins log like so:
```
sudo tail -f /var/log/jenkins/jenkins.log
```
Once you install Jenkins, you will need the temporary admin password to complete setup in the browser. You can get the temporary admin password with this command:

```
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Under Apache Tomcat**

1. Install Tomcat\.

    ```
    sudo yum install java-1.8.0-openjdk
    sudo groupadd tomcat
    sudo useradd -M -s /bin/nologin -g tomcat -d /opt/tomcat tomcat
    wget http://apache.cbox.biz/tomcat/tomcat-8/v8.5.32/bin/apache-tomcat-8.5.32.tar.gz
    sudo mkdir /opt/tomcat
    sudo tar xvf apache-tomcat-8*tar.gz -C /opt/tomcat --strip-components=1
    cd /opt/tomcat
    sudo chgrp -R tomcat /opt/tomcat
    sudo chmod -R g+r conf
    sudo chmod g+x conf
    sudo chown -R tomcat webapps/ work/ temp/ logs/
    sudo vi /etc/systemd/system/tomcat.service
    ```

    Now you need to configure the tomcat service file\.
   
    For example like that:

    ```
    # Systemd unit file for tomcat
    [Unit]
    Description=Apache Tomcat Web Application Container
    After=syslog.target network.target

    [Service]
    Type=forking

    Environment=JAVA_HOME=/usr/lib/jvm/jre
    Environment=CATALINA_PID=/opt/tomcat/temp/tomcat.pid
    Environment=CATALINA_HOME=/opt/tomcat
    Environment=CATALINA_BASE=/opt/tomcat
    Environment='CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC'
    Environment='JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom'

    ExecStart=/opt/tomcat/bin/startup.sh
    ExecStop=/bin/kill -15 $MAINPID

    User=tomcat
    Group=tomcat
    UMask=0007
    RestartSec=10
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```
   
    Then start the tomcat service:
   
    ```
    sudo systemctl daemon-reload
    sudo systemctl start tomcat
    ```
    
    Now you will need to add user and apply role to it:
    
    ```
    sudo vi /opt/tomcat/conf/tomcat-users.xml         
    ```
    
    Add the following lines under users:
    
    ```
    <role rolename="manager-gui"/>
    <user username="username" password="password" roles="manager-gui,admin-gui"/>
    ```
   
1. Download the jenkins .war file and place it `/opt/tomcat/webapps`:

    ```
    sudo wget -O /opt/tomcat/webapps http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo
    ```

1. Now when you try to access it in the browser, Tomcat will automatically deploy the `jenkis.war` file:
    
    Go to your browser and type: `http://your_public_ip:8080/jenkins`

1. Get the jenkins initial pass like that:
    
    ```
    sudo cat /var/lib/jenkins/secrets/initialAdminPassword
    ```

1. Voila! now you have jenkins installed and hosted by Apache Tomcat