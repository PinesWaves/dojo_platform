#### Build project containers
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
```sh
python manage.py createsuperuser
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
