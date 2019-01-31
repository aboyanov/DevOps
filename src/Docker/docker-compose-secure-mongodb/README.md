This is example of how to create and running mongodb in a container using docker-compose and also create user and working database on first start

Do not forget to add the '.env' file to your '.gitignore' and leave only '.env.dist' to be pushed to your reppo for explanatory purpose.

Explanation / how it works:

The only way to create a db and a user on the initialization of the container is with .sh or .js script located in the /docker-entrypoint-initdb.d/ folder inside the container. The docker-entrypoint.sh will execute all the .sh/.js files located in that directory. This solution will place all scripts from ./mongo_setups/* to the /docker-entrypoint-initdb.d/ in the container. the ./mongo_setups/setup.sh will connect to the admin db and create user using the params from ./.env file.
