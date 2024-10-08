import requests
from bs4 import BeautifulSoup
import json
import csv
from time import sleep
from random import randrange
import os

url = "https://health-diet.ru/table_calorie"

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.7.0.0 Safari/537.36",
}
req = requests.get(url, headers=headers)
src = req.text

with open("index.html", "w", encoding="utf-8") as file:
    file.write(src)

with open("index.html", encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")
all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")

all_categories_dict = {}
for item in all_products_hrefs:
    item_text = item.text
    item_url = "https://health-diet.ru" + item.get("href")
    all_categories_dict[item_text] = item_url

with open("all_categories_dict.json", "w", encoding="utf8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open("all_categories_dict.json", encoding="utf8") as file:
    all_categories = json.load(file)

iterations_count = int(len(all_categories)) - 1

count = 0

print(f"Всего итераций: {iterations_count}")

directort_data = "data"

if not os.path.exists(directort_data):
    os.makedirs(directort_data)

for category_name, category_url in all_categories.items():

    rep = [",", " ", "-", "'"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")

    req = requests.get(category_url, headers=headers)
    src = req.text

    with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open(f"data/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Проверка страницы на пустоту
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # Сборка заголовков таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(
        f"data/{count}_{category_name}.csv",
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow((product, calories, proteins, fats, carbohydrates))

    # Сборка данных продуктов
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    products_info = []

    for item in products_data:
        products_tds = item.find_all("td")

        title = products_tds[0].find("a").text
        calories = products_tds[1].text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        carbohydrates = products_tds[4].text

        products_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates,
            }
        )

        with open(
            f"data/{count}_{category_name}.csv",
            "a",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow((title, calories, proteins, fats, carbohydrates))

    with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(products_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"Итерация {count}. {category_name} записан...")
    iterations_count -= 1

    if iterations_count == 0:
        print(f"Работа завершена")
        break

    print(f"Осталось итерация {iterations_count}")
    sleep(randrange(2, 4))
