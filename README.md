# XMLChequeSender


`XMLChequeSender` — это Python-скрипт для генерации случайных документов ChequeOnline и их отправки по HTTP. Скрипт создает XML-документы с уникальными баркодами и отправляет их на указанный сервер.


## Установка


1. Убедитесь, что у вас установлен Python 3.6 или выше.

2. Установите необходимые библиотеки, выполнив команду:


   ```bash

   pip install requests xeger

Использование

   Скачайте или клонируйте этот репозиторий:

    git clone https://github.com/AlexCompDev/xml_cheque_sender.git

    cd xml_cheque_sender

Откройте файл и замените все заглушки в XML-документе на ваши реальные данные:

    <ваш_FSRAR_ID>: Укажите ваш FSRAR ID.
    <ваш_адрес>: Укажите адрес, связанный с чеком.
    <ваша_дата>: Укажите дату в формате YYYY-MM-DD или другой подходящий формат.
    <ваш_INN>: Укажите ваш ИНН.
    <ваш_kassa>: Укажите номер вашей кассы.
    <ваш_KPP>: Укажите ваш КПП.
    <ваше_имя>: Укажите ваше имя или название организации.
    <ваш_номер>: Укажите номер чека.
    <ваш_shift>: Укажите номер смены.
    <ваш_UUID>: Укажите уникальный идентификатор для чека.
    http://<ваш_сервер>:<порт>/wb: Укажите URL вашего сервера и порт, на который будет отправляться запрос.

Запустите скрипт:

    python xml_cheque_sender.py

Примечания

    Скрипт генерирует случайные баркоды и сохраняет их в файл marks.txt в директории _output/marks/.
    Сгенерированный XML-документ будет сохранен в файл Check.xml.
    Скрипт отправляет запрос на указанный сервер и логирует статус ответа.

Логирование

Логи будут выводиться в консоль и содержать информацию о процессе генерации марок, обновлении XML файла и отправке запроса.
