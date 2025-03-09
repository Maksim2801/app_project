import logging
import os

def setup_logging():
    logger = logging.getLogger("delivery_service")
    logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Создаем обработчик для записи в файл
    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/delivery_service.log")
    file_handler.setLevel(logging.INFO)

    # Формат логов
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger