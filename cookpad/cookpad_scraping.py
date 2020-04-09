import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime
import time
from fake_useragent import UserAgent

baseURL = "https://cookpad.com/recipe/"

regex_recipe_id = re.compile(r'レシピID : ([0-9]+)')
regex_published_date = re.compile(r'公開日 : ([0-9]{2}/[0-9]{2}/[0-9]{2})')
regex_updated_date = re.compile(r'更新日 : ([0-9]{2}/[0-9]{2}/[0-9]{2})')


def read_html(path):
    with open(path) as f:
        content = f.readlines()
        return '\n'.join(content)

def get_HTML(url, header, path):
    try:
        res = requests.get(url, timeout=0.2, headers=header)
    except requests.exceptions.ReadTimeout:
        return None
    except requests.exceptions.ConnectionError:
        print("sleep 10 sec")
        time.sleep(10)
        return None
    if res.ok:
        with open(path, 'w') as f:
            f.write(res.text)
        return res.content
    else:
        return None

def get_title(soup):
    title = soup.find('h1', class_="recipe-title fn clearfix").get_text().strip()
    return {"title": title}

def get_ingredients(soup):
    def get_ingredient(soup):
        if soup.find("div", class_="ingredient_name"):
            ingredient_name = soup.find("div", class_="ingredient_name").get_text().strip()
            ingredient_value = soup.find("div", class_="ingredient_quantity").get_text().strip()
            return {"ingredient_name": ingredient_name, "ingredient_value": ingredient_value}
        else:
            return None

    ingredients = soup.find_all("div", class_="ingredient_row")
    ingredients_list = []
    for ingredient in ingredients:
        ingredient_dict = get_ingredient(ingredient)
        if ingredient_dict:
            ingredients_list.append(ingredient_dict)
    return {"ingredients_list": ingredients_list}

def get_recipe_steps(soup):
    def get_recipe_step(soup):
        data_position = soup.get("data-position")
        step_text = soup.find("p", class_="step_text").get_text().strip()
        return {"data_position": data_position, "step_text": step_text}

    steps = soup.find_all("div", class_=re.compile("step.*"))
    steps_list = []
    for step in steps:
        step_dict = get_recipe_step(step)
        steps_list.append(step_dict)
    return {"steps_list": steps_list}

def get_advice(soup):
    if not soup.find("div", id="advice"):
        return {"advice": ""}
    advice = soup.find("div", id="advice").get_text().strip()
    return {"advice": advice}

def get_history(soup):
    if not soup.find("div", id="history"):
        return {"history": ""}
    history = soup.find("div", id="history").get_text().strip()
    return {"history": history}

def get_recipe_id_and_published_date(soup):
    recipe_id_and_published_date = soup.find("div", id="recipe_id_and_published_date").get_text()
    recipe_id = regex_recipe_id.search(recipe_id_and_published_date).group(1)
    published_date = regex_published_date.search(recipe_id_and_published_date).group(1)
    published_date = datetime.strptime(f"20{published_date}", '%Y/%m/%d').date()
    recipe_id_and_published_date_dict = {"recipe_id": recipe_id, "published_date": str(published_date)}
    if regex_updated_date.search(recipe_id_and_published_date):
        updated_date = regex_updated_date.search(recipe_id_and_published_date).group(1)
        updated_date = datetime.strptime(f"20{updated_date}", '%Y/%m/%d').date()
        recipe_id_and_published_date_dict["updated_date"] = str(updated_date)
    return recipe_id_and_published_date_dict


def get_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    content_dict = {}
    content_dict.update(get_title(soup))
    content_dict.update(get_ingredients(soup))
    content_dict.update(get_recipe_steps(soup))
    content_dict.update(get_advice(soup))
    content_dict.update(get_history(soup))
    content_dict.update(get_recipe_id_and_published_date(soup))
    return content_dict

def dump_json(contents, path):
    with open(path, 'w') as f:
        json.dump(contents, f, indent=4)

def main():
    contents = {}
    ua = UserAgent()
    skip_num =  int(sorted(os.listdir("data/html/"))[-1].replace(".html", ""))
    print(f"skip_num is {skip_num}")
    # TODO: 手動で書き換えなくても途中から再開できるようにする
    for i in range(1731500, 6000000):
        if i % 1000 == 0:
            print(i)
            ua = UserAgent()
            dump_json(contents, f"data/json/{i}.json")
            contents = {}
        if i % 5 == 0:
            header = {'user-agent': ua.edge}
        elif i % 5 == 1:
            header = {'user-agent': ua.ie}
        elif i % 5 == 2:
            header = {'user-agent': ua.chrome}
        elif i % 5 == 3:
            header = {'user-agent': ua.firefox}
        elif i % 5 == 4:
            header = {'user-agent': ua.safari}

        content = None
        url = f"{baseURL}{i}"
        path = f"data/html/{i}.html"
        if i < skip_num:
            if os.path.exists(path):
                content = read_html(path)
        else:
            content = get_HTML(url, header, path)
            time.sleep(0.2)
        if content:
            contents[i] = get_content(content)
        

if __name__ == "__main__":
    main()