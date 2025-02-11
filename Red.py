import requests
import time
import configparser
import serial
import logging

# Настройка логгера
logging.basicConfig(
    filename='postamat.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Инициализация COM-порта
def init_serial():
    try:
        ser = serial.Serial(
            port="COM3",
            baudrate=115200,
            timeout=1,
            write_timeout=1
        )
        logging.info("COM-порт успешно открыт")
        return ser
    except serial.SerialException as e:
        logging.error(f"Ошибка открытия COM-порта: {e}")
        return None

# Отправка команды на открытие ячейки
def send_command(ser, board: int, output: int) -> bool:
    try:
        command = f"{board}:{output:02d}\r\n".encode('ascii')
        ser.write(command)
        ser.flush()
        return True
    except serial.SerialException as e:
        logging.error(f"Ошибка отправки команды: {e}")
        return False

# Основной цикл
def main_loop():
    ser = init_serial()
    if not ser:
        return

    api_url = "https://пост-автоматика.рф/api/postomat/Get.php"
    request_payload = {"postomat_id": "1000000001"}

    try:
        while True:
            # Запрос к API
            try:
                response = requests.post(
                    api_url,
                    json=request_payload,
                    timeout=2
                )
                response.raise_for_status()
                
                if response.status_code == 200:
                    data = response.json()
                    if 'cell_code' in data:
                        cell_code = data['cell_code']
                        if 10 <= cell_code <= 209:
                            board = cell_code // 10
                            output = cell_code % 10
                            
                            # Отправка команды
                            if send_command(ser, board, output):
                                logging.info(f"Команда отправлена: {board}:{output:02d}")
                                print(f"Отправлено: {board}:{output:02d}")

            except requests.exceptions.RequestException as e:
                logging.warning(f"Ошибка запроса: {e}")
                time.sleep(1)
                continue

            # Постоянный опрос порта
            try:
                while ser.in_waiting > 0:
                    response = ser.readline().decode('ascii', errors='ignore').strip()
                    if response:
                        logging.info(f"Ответ устройства: {response}")
                        print(f"Ответ: {response}")
            except serial.SerialException as e:
                logging.error(f"Ошибка чтения: {e}")

            time.sleep(0.1)  # Короткая пауза для снижения нагрузки на CPU

    except KeyboardInterrupt:
        logging.info("Работа прервана пользователем")
    finally:
        ser.close()
        logging.info("COM-порт закрыт")

if __name__ == "__main__":
    main_loop()
