import requests
import json
import time
import base64
import os
import shutil

class Text2ImageAPI:
    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_model(self):
        response = requests.get(self.URL + 'key/api/v1/models', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'model_id': (None, model),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/text2image/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/text2image/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['images']

            attempts -= 1
            time.sleep(delay)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def clear_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        os.makedirs(directory)

def get_next_file_number(directory):
    existing_files = [f for f in os.listdir(directory) if f.endswith(".jpg")]
    numeric_files = [int(f.split('.')[0]) for f in existing_files if f.split('.')[0].isdigit()]
    return max(numeric_files, default=0) + 1

def gen(prompt, dirr="photo", etap="Etap 1"):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/',
                        '3E522E54EB474C0AA97156C5021EFE00',
                        'E7A5EE1FCBB86DCBC49DE04EABC06AAE')
    model_id = api.get_model()
    uuid = api.generate(prompt, model_id)
    images = api.check_generation(uuid)

    image_base64 = images[0]
    image_data = base64.b64decode(image_base64)

    etap_dir = ensure_directory_exists(os.path.join(dirr, etap))
    next_file_number = get_next_file_number(etap_dir)
    save_path = os.path.join(etap_dir, f"{next_file_number}.jpg")

    with open(save_path, "wb") as file:
        file.write(image_data)

# Запрос данных у пользователя
zapros = input("Запрос: ")
etap_number = input("Номер этапа игры: ")

dir_path = "photo"
etap = f"Etap {etap_number}"

ensure_directory_exists(dir_path)
clear_directory(os.path.join(dir_path, etap))

# Генерация изображений
for j in range(2):  # количество генераций
    gen(zapros.replace("\n", " "), dir_path, etap)
    print(f"Сделано генераций {j + 1}")

print("Генерация завершена")
