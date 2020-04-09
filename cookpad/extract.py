import json
import os

def read_json(path):
    with open(path) as f:
        recipes = json.load(f)
    return recipes

def extract_text(recipes):
    for key, recipe in recipes.items():
        for step in recipe['steps_list']:
            yield step['step_text']

def output(path, text):
    with open(path, 'w') as f:
        for sentence in text:
            f.write(sentence)
            f.write('\n')

def main():
    base_dir = './cookpad/json/'
    text = []
    for file in os.listdir(base_dir):
        recipes = read_json(base_dir + file)
        for sentence in extract_text(recipes):
            text.append(sentence)
    output('recipes.txt', text)

if __name__ == '__main__':
    main()
