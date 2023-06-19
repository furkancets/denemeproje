docker run --name mysql-server-1 -p 3309:3306 -v /opt/data:/etc/mysql/conf.d -e MYSQL_ROOT_PASSWORD=Ankara06 -e MYSQL_USER=train -e MYSQL_PASSWORD=Ankara06 -d mysql
