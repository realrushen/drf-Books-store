# Books store
#### _Simple api service, that allow to sell and read books_


This project was developed only for educational purposes 

## Features

- Make CRUD operations on books
- Buy and mark books read
- Like books
- Add books to bookmarks
- Filtering and searching for books

## Installation

To setup development environment you need python 3.8+, [pipenv](https://pipenv.pypa.io/en/latest/) and PostgreSQL 12.6 

- Clone repository and install dependences
```shell script
git clone https://github.com/realrushen/drf-Books-store.git
cd drf-Books-store
pipenv install --dev
```
- Create .env.secrets
```shell script
touch .env.secrets 
```
- Specify environment variables in .env.secrets to configure project

| Variable | Value |
| --- | --- |
|DJANGO_SECRET_KEY|your_secret_key|
|BOOKS_APP_SOCIAL_AUTH_GITHUB_KEY|your_github_key|
|BOOKS_APP_SOCIAL_AUTH_GITHUB_SECRET|your_github_secret|
|POSTGRES_DB_NAME|your_db_name|
|POSTGRES_DB_USER|your_db_user|
|POSTRGES_DB_PASSWORD|your_db_password|
|POSTGRES_DB_HOST|your_db_host|
|POSTGRES_DB_PORT|your_db_port|

- Run tests
```shell script
python3 manage.py test
```
- Apply migrations
```shell script
python3 manage.py makemigrations && python3 manage.py migrate 
```

- Start development server
```shell script
python3 manage.py runserver
```