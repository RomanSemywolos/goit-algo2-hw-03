import csv
import timeit
from BTrees.OOBTree import OOBTree


def load_items_from_csv(filename):
    """
    Завантаження інформації про товари з файлу generated_items_data.csv.
    Кожен товар включає:
      - унікальний ідентифікатор (ID)
      - назву (Name)
      - категорію (Category)
      - ціну (Price)
    
    Після завантаження значення ціни перетворюються на float для подальшої роботи.
    """
    items = []
    try:
        with open(filename, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    row["Price"] = float(row["Price"])
                except (ValueError, KeyError):
                    continue  # Пропускаємо записи з некоректним значенням Price
                items.append(row)
    except FileNotFoundError:
        print(f"Файл '{filename}' не знайдено.")
    return items


def add_item_to_tree(tree, item):
    """
    Додавання товару до структури OOBTree.
    
    Реалізуйтємо функцію add_item_to_tree,
    де ключем є Price, а значенням – список словників з атрибутами товару.
    """
    price = item.get("Price")
    if price is None:
        return
    if price in tree:
        tree[price].append(item)
    else:
        tree[price] = [item]


def add_item_to_dict(dict_data, item):
    """
    Додавання товару до стандартного словника dict.
    Ключем є ID товару, а значенням – словник з атрибутами товару.
    """
    item_id = item.get("ID")
    if item_id is None:
        return
    dict_data[item_id] = item


def range_query_tree(tree, min_price, max_price):
    """
    Виконання діапазонного запиту по структурі OOBTree.
    Завдання: знайти всі товари, чия ціна (Price) належить діапазону [min_price, max_price].
    Для цього використовується метод items(min, max), що забезпечує швидкий доступ до відсортованих даних.
    """
    results = []
    for price, items in tree.items(min_price, max_price):
        if min_price <= price <= max_price:
            results.extend(items)
    return results


def range_query_dict(dict_data, min_price, max_price):
    """
    Виконання діапазонного запиту по словнику dict.
    Завдання: знайти всі товари, чия ціна (Price) належить діапазону [min_price, max_price].
    Реалізація здійснюється шляхом лінійного перебору всіх товарів.
    """
    results = []
    for item in dict_data.values():
        price = item.get("Price")
        if price is not None and min_price <= price <= max_price:
            results.append(item)
    return results


def run_range_queries_tree(tree, query_range, num_queries=100):
    """
    Вимірювання продуктивності діапазонного запиту по структурі OOBTree.
    
    Технічні умови:
      - Використовується бібліотека timeit для точного вимірювання часу.
      - Діапазонний запит виконується 100 разів.
    """
    start_time = timeit.default_timer()
    for _ in range(num_queries):
        range_query_tree(tree, query_range[0], query_range[1])
    end_time = timeit.default_timer()
    return end_time - start_time


def run_range_queries_dict(dict_data, query_range, num_queries=100):
    """
    Вимірювання продуктивності діапазонного запиту для словника шляхом лінійного перебору всіх товарів.
    
    Технічні умови:
      - Використовується бібліотека timeit для точного вимірювання часу.
      - Діапазонний запит виконується 100 разів.
    """
    start_time = timeit.default_timer()
    for _ in range(num_queries):
        range_query_dict(dict_data, query_range[0], query_range[1])
    end_time = timeit.default_timer()
    return end_time - start_time


def main():
    # Завантаження даних з файлу generated_items_data.csv
    filename = "generated_items_data.csv"
    print("Завантаження даних з файлу generated_items_data.csv...")
    items = load_items_from_csv(filename)
    if not items:
        print("Помилка: дані не завантажено.")
        return
    print("Кількість завантажених товарів:", len(items))

    # Реалізація двох структур для зберігання товарів:
    # 1. OOBTree – ключем є Price (для діапазонного запиту методом items(min, max))
    # 2. dict – ключем є ID
    tree = OOBTree()
    dict_data = {}

    # Додавання товарів до обох структур (функції add_item_to_tree та add_item_to_dict)
    for item in items:
        add_item_to_tree(tree, item)
        add_item_to_dict(dict_data, item)

    # Виконання діапазонного запиту: знайти товари з ціною від 50 до 100
    query_range = (50.0, 100.0)
    results_tree = range_query_tree(tree, query_range[0], query_range[1])
    results_dict = range_query_dict(dict_data, query_range[0], query_range[1])
    print(f"\nКількість товарів у діапазоні цін ({query_range[0]} - {query_range[1]}):")
    print("OOBTree:", len(results_tree))
    print("Dict:   ", len(results_dict))

    # Вимірювання часу виконання 100 діапазонних запитів для кожної структури
    num_queries = 100
    total_time_tree = run_range_queries_tree(tree, query_range, num_queries)
    total_time_dict = run_range_queries_dict(dict_data, query_range, num_queries)

    # Вивід загального часу виконання діапазонного запиту для кожної структури
    print("\nПорівняльний аналіз продуктивності діапазонного запиту")
    OOBTree_time_str = "{:.6f}".format(total_time_tree)
    dict_time_str = "{:.6f}".format(total_time_dict)
    print(f"Total range_query time for OOBTree: {OOBTree_time_str} seconds")
    print(f"Total range_query time for Dict: {dict_time_str} seconds")

    print("\nАналіз:")
    print(" - OOBTree забезпечує швидкий діапазонний доступ через відсортовану структуру та метод items(min, max).")
    print(" - Dict виконує діапазонний запит через лінійний перебір усіх товарів, що має лінійну складність.")
    print(f"Очікується, що {OOBTree_time_str} буде меншим ніж {dict_time_str}")

if __name__ == "__main__":
    main()
