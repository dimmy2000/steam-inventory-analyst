# Steam Inventory Analyst

---

## Описание

### Проект
Данный проект выполнен в рамках курса Learn Python 20 (весна 2021 г.) и
представляет из себя веб-сайт для визуализации статистики активности пользователя
Steam на торговой площадке сервиса. На текущий момент реализован следующий 
функционал:
- регистрация нового пользователя
- авторизация зарегистрированного пользователя на сайте
- страница профиля авторизованного пользователя с визуализацией подключенных аккаунтов
- страница авторизации аккаунта через сервис Steam с последующей записью ключей
сессии в БД для повторной авторизации без ввода пользовательских данных
- страница подключенного аккаунта с визуализацией предметов в инвентаре
- страница отдельного предмета
- всплывающее уведомление с предложением повторной авторизации в случае
истечения сессии подключенного аккаунта.

### Стек технологий
Веб-приложение построено на базе Flask, для авторизации пользователя используется
Flask-Login, аватар пользователя подключен к сервису Gravatar от Wordpress и 
привязан к адресу электронной почты. Если пользователь не загружал свой 
аватар - сервис генерирует уникальное изображение.

Взаимодействие с сервисом Steam осуществляется при помощи библиотеки
Steam от ValvePython. Обрабатываемая информация хранится в базе
данных SQLite. Запросы в БД генерирует SQLAlchemy, для сериализации данных
из БД взят Marshmallow. Интеграцию этих пакетов с Flask обеспечивают
Flask-SQLAlchemy и Flask-Marshmallow. За миграции БД отвечает Flask-Migrate.
Чтобы уменьшить время отклика сайта, операции записи в БД производятся
асинхронно с помощью Celery tasks и Redis. Для отслеживания работы задач
Celery использeтся Flower.

### Дополнительная информация:
* [Диаграмма последовательности работы приложения](docs/images/sequence_diagram.png)  
* [Диаграмма отношений базы данных](docs/images/db_relationship_diagram.png) 

---

### Установка

Выполните в консоли следующие команды:
```
git clone https://github.com/dimmy2000/steam-inventory-analyst.git
cd steam-inventory-analyst/
```
Создайте виртуальное окружение:

<table>
    <tr>
        <th>MacOS/Linux</th>
        <th>Windows</th>
    </tr>
    <tr>
        <td><code>python3 -m venv venv</code></td>
        <td><code>py -3 -m venv venv</code></td>
    </tr>
</table>

Активируйте виртуальное окружение и установите пакеты, необходимые для работы приложения:

<table>
    <tr>
        <th>MacOS/Linux</th>
        <th>Windows</th>
    </tr>
    <tr>
        <td>
            <code>source venv/bin/activate</code><br>
            <code>pip install -r requirments.txt</code>
        </td>
        <td>
            <code>venv\Scripts\activate.bat</code><br>
            <code>pip install -r requirments.txt</code>
        </td>
    </tr>
</table>

Также, в качестве брокера задач Celery, необходимо установить Redis

<table>
    <tr>
        <th>Linux</th>
        <th>MacOS</th>
        <th>Windows</th>
    </tr>
    <tr>
        <td width="30%">
            <span>
                Установите пакет redis-server<br>
                <code>apt-get install redis-server</code>
            </span>
        </td>
        <td width="30%"><span>
            Установите redis при помощи 
            <a href="https://brew.sh/index_ru" target="_blank">homebrew</a>
            (<a href="https://medium.com/@djamaldg/install-use-redis-on-macos-sierra-432ab426640e" target="_blank">инструкция</a>)
        </span></td>
        <td width="40%"><span>
            Для Windows лучше всего установить 
            <a href="https://www.comss.ru/page.php?id=4897" target="_blank">Linux-подсистему для Windows</a>
            и продолжать работу в ней. Если вы не можете установить WSL, то можно воспользоваться
            <a href="https://github.com/MicrosoftArchive/redis/releases" target="_blank">старой сборкой Redis</a>
        </span></td>
    </tr>
</table>

### Настройка
Настройки по умолчанию хранятся в файле `./webapp/config.py`. Если требуется внести изменения в секретные
ключи - создайте файл .env и добавьте туда следующие настройки:
```
SECRET_KEY=ваш секретный ключ для создания сессий Flask 
LOG_TYPE=полный или сокращенный формат сообщений ('stream'/'watched')
LOG_LEVEL=уровень сообщений для записи в журнал
LOG_DIR=путь к папке с файлами логов
APP_LOG_NAME=имя файла 'stream'-логов
WWW_LOG_NAME=имя файла 'watched'-логов
```

#### Миграция базы данных
Чтобы создать новую базу данных или применить миграции к существующей,
выполните в командной строке `export FLASK_APP=webapp.factory:create_app &&
flask db upgrade`

### Запуск
Чтобы запустить приложение на локальном сервере, выполните в консоли:
#### MacOS/Linux
```
./runserver.sh
```

Теперь вы можете работать с сервисом по адресу [http://localhost:5000](http://localhost:5000) и отслеживать статистику
выполнения задач Celery по адресу [http://localhost:5555](http://localhost:5555)