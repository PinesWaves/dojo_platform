Build project containers:
- Powershell
```sh
docker-compose -f .\docker-compose-local.yml up -d
```
- Linux terminal
```sh
chmod 755 dojo/entrypoint.sh
docker-compose -f docker-compose-local.yml up -d
```

if there is an updated, run:
```sh
docker-compose -f .\docker-compose-local.yml down
docker rm nginx
docker rm web
docker-compose -f .\docker-compose-local.yml build nginx
docker-compose -f .\docker-compose-local.yml build web
docker-compose -f .\docker-compose-local.yml up -d
```

Once docker containers are running, we can launch ngrok
```sh
ngrok http 443
```

Create superuser
