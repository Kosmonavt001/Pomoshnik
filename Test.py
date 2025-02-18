import requests
import time
from pymodbus.client import ModbusSerialClient
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_post_request():
    url = "https://пост-автоматика.рф/api/postomat/ApiGetInfo.php"
    data = {"postomat_id": 1000000001}
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Ошибка при отправке POST-запроса: {e}")
        return None

def control_door(client, board, input, value):
    address = input
    try:
        logging.info(f"Попытка записи {value} в адрес {address} на плате {board}.")
        result = client.write_register(address, value, unit=board)
        if not result.isError():
            logging.info(f"Успешно записано: {value} на адрес {address} на плате {board}.")
        else:
            logging.error(f"Ошибка записи: {result}")
    except Exception as e:
        logging.error(f"Ошибка при управлении дверцей: {e}")

def handle_connection():
    client = ModbusSerialClient(port='COM3', baudrate=115200, timeout=1)
    while True:
        try:
            if not client.connect():
                logging.error("Ошибка подключения к Modbus-клиенту.")
                time.sleep(5)
                continue
            response = send_post_request()
            if response is None or response == 'None':
                logging.warning("Пустой ответ от API. Пропускаем итерацию.")
                client.close()
                time.sleep(10)
                continue
            logging.info(f"Ответ от сервера: {response}")
            try:
                response_number = int(response)
                board = response_number // 10
                input = response_number % 10
                control_door(client, board, input, 1)
                logging.info(f"Дверца открыта на плате {board}, вход {input}.")
                close_url = "https://пост-автоматика.рф/api/postomat/CloseAPI.php"
                data = {"id_towar": str(response_number)}
                requests.post(close_url, json=data, timeout=10)
                time.sleep(180)
                control_door(client, board, input, 0)
                logging.info(f"Дверца закрыта на плате {board}, вход {input}.")
            except ValueError:
                logging.error("Ошибка обработки ответа от сервера. Не удалось преобразовать ответ в число.")
            except Exception as e:
                logging.error(f"Произошла ошибка в блоке управления дверцей: {e}")
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
        finally:
            client.close()
        time.sleep(1)

def main():
    thread = threading.Thread(target=handle_connection)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
