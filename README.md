# Log Reminder

It reminds the team members to push their work logs at the start of every month and if they still didn't push we remind them again everyday.

## Requirements
* Python 3.6 (and various dependencies e.g virtualenv, Django, Celery, Supervisord, docker-compose, gunicorn, bleach).
* Local Mail Transfer Agent (I setup mine using [this guide](https://opensource.com/article/18/8/postfix-open-source-mail-transfer-agent)).
* Docker (we need rabbitmq for celery).

## Setup (Ubuntu)

### Optional (Setup non-root user)
```bash
useradd app -Um --shell /usr/bin/bash
su - app
```

### Installation instructions
```bash
git clone https://github.com/ahmedbilal/log-reminder.git && cd log-reminder

sudo apt install docker.io git python3-pip nano pwgen nginx
sudo systemctl enable --now docker
sudo usermod -aG docker app && exit
su - app
cd log-reminder

pip3 install virtualenv
virtualenv venv
source venv/bin/activate

pip3 install django celery supervisor docker-compose gunicorn bleach

# Update username and password for rabbitmq
# Update RABBITMQ_DEFAULT_USER=user and RABBITMQ_DEFAULT_PASS=pass under environment section and take note of this password somewhere as we would need it soon
nano docker-compose.yml

nano logreminder/logreminder/private.py
```

Now, paste the following content there and edit it accordingly. For example, create a strong random secret key for django (you can run `pwgen 50 -ycs 1` to create a strong secret key). In short, update `SECRET_KEY`, `CELERY_BROKER_URL`, `ALLOWED_HOSTS`, `DOMAIN` (this is used to create confirmation link, so put actual domain on which the application is running).

```python
PROTOCOL = "http"
DOMAIN = "localhost"
PORT = 80
SECRET_KEY = "secret_key_for_django"
CELERY_RESULT_BACKEND = "rpc://"
CELERY_BROKER_URL = "amqp://user:password@localhost//"
DEBUG = False
ALLOWED_HOSTS = ["your_ip_address_here"]
```
after saving the file, run the following commands
```bash
(cd logreminder && python manage.py migrate && python manage.py collectstatic && sudo chown :www-data static -R)

# Keep note of username and password as you would need it to login to admin panel
python manage.py createsuperuser

# The following would start supervisord which would in turn start our application, celery worker and rabbitmq container.
supervisord
```


Now, you should setup `nginx`. A sample (HTTP only) configuration is provided as following


```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;
    location /static/ {
        root /path/to/static/;
    }
    location / {
        include proxy_params;
        proxy_pass http://localhost:8000;
    }
}
```
