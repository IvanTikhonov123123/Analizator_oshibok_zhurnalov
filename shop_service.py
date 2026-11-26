import logging
import time
import random
import os
import shutil

# Параметр filemode="w" очищает старый лог-файл при каждом новом запуске программы
logging.basicConfig(
    filename="live_service.log",
    filemode="w",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [ShopService] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)


def check_database_file():
    """Реальная проверка наличия файла базы данных на диске."""
    db_file = "orders_db.json"
    if not os.path.exists(db_file):
        logging.warning(f"Файл локального кэша '{db_file}' не найден. Создаём новый...")
        with open(db_file, "w", encoding="utf-8") as f:
            f.write("{}")
        logging.info(f"Файл '{db_file}' успешно инициализирован.")
    else:
        size = os.path.getsize(db_file)
        logging.info(f"Проверка кэша завершена. Размер файла: {size} байт.")


def process_order(order_id):
    """Имитация обработки заказа с реальными вычислениями и перехватом ошибок."""
    logging.info(f"Начата обработка заказа #{order_id}...")
    # Выбираем случайное количество товаров (0 специально добавлен для вызова ошибки)
    items_count = random.choice([0, 1, 2, 3, 5])
    total_price = random.randint(500, 15000)

    try:
        avg_price = total_price / items_count
        logging.info(
            f"Заказ #{order_id} рассчитан: товаров {items_count}, средняя цена {avg_price:.2f} руб."
        )
    except ZeroDivisionError as e:
        logging.error(
            f"Сбой расчёта заказа #{order_id}: пустая корзина товаров ({type(e).__name__}: {e})"
        )


def check_disk_space():
    """Получение реальных данных о свободном месте на вашем диске."""
    total, used, free = shutil.disk_usage(".")
    free_gb = free // (2**30)
    if free_gb < 15:
        logging.warning(f"Мало свободного места на диске! Осталось всего {free_gb} ГБ.")
    else:
        logging.info(f"Проверка диска: свободно {free_gb} ГБ.")


if __name__ == "__main__":
    print("Запуск фоновой службы интернет-магазина...")
    print("Старый лог очищен. Записываются только события текущего запуска...\n")

    logging.info("=== СЛУЖБА ЗАПУЩЕНА ===")
    check_database_file()
    check_disk_space()

    for i in range(1, 11):
        order_num = 1000 + i
        process_order(order_num)
        print(f"Обработан заказ #{order_num}...")
        time.sleep(0.3)

    logging.info("=== СЛУЖБА ЗАВЕРШИЛА ПЛАНОВЫЙ ЦИКЛ ===")
    print("\nГотово! Теперь откройте 'live_service.log' в программе main.py.")
