import os
import json
import re
import random
import xml.etree.ElementTree as et
import requests as rq
import logging
from xeger import Xeger


# **Настройка логирования**
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# **Класс для генерации марок**
class MarksGenerator(list):
    def __init__(
        self, product_code: int, mark_type: int | None = None, amount: int = 1
    ):
        self.marks = None
        assert isinstance(product_code, int | str) and len(str(product_code)) == 3
        assert isinstance(mark_type, int) and mark_type in [150]
        assert isinstance(amount, int) and amount > 0

        super().__init__(self.create_marks(product_code, mark_type, amount))

    def __validate_mark147__(self, product_code):
        pattern = (
            r"([1-9]\d{2}|\d([1-9]\d|\d[1-9])){2}([1-9]\d{7}|\d([1-9]\d{6}|\d([1-9]\d{5}|\d([1-9]\d{4}|\d(["
            r"1-9]\d{3}|\d([1-9]\d{2}|\d([1-9]\d|\d[1-9])))))))(0[1-9]|1[0-2])(1[8-9]|[2-9][0-9])([1-9]\d{"
            r"2}|\d([1-9]\d|\d[1-9]))[0-9A-Z]{129}|\d\d[a-zA-Z0-9]{21}\d[0-1]\d[0-3]\d{10}[a-zA-Z0-9]{31}|["
            r"0-9]{40}"
        )

        mark = f"{product_code}{self.mark147()}"
        while not re.match(pattern, mark):
            logging.warning(f"Не валидная марка: {mark}")
            mark = f"{product_code}{self.mark147()}"

        return mark

    def mark147(self):
        xeger = Xeger()
        number = xeger.xeger(r"\d{8}")
        ser = xeger.xeger(r"\d{3}")
        sign = xeger.xeger(
            r"(0[1-9]|1[0-2])(1[8-9]|[2-9][0-9])([1-9]\d{2}|\d([1-9]\d|\d[1-9]))[0-9A-Z]{100}[0-9A-Z]{29}"
        ).upper()
        return f"{ser}{number}{sign}"

    def create_marks(
        self, product_code: int, mark_type: int = None, amount: int = 1
    ) -> list:
        match mark_type:
            case 150:
                self.marks = [
                    f"{self.__validate_mark147__(product_code)}" for _ in range(amount)
                ]
                return self.marks
            case _:
                raise NotImplementedError()

    def export(self):
        os.makedirs("./_output/marks/", exist_ok=True)
        with open("./_output/marks/marks.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(self.marks, ensure_ascii=False, indent=2))

        # Выводим сгенерированные марки в терминал
        for mark in self.marks:
            logging.info(mark)


# **Функция для генерации случайных значений**
def generate_random_bottles(count):
    bottles = []
    for _ in range(count):
        barcode = MarksGenerator(123, 150, 1)[0]  # Генерация уникального баркода
        price = round(random.uniform(1.00, 1000.00), 2)  # Случайная цена
        volume = round(random.uniform(0.1000, 2.0000), 4)  # Случайный объем
        bottles.append(
            f'<ns3:Bottle barcode="{barcode}" price="{price}" volume="{volume}"/>'
        )
    return bottles


# **Функция для обновления XML файла с баркодами**
def update_xml_with_bottles():
    bottle_count = random.randint(1, 30)  # Случайное количество бутылок от 1 до 30
    bottles = generate_random_bottles(bottle_count)
    bottles_xml = "\n".join(bottles)

    xml_content = f"""<ns2:Documents Version="1.0" xsi:schemaLocation="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://fsrar.ru/WEGAIS/WB_DOC_SINGLE_01" xmlns:ns3="http://fsrar.ru/WEGAIS/Cheque" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <ns2:Owner>
        <ns2:FSRAR_ID><ваш_FSRAR_ID></ns2:FSRAR_ID>
    </ns2:Owner>
    <ns2:Document>
        <ns2:ChequeOnLine address="<ваш_адрес>" datetime="<ваша_дата>" inn="<ваш_INN>" kassa="<ваш_kassa>" kpp="<ваш_KPP>" name="<ваше_имя>" number="<ваш_номер>" shift="<ваш_shift>" uuid="<ваш_UUID>">
            {bottles_xml}
        </ns2:ChequeOnLine>
    </ns2:Document>
</ns2:Documents>"""

    # Сохранение обновленного XML в файл
    with open("Check.xml", "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_content)
    logging.info("XML файл обновлен с новыми баркодами.")


# **Основная логика программы**
if __name__ == "__main__":
    product_code = 123
    mark_type = 150

    # Генерация марок
    generator = MarksGenerator(product_code, mark_type)
    generator.export()

    # Обновление XML файла с несколькими бутылками
    update_xml_with_bottles()

    # Вывод содержимого файла Check.xml
    with open("Check.xml", "r", encoding="utf-8") as xml_file:
        logging.info("Содержимое файла Check.xml:")
        logging.info(xml_file.read())

    # **Отправка XML файла на сервер**
    logging.info("Отправка XML файла на сервер...")
    netty = "http://<ваш_сервер>:<порт>/wb"

    # Чтение XML файла
    try:
        with open("Check.xml", "r", encoding="utf-8") as xml_file:
            xml_data = xml_file.read()
            xmlfile = {"file": xml_data}
            resp = rq.post(netty, files=xmlfile)
            logging.info("Запрос отправлен успешно.")
    except rq.exceptions.RequestException as e:
        logging.error(f"Ошибка при отправке запроса: {e}")
        exit()

    # Логирование статуса ответа
    logging.info(f"Код статуса ответа: {resp.status_code}")

    # Обработка ответа
    if resp.status_code == 200:
        logging.info("Ответ OK")
        try:
            outroot = et.fromstring(resp.text)
            btls = outroot.findall("{http://fsrar.ru/WEGAIS/Cheque}Bottle")
            for bo in btls:
                logging.info(
                    f'Bottle: {bo.attrib["barcode"]} - {bo.find("{http://fsrar.ru/WEGAIS/Cheque}Form2").text}'
                )
        except et.ParseError as e:
            logging.error(f"Ошибка при разборе ответа XML: {e}")
    else:
        logging.error(f"Ошибка: {resp.status_code}")
        logging.info(f"Текст ответа: {resp.text}")
