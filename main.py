import time
import threading
from config import token
from bot import create_telebot_task, create_storage_handler_task
from service import Service


def main():
    storage = []
    service = Service()

    telebot_task = create_telebot_task(token, service, storage)
    storage_handler_task = create_storage_handler_task(token, service, storage)

    telebot_thread = threading.Thread(target=telebot_task.run, daemon=True)
    storage_handler_thread = threading.Thread(target=storage_handler_task.run)

    telebot_thread.start()
    storage_handler_thread.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        storage_handler_task.terminate()
        print("Application terminated")


if __name__ == "__main__":
    main()
