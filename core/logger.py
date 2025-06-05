import logging
from datetime import datetime
from colorama import init as colorama_init, Fore, Style
import os
import atexit
import traceback
from pathlib import Path


class Log:
    def __init__(self, PROJECT_ROOT: Path, class_name: str):
        """
        Инициализация логгера: создаёт сессионный лог и основной лог-файл,
        подключает обработчики, настраивает цветной вывод в консоль.
        """
        colorama_init(autoreset=True)

        self.PROJECT_ROOT = PROJECT_ROOT

        log_dir = self.PROJECT_ROOT / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        self.session_starttime = datetime.now()
        session_name = f'{class_name.lower()}_session_{self.session_starttime.strftime("%Y_%m_%d_%H_%M_%S")}.log'
        log_filename = f'{class_name.lower()}.log'
        self.session_path = log_dir / session_name
        self.log_path = log_dir / log_filename

        self.max_log_size = 5_242_880 # 5MB
        atexit.register(self.__log_finish)

        self.logger = logging.getLogger(session_name)
        self.logger.setLevel(logging.INFO)

        self.file_handler = logging.FileHandler(self.session_path, mode='w', encoding='utf-8')
        self.file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d_%H:%M:%S')
        self.file_handler.setFormatter(formatter)
        
        self.logger.addHandler(self.file_handler)

        self.__start()

    def __start(self) -> None:
        """Создаёт заголовок новой сессии и выводит его в лог и консоль."""
        session_header = f"—————————— NEW SESSION ——————————"
        self.logger.info(session_header)
        self.__console_output(f'{session_header}\n—— [TIME]  {self.session_starttime.strftime("%Y-%m-%d %H:%M:%S")} ——', Fore.LIGHTCYAN_EX)

    def __console_output(self, message, color) -> None:
        """Выводит сообщение в консоль с цветом."""
        print(color + message + Style.RESET_ALL)

    def __log_finish(self) -> None:
        """
        Выполняется при завершении программы:
        объединяет текущий сессионный лог с основным логом и удаляет временный файл.
        """
        try:
            with open(self.session_path, 'r', encoding='utf-8') as session_file:
                session_data = session_file.read()

            log_data = ''
            if self.log_path.exists():
                with open(self.log_path, 'r', encoding='utf-8',  errors='replace') as log_file:
                    log_data = log_file.read()

            log_data = session_data + "\n" * 5 + log_data if log_data else session_data

            with open(self.log_path, 'w', encoding='utf-8') as log_file:
                log_file.write(log_data)
                log_file.truncate(self.max_log_size)

            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)
            os.remove(self.session_path)
        except Exception as e:
            error_message = f"Ошибка при завершении лога: "
            self.log_error(error_message, e)

    def log_message(self, message: str):
        self.logger.info(message)
        self.__console_output(message, Fore.LIGHTYELLOW_EX)

    def log_info(self, message: str):
        self.logger.info(message)
        self.__console_output(message, Fore.LIGHTCYAN_EX)

    def log_warning(self, message: str):
        self.logger.warning(message)
        self.__console_output(message, Fore.LIGHTMAGENTA_EX)

    def log_error(self, message: str, exception=''):
        """
        Логирует ошибку с трейсбеком (если есть), а также выводит в консоль.
        """
        error_message = f"{message}{exception}"
        file_error_message = error_message

        traceback_message = traceback.format_exc()
        if traceback_message != 'NoneType: None\n':
            file_error_message += f"\n\n{'—'*100}\n{traceback_message}{'—'*100}\n"

        self.logger.error(file_error_message)
        self.__console_output(error_message, Fore.LIGHTRED_EX)

    def log_time(self, message: str, start_time=None):
        """
        Логирует прошедшее время с начала сессии или заданного времени.
        """
        start_time = self.session_starttime if start_time == None else start_time
        time_message = f"{message}{datetime.now() - start_time}"
        self.logger.info(time_message)
        self.__console_output(time_message + '\n', Fore.LIGHTCYAN_EX)
