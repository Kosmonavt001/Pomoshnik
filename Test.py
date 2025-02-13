import requests
import time
from pymodbus.client import ModbusSerialClient
import threading

def send_post_request():
    url = "https://пост-автоматика.рф/api/postomat/ApiGetInfo.php" 
    data = {"postomat_id": 1000000001}
    response = requests.post(url, json=data)
    return response.text

def control_door(client, board, input, value):
    address = input 
    client.write_register(address, value, unit=board)

def handle_connection():
    client = ModbusSerialClient(port='COM3', baudrate=115200, timeout=1)
    if not client.connect():
        print("Ошибка подключения к Modbus-клиенту.")
        return
    while True:
        response = send_post_request()
        print(f"Ответ от сервера: {response}")
        try:
            response_number = int(response)
            board = response_number // 10
            input = response_number % 10
            control_door(client, board, input, 1)
            print(f"Дверца открыта на плате {board}, вход {input}.")
            url = "https://пост-автоматика.рф/api/postomat/postomat/CloseAPI.php" 
            data = {"id_towar": str(response_number)}
            requests.post(url, json=data)
            time.sleep(180)
            control_door(client, board, input, 0)
            print(f"Дверца закрыта на плате {board}, вход {input}.")
        except ValueError:
            print("Ошибка обработки ответа от сервера. Не удалось преобразовать в число.")
        time.sleep(10)

def main():
    threads = []
    for _ in range(2): 
        thread = threading.Thread(target=handle_connection)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
