import serial
import time

# Функция для отправки запроса на плату
def send_request(ser, board, input):
    request = f"{board} {input}\n"  # Формируем запрос
    ser.write(request.encode())  # Отправляем запрос
    print(f"Отправлен запрос на плату {board}, вход {input}")

# Основная функция
def main():
    # Настройка COM-порта
    port = 'COM3'
    baudrate = 115200
    ser = serial.Serial(port, baudrate, timeout=1)
    time.sleep(2)  # Ожидание инициализации порта

    try:
        while True:
            # Выбор платы и входа
            board = input("Введите номер платы (10 или 4): ")
            input_num = input("Введите номер входа (0 для платы 10, 9 для платы 4): ")

            # Проверка корректности ввода
            if board not in ['10', '4']:
                print("Ошибка: Некорректный номер платы. Допустимые значения: 10, 4.")
                continue
            if (board == '10' and input_num != '0') or (board == '4' and input_num != '9'):
                print("Ошибка: Некорректный номер входа для выбранной платы.")
                continue

            # Отправка запроса
            send_request(ser, board, input_num)

            # Пауза перед следующим запросом
            time.sleep(1)

    except KeyboardInterrupt:
        print("Программа завершена.")
    finally:
        ser.close()  # Закрытие COM-порта

if __name__ == "__main__":
    main()
