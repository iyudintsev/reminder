import time
from telebot import TeleBot
from threading import Lock
from service import Service, ServiceError, State
from datetime import datetime


max_storage_len = 2
reminder_bot = None


def get_reminder_bot(token):
    global reminder_bot
    if reminder_bot is None:
        reminder_bot = TeleBot(token)
    return reminder_bot


class TelebotMessages(object):
    @staticmethod
    def hello():
        return "Hello!\nMessages Format Examples:\n13:45 text\n13-45 another text"

    @staticmethod
    def wrong():
        return "Incorrect message"

    @staticmethod
    def okay():
        return "Okay"

    @staticmethod
    def busy():
        return "I'm so busy. Please try again later."


class TelebotTask(object):
    def __init__(self, bot, service, storage):
        super(TelebotTask, self).__init__()
        self.service = service
        self.bot = bot
        self.bot.message_handler(content_types=["text"])(self.handle_message)
        self.storage = storage
        self.lock = Lock()

    def handle_message(self, message):
        try:
            if message.text == "/start":
                self.bot.send_message(message.chat.id, TelebotMessages.hello())
                return

            time_, text = self.service.parse(message.text)
            data = time_, message.chat.id, text
            if len(self.storage) > max_storage_len:
                self.bot.send_message(message.chat.id, TelebotMessages.busy())
                return

            with self.lock:
                self.storage.append(data)
                self.storage.sort()
            self.bot.send_message(message.chat.id, TelebotMessages.okay())
        except ServiceError:
            self.bot.send_message(message.chat.id, TelebotMessages.wrong())

    def run(self):
        self.bot.polling(none_stop=True)


def create_telebot_task(token: str, service: Service, storage: list) -> TelebotTask:
    bot = get_reminder_bot(token)
    task = TelebotTask(bot, service, storage)
    return task


class StorageHandlerTask(object):
    def __init__(self, bot, service, storage):
        self.lock = Lock()
        self.service = service
        self.storage = storage
        self.bot = bot
        self._running = True

    def run(self):
        while self._running:
            if self.storage:
                with self.lock:
                    now = datetime.now()
                    while self.service.compare_time(self.storage[0][0], now) == State.equal:
                        self.bot.send_message(self.storage[0][1], self.storage[0][2])
                        self.storage.pop(0)
                        if not self.storage:
                            break
                        time.sleep(.1)
                        now = datetime.now()
            time.sleep(10)

    def terminate(self):
        self._running = False


def create_storage_handler_task(token: str, service: Service, storage: list) -> StorageHandlerTask:
    bot = get_reminder_bot(token)
    task = StorageHandlerTask(bot, service, storage)
    return task
