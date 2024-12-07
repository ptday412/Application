# Quick Start
## 1. Create & activate a virtual environment
Make it in the root path
```
python -m venv .venv
source .venv/Scripts/activate   # Window
```
## 2. install requirements
```
pip install -r requirements.txt
```
## 3. Create environment variable file
Make it in the root path
```
touch .env
```
### - What should be in the file?
```
DEV_SECRET_KEY = 'YOUR_DEV_SECRET_KEY'
LOCAL_SECRET_KEY = 'YOUR_LOCAL_SECRET_KEY'
PROD_SECRET_KEY = 'YOUR_PROD_SECRET_KEY'
```
## 4. makemigrations & migrate
```
python manage.py makemigrations --settings=config.settings.the_execution_environment_you_want
python manage.py migrate --settings=config.settings.the_execution_environment_you_want
```
## 5. runserver
### Run as a production environment for real services
```
python manage.py runserver --settings=config.settings.prod
```
### Run in a development environment
```
python manage.py runserver --settings=config.settings.dev
```
### Run in a local environment
```
python manage.py runserver --settings=config.settings.local
```
### How to automate running environment settings
Enter in terminal
```
set DJANGO_SETTINGS_MODULE=config.settings.the_execution_environment_you_want
python manage.py runserver
```