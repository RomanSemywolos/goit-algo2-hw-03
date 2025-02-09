from collections import deque, defaultdict

# Алгоритм Едмондса–Карпа

def edmonds_karp(graph, source, sink):
    """
    Обчислює максимальний потік у мережі за алгоритмом Едмондса–Карпа.

    Аргументи:
        graph  - орієнтований граф, представлений як словник, 
                            де для кожного ребра graph[u][v] вказано ємність ребра від u до v.
        source - вузол-джерело.
        sink   - вузол-сток.
    
    Повертає:
        (max_flow, flow) - кортеж, де max_flow – значення максимального потоку,
                           flow – словник з потоками на ребрах, який показує, скільки потоку пройшло від u до v.
    """
    # Ініціалізація структури для зберігання потоків: за умовчанням для кожного ребра значення 0.
    flow = defaultdict(lambda: defaultdict(int))
    
    # Створення копії графа для роботи із залишковими ємностями.
    # Використовуємо просте копіювання вкладених словників.
    residual = {u: dict(graph[u]) for u in graph}
    
    # Додаємо зворотні ребра з початковою ємністю 0, якщо вони відсутні.
    for u in list(graph.keys()):
        for v in graph[u]:
            if v not in residual:
                residual[v] = {}
            if u not in residual[v]:
                residual[v][u] = 0

    max_flow = 0
    while True:
        # Пошук збільшувального шляху (augmenting path) від source до sink за допомогою BFS.
        parent = {node: None for node in residual}
        parent[source] = source  # Позначаємо початковий вузол
        queue = deque([source])
        
        # Знаходимо шлях, де на кожному ребрі залишкова ємність > 0.
        while queue and parent[sink] is None:
            current = queue.popleft()
            for neighbor, capacity in residual[current].items():
                if capacity > 0 and parent[neighbor] is None:
                    parent[neighbor] = current
                    queue.append(neighbor)
                    if neighbor == sink:
                        break  # Якщо досягли стоку, можна завершити пошук.
        
        # Якщо шлях не знайдено – виходимо з циклу.
        if parent[sink] is None:
            break
        
        # Визначаємо мінімальну залишкову ємність (бутилькове горлечко) уздовж знайденого шляху.
        path_flow = float('inf')
        node = sink
        while node != source:
            prev = parent[node]
            path_flow = min(path_flow, residual[prev][node])
            node = prev
        
        # Оновлюємо потоки та залишкові ємності вздовж знайденого шляху.
        node = sink
        while node != source:
            prev = parent[node]
            flow[prev][node] += path_flow
            flow[node][prev] -= path_flow  # Оновлюємо зворотний потік.
            residual[prev][node] -= path_flow
            residual[node][prev] += path_flow
            node = prev
        
        max_flow += path_flow

    return max_flow, flow


# Граф логістичної мережі


def build_logistics_graph():
    """
    Граф логістичної мережі
    
    Структура:
        S (суперджерело) → [Термінали] → [Склади] → [Магазини] → T (супертин)

    Повертає:
        graph      - граф (словник з ребрами та їх ємностями),
        S          - вузол-суперджерело,
        T          - вузол-супертин,
        terminals  - список терміналів,
        warehouses - список складів,
        shops      - список магазинів.
    """
    graph = defaultdict(dict)
    
    # Визначення вузлів мережі
    terminals = ["Terminal 1", "Terminal 2"]
    warehouses = ["Warehouse 1", "Warehouse 2", "Warehouse 3", "Warehouse 4"]
    shops = [f"Shop {i}" for i in range(1, 15)]
    
    # Встановлюємо суперджерело та супертин
    S, T = "S", "T"
    
    # Ребра від суперджерела S до терміналів.
    graph[S]["Terminal 1"] = 25 + 20 + 15   # 60
    graph[S]["Terminal 2"] = 15 + 30 + 10   # 55
    
    # Ребра від терміналів до складів.
    graph["Terminal 1"]["Warehouse 1"] = 25
    graph["Terminal 1"]["Warehouse 2"] = 20
    graph["Terminal 1"]["Warehouse 3"] = 15

    graph["Terminal 2"]["Warehouse 3"] = 15
    graph["Terminal 2"]["Warehouse 4"] = 30
    graph["Terminal 2"]["Warehouse 2"] = 10
    
    # Ребра від складів до магазинів.
    # Для Warehouse 1:
    graph["Warehouse 1"]["Shop 1"] = 15
    graph["Warehouse 1"]["Shop 2"] = 10
    graph["Warehouse 1"]["Shop 3"] = 20
    # Для Warehouse 2:
    graph["Warehouse 2"]["Shop 4"] = 15
    graph["Warehouse 2"]["Shop 5"] = 10
    graph["Warehouse 2"]["Shop 6"] = 25
    # Для Warehouse 3:
    graph["Warehouse 3"]["Shop 7"] = 20
    graph["Warehouse 3"]["Shop 8"] = 15
    graph["Warehouse 3"]["Shop 9"] = 10
    # Для Warehouse 4:
    graph["Warehouse 4"]["Shop 10"] = 20
    graph["Warehouse 4"]["Shop 11"] = 10
    graph["Warehouse 4"]["Shop 12"] = 15
    graph["Warehouse 4"]["Shop 13"] = 5
    graph["Warehouse 4"]["Shop 14"] = 10
    
    # Ребра від магазинів до супертину T.
    # Встановлюємо дуже високу ємність, щоб ці ребра не обмежували потік.
    INF = 10 ** 9
    for shop in shops:
        graph[shop][T] = INF

    return graph, S, T, terminals, warehouses, shops


# Декомпозиція потоку від терміналів до магазинів


def decompose_terminal_flows(terminal, flow, terminals, warehouses, shops):
    """
    Декомпонує потік, що виходить із заданого терміналу, для визначення розподілу товарів по магазинах.

    Аргументи:
        terminal - назва терміналу (наприклад, "Terminal 1").
        flow     - словник, отриманий після виконання алгоритму Едмондса–Карпа, що містить значення потоку.
        terminals, warehouses, shops - списки назв відповідних вузлів.
    
    Повертає:
        Словник, де ключ – назва магазину, а значення – обсяг потоку, що надійшов з даного терміналу.
    """
    # Формуємо підграф потоку, враховуючи лише вузли, що належать до мережі (термінали, склади, магазини)
    valid_nodes = set(terminals) | set(warehouses) | set(shops)
    sub_flow = defaultdict(dict)
    for u in flow:
        if u in valid_nodes:
            for v, f in flow[u].items():
                if v in valid_nodes and f > 0:
                    sub_flow[u][v] = f

    # Рекурсивна функція DFS для пошуку шляху від поточного вузла до будь-якого магазину
    def dfs(node, visited):
        if node in shops:
            return [node], float('inf')
        visited.add(node)
        if node in sub_flow:
            for neighbor, capacity in sub_flow[node].items():
                if capacity > 0 and neighbor not in visited:
                    path, bottleneck = dfs(neighbor, visited)
                    if path is not None:
                        return [node] + path, min(capacity, bottleneck)
        return None, 0

    result = defaultdict(int)
    # Знаходимо усі можливі шляхи від заданого терміналу до магазинів
    while True:
        visited = set()
        path, bottleneck = dfs(terminal, visited)
        if path is None or bottleneck == 0:
            break
        # Останній вузол у знайденому шляху – це магазин
        shop = path[-1]
        result[shop] += bottleneck
        # Віднімаємо знайдений обсяг потоку з усіх ребер на шляху
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            sub_flow[u][v] -= bottleneck
        # Продовжуємо пошук додаткових шляхів
    return dict(result)


# Головна функція


# побудова графа, розрахунок максимального потоку та аналіз результатів
def main():
    # Побудова графа логістичної мережі
    graph, S, T, terminals, warehouses, shops = build_logistics_graph()

    # Обчислення максимального потоку від S до T
    max_flow, flow = edmonds_karp(graph, S, T)
    print("=== Результат роботи алгоритму Едмондса–Карпа ===")
    print("Максимальний потік (від S до T):", max_flow)
    print()

    # Декомпозиція потоку для кожного терміналу (ігноруючи суперджерело S та супертин T)
    terminal_to_shop_flow = {}
    for term in terminals:
        terminal_to_shop_flow[term] = decompose_terminal_flows(term, flow, terminals, warehouses, shops)


    # Формування таблиці
        

    # Термінал – Магазин – Потік
    print("Потік від терміналів до магазинів")
    print("{:<12} {:<12} {:<20}".format("Термінал", "Магазин", "Фактичний Потік (одиниць)"))
    for term in terminals:
        for shop, amount in terminal_to_shop_flow[term].items():
            print("{:<12} {:<12} {:<20}".format(term, shop, amount))
    print()


    # Аналіз отриманих результатів


    # 1. Обчислюємо сумарний потік від кожного терміналу
    terminal_totals = {term: sum(terminal_to_shop_flow[term].values()) for term in terminals}
    print("Сумарний потік за терміналами:")
    for term, total in terminal_totals.items():
        print("  {}: {} одиниць".format(term, total))
    print()

    # 2. Обчислюємо сумарний потік до кожного магазину (від усіх терміналів)
    shop_totals = defaultdict(int)
    for shop_flow in terminal_to_shop_flow.values():
        for shop, amount in shop_flow.items():
            shop_totals[shop] += amount
    print("Сумарний потік до магазинів:")
    for shop in sorted(shop_totals.keys(), key=lambda x: int(x.split()[1])):
        print("  {}: {} одиниць".format(shop, shop_totals[shop]))
    print()

    # 3. Аналіз вузьких місць: приклади маршрутів з малою ємністю
    print("Приклади маршрутів з низькою пропускною здатністю (потенційні вузькі місця):")
    print("  Warehouse 4 -> Shop 13: 5 одиниць")
    print("  Warehouse 1 -> Shop 2: 10 одиниць")
    print()

    # 4. Відповіді на запитання:

    print("Аналіз")
    # 4.1 Які термінали забезпечують найбільший потік товарів до магазинів?
    if terminal_totals["Terminal 1"] > terminal_totals["Terminal 2"]:
        best_terminal = "Terminal 1"
    elif terminal_totals["Terminal 1"] < terminal_totals["Terminal 2"]:
        best_terminal = "Terminal 2"
    else:
        best_terminal = "Обидва термінали мають однаковий потік"
    print("Термінал з найбільшим потоком:", best_terminal)

    # 4.2 Які маршрути мають найменшу пропускну здатність і як це впливає на загальний потік?
    print("Маршрут Warehouse 4 -> Shop 13 має ємність 5 одиниць, що може обмежувати доставку товарів до цього магазину і впливати на загальний потік.")

    # 4.3 Які магазини отримали найменше товарів і чи можна збільшити їх постачання, збільшивши пропускну здатність певних маршрутів?
    min_shop = min(shop_totals, key=shop_totals.get)
    print("Магазин з найменшим потоком:", min_shop, "– отримав", shop_totals[min_shop], "одиниць.")
    print("Для збільшення постачання можна розглянути підвищення ємності відповідних маршрутів.")

    # 4.4 Чи є вузькі місця, які можна усунути для покращення ефективності логістичної мережі?
    print("Аналіз показує, що деякі ребра, наприклад, Warehouse 4 -> Shop 13, є вузькими місцями.")
    print("Усунення або збільшення їх ємності може покращити загальну ефективність логістичної мережі.")

if __name__ == "__main__":
    main()