## Pre-requisites

- Python 3.10
- PostgreSQL

## Running the project

First create an environment

```bash
python -m venv django-env
```

Then activate it

```bash
source django-env/bin/activate
```

Then install the requirements

```bash
pip install -r requirements.txt
```

Then create a .env file with the following content:

```bash
BASE_URL_PREFIX=dev/api/v1
DJANGO_SECRET_KEY=django_key
GEMINI_API_KEY=gemini_key
DB_NAME=db_name
DB_USER=db_user
DB_PASSWORD=db_password
DB_HOST=db_host
DB_PORT=db_port
```

In order to generate static files:

```bash
python manage.py collectstatic
```

In order to generate the database:

```bash
python manage.py migrate
```

Later on, you can also create a superuser, but this is not supported now:

```bash
python manage.py createsuperuser
```

In order to run the server:

```bash
python manage.py runserver
```
