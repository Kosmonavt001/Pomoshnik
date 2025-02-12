import serial
import time

# Настройка COM-порта
COM_PORT = "COM3"
BAUD_RATE = 115200

def init_serial():
    try:
        ser = serial.Serial(
            port=COM_PORT,
            baudrate=BAUD_RATE,
            timeout=1,
            write_timeout=1
        )
        print("COM-порт успешно открыт")
        return ser
    except serial.SerialException as e:
        print(f"Ошибка открытия COM-порта: {e}")
        return None

def send_command(ser, board: int, output: int) -> bool:
    try:
        command = f"{board}:{output:02d}\r\n".encode('ascii')
        ser.write(command)
        ser.flush()
        print(f"Отправлено: {board}:{output:02d}")
        return True
    except serial.SerialException as e:
        print(f"Ошибка отправки команды: {e}")
        return False

def main_loop():
    ser = init_serial()
    if not ser:
        return

    try:
        while True:
            user_input = input("Введите '1' для команды на плату 10 вход 0, '2' для платы 4 вход 9 или 'exit' для выхода: ")
            if user_input == '1':
                # Команда на плату 10, вход 0
                send_command(ser, 10, 0)
            elif user_input == '2':
                # Команда на плату 4, вход 9
                send_command(ser, 11, 9)
            elif user_input.lower() == 'exit':
                break
            else:
                print("Неверный ввод, попробуйте еще раз.")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Работа прервана пользователем")
    finally:
        ser.close()
        print("COM-порт закрыт.")

if __name__ == "__main__":
    main_loop()
