# Запуск приложения

Клонируем репозиторий:

`git clone https://github.com/k1cker666/pavepo_test.git`

Заходим в корень проекта и запускаем через docker-compose:

`docker-compose up -d`

Файл .env уже есть в проекте, поэтому создавать не нужно

# Использование
- Заходим в документацию http://localhost/docs/ и используем эндпоинт /admin/create_tables

Эндпоинт удаляет и создает таблицы в бд, реализован для удобства
- Чтобы авторизоваться через яндекс переходим по адресу http://localhost/auth/yandex
- Далее возвращаемся в документацию и создаем данные для входа через эндпоинт /auth/set_credentials
- Логинимся в документации через Authorize и можем тестировать /users/ и /audio/
- Чтобы сделать текущего пользователя админом используем эндпоинт /admin/make_admin/
- После этого использование /admin/delete_user/ станет доступен
