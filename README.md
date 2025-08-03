#### Build project containers
- Powershell
```sh
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```
- Linux terminal
```sh
chmod 755 dojo/entrypoint_local.sh
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```

if there is an update, run:
```sh
docker compose --env-file .env_local -f docker-compose-local.yml down -v
docker rm nginx
docker rm web
docker compose --env-file .env_local -f .\docker-compose-local.yml build nginx
docker compose --env-file .env_local -f .\docker-compose-local.yml build web_local
docker-compose --env-file .env_local -f docker-compose-local.yml up -d
```

Push docker hub image
```sh
docker tag karate_site-web elph4nt0m/karate_site-web:v1.0
docker push elph4nt0m/karate_site-web:v1.0
```

Once docker containers are running, we can launch ngrok
```sh
ngrok http 8000
```

Create superuser
```sh
python manage.py createsuperuser
```

Load initial test data
```sh
python manage.py create_test_dataset
```

### Test local ssl
```sh
pip install django-sslserver
```
Add to installed apps in settings.py
```python
INSTALLED_APPS = [
    'sslserver',
    '...'
]
```
Run the code using runsslserver instead of runserver. Certificate & key are optional
```sh
python manage.py runsslserver --certificate /path/to/certificate.crt --key /path/to/key.key
```
