Развертывание проекта

Развертывание на локальном сервере

Установите на сервере docker и docker-compose.
Создайте файл .env. Шаблон для заполнения файла нахоится в /infra/.env.example.
Выполните команду docker-compose up -d --buld.
Выполните миграции docker-compose exec backend python manage.py migrate.
Создайте суперюзера docker-compose exec backend python manage.py createsuperuser.
Соберите статику docker-compose exec backend python manage.py collectstatic --noinput.
Зайдите в admin панель и создайте в базе данных как минимум 2 ингредиента и 3 тега.
