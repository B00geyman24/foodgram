Развертывание проекта

Развертывание на локальном сервере

1)Установите на сервере docker и docker-compose.
2)Создайте файл .env. Шаблон для заполнения файла нахоится в /infra/.env.example.
3)Выполните команду docker-compose up -d --buld.
4)Выполните миграции docker-compose exec backend python manage.py migrate.
5)Создайте суперюзера docker-compose exec backend python manage.py createsuperuser.
6)Соберите статику docker-compose exec backend python manage.py collectstatic --noinput.
7)Зайдите в admin панель и создайте в базе данных как минимум 2 ингредиента и 3 тега.
