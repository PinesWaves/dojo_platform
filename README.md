Build project containers:
```sh
docker-compose -f .\docker-compose-local.yml up -d 
```

if libs are updated, run:
```sh
docker-compose -f .\docker-compose-local.yml down
docker-compose -f .\docker-compose-local.yml build web
docker-compose -f .\docker-compose-local.yml up -d
```
