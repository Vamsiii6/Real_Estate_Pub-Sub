# Real Estate Information Pub-Sub Model

# Steps to Deploy

You need to install docker in your system to run this project

Check the link to install Docker based on your system https://docs.docker.com/get-docker/

This project uses port 8080 5000 and 3003 on your local system ensure these ports are free. Inscase they are used already use

```
lsof -i :<port number>
```

Kill the list of process listed to ensure the ports are free to be deployed using the below command

```
kill -9 <PID>
```

To run the docker container use the below command

```
docker compose up
```

Once the app is deployed Now enter http://localhost:8080/list in the browser to open view the app
