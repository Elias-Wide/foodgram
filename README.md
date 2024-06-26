# Foodrgam 
[![Python](https://img.shields.io/badge/Python-3776AB?style=plastic&logo=python&logoColor=092E20&labelColor=white
)](https://www.python.org/) [![Django](https://img.shields.io/badge/django-822e0d?style=plastic&logo=django&logoColor=092E20&labelColor=white
)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django_REST_framework-DC143C?style=red
)](https://www.django-rest-framework.org/)

Дипломный проект Яндекс.Практикума, направление - Python backend-разработка.

 «Фудграм» — сайт, на котором пользователи моугт публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволяетт создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Стэк используемых технологий
- Django
- DjangoRestFramework
- Docker
- Nginx
- Postgres 

## Особенности проекта
- Проект "упакован" в Docker-контейнеры
- Скрипт загрузки образов с Docker Gub описан в файле 'docker-compose.production.yml'
- Реализован workflow - автоматическое тестирование на соответствие PEP8, автоматический деплой на удаленный сервер и отправка сообщения в Телеграмм в случае успешного запуска проекта.

## Запуск проекта локально
### 1. Скачать данный репозиторий
```
git clone https://github.com/Elias-Wide/foodgram.git
```
В основной директории проекта необходимо создать файл .env с данными
```
POSTGRES_USER      #имя пользователя в БД PostgreSQL
POSTGRES_PASSWORD  #пароль пользователя в БД PostgreSQL
POSTGRES_DB        #имя БД
DB_HOST            #имя контейнера, где запущен сервер БД
DB_PORT            #порт, по которому Django будет обращаться к серверу с БД 

SECRET_KEY         #ваш секретный код из settings.py для Джанго проекта
DEBUG              #статус режима отладки (default=False)
ALLOWED_HOSTS      #список доступных хостов
```

### 2. Запустить Docker engine
### В основной директории проекта, где лежит файл docker-compose.yml, выполнить команды:
```
docker compose up -build
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py import_csv
```
Последняя команда загружает в бд подготовленный набор необходимых данных(ингредиенты и тэги)
Дополнительно можно создать суперпользователя, для доступа к админ-панели сайта, командой:
```
docker compose exec backend python manage.py createsuperuser
```
После Foodgram станет доступен по адресу http://localhost 
Список доступных API-эндпоинтов доступен по ссылке http://localhost/api/redoc/

### Автор проекта
**Широков Илья** 