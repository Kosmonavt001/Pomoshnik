import requests
import time
import configparser
import serial
import os
import logging


logging.basicConfig(filename='postamat.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

config = configparser.ConfigParser()
config.read('configuration.bin')
com_port = config.get('DEFAULT', 'com_port')
api_url = "https://пост-автоматика.рф/api/Get.php"
data = {
    "postomat_id":"1000000001"
}
try:
    report_url = "https://пост-автоматика.рф/api/postomat/Reported.php"
except configparser.NoOptionError:
    report_url = None


def open_cell(cell_code):
    try:
        ser = serial.Serial(com_port, 115200, timeout=1)
        board_number = cell_code // 10
        output_number = cell_code % 10
        command = f"{board_number}:{output_number}\r\n".encode('ascii')
        ser.write(command)
        response = ser.readline().decode('ascii', errors='ignore').strip()
        ser.close()
        logging.info(f"Отправлена команда: {command.decode().strip()}, ответ: {response}")
        print(f"Отправлена команда: {command.decode().strip()}, ответ: {response}")
    except serial.SerialException as e:
        logging.error(f"Ошибка COM-порта: {e}")
        print(f"Ошибка COM-порта: {e}")


while True:
    try:
        response = requests.post(api_url, data=data)
        response.raise_for_status()
        data = response.json()

        if 'cell_code' in data:
            cell_code = data['cell_code']
            if 10 <= cell_code <= 209:
                logging.info(f"Получено значение cell_code из API: {cell_code}")
                print(f"Получено значение cell_code из API: {cell_code}")
                open_cell(cell_code)
                if report_url:
                    try:
                        report_data = {"cell_code": cell_code, "status": "opened"}
                        report_response = requests.post(report_url, json=report_data)
                        report_response.raise_for_status()
                        logging.info(f"Отчет об открытии ячейки {cell_code} отправлен.")
                        print(f"Отчет об открытии ячейки {cell_code} отправлен.")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Ошибка отправки отчета: {e}")
                        print(f"Ошибка отправки отчета: {e}")


            else:
                logging.warning(f"Получено некорректное значение cell_code: {cell_code}")
                print(f"Получено некорректное значение cell_code: {cell_code}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка API запроса: {e}")
        print(f"Ошибка API запроса: {e}")
    except (KeyError, ValueError) as e:
        logging.error(f"Ошибка обработки ответа API: {e}")
        print(f"Ошибка обработки ответа API: {e}")

    time.sleep(1)
