Dont forget;

chmod +x mysql-start.sh

After run this command mysql-start.sh

docker exec -it mysql-server-1 bash

mysql -u root -p

create database traindb;

GRANT ALL PRIVILEGES ON traindb.* TO 'train'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;

exit

mysql -u train -p -D traindb

uvicorn mainapp.main:app --host 0.0.0.0 --port 8002 --reload