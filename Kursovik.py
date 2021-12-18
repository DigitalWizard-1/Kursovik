import requests
import os
import json

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create(self, name_path: str):
        create_url = 'https://cloud-api.yandex.net/v1/disk/resources?path='+name_path
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}
        response = requests.put(create_url, headers=headers)
        return response

    def upload(self, file_path: str, papka: str):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}
        params = {"path": papka + '/' + file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        load_dict = response.json()
        href = load_dict.get("href", "")
        response = requests.put(href, data=open(file_path, 'rb'))
        response.raise_for_status()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def search_people(self, name):
        people_search_url = self.url + 'users.get'
        people_search_params = {
            'user_ids': name
        }
        req = requests.get(people_search_url, params={**self.params, **people_search_params}).json()
        return req

    def find_photo(self, id):
        find_photo_url = self.url + 'photos.get'
        find_photo_params = {
            'owner_id': id,
            'extended' : 1,
            'photo_sizes' : 1,
            'album_id': 'profile',
            'count' : 1000
        }
        req = requests.get(find_photo_url, params={**self.params, **find_photo_params}).json()
        return req['response']


def find_photo_max(list_photo):
    size = 0
    url = ''
    type = ''
    for num_photo in list_photo:
        height = num_photo['height']
        width = num_photo['width']
        if size < height + width:
            size = height + width
            type = num_photo['type']
            url = num_photo['url']
    return url, type

def photo_vk():
    global number_photo
    dim = []
    for num in photo:
        number_photo += 1
        likes = str(num['likes']['count'])
        name, type = find_photo_max(num['sizes'])
        if number_photo == 1:
            dim = [likes + '.jpg', name, type]
        else:
            flag = 0
            for i in range(number_photo - 1):
                if dim[i * 3] == likes + '.jpg':
                    flag = 1
            if flag:
                likes += '_' + str(number_photo)
            dim += [likes + '.jpg', name, type]
    return dim

def save_photo(n):
    for i in range(n):
        print('сохраняем фотку:', i)
        path_to_file = photo_alboum[i * 3 + 1]
        req = requests.get(path_to_file)
        with open(temp_dir + '/' + photo_alboum[i * 3], 'wb') as file:
            file.write(req.content)

def upload(n):
    json_file = []
    for i in range(n):
        path_to_file = photo_alboum[i * 3]
        print('Передаем фотку:', path_to_file)
        uploader.upload(path_to_file, alboum)
        sc = {}
        sc['file_name'] = path_to_file
        sc['size'] = photo_alboum[i * 3 + 2]
        json_file.append(sc)
    print('Создаем json-файл')
    json_data = json.dumps(json_file)
    with open("data.json", "w") as file:
        file.write(json_data)
    uploader.upload("data.json", alboum)


token_vk = ""
vk_client = VkUser(token_vk, '5.131')
id = int(vk_client.search_people('begemot_korovin')['response'][0]['id'])

print('Загружаем фотки со страницы VK')
photo = vk_client.find_photo(id)
number = photo['count']
photo = photo['items']

print('Обробатываем фотки')
photo_alboum = []
number_photo = 0
photo_alboum = photo_vk()

print('Создаем папку на Яндекс.Диск')
token_yandex = ""
uploader = YaUploader(token=token_yandex)
alboum = 'VK_Alboum'
temp_dir = 'PhotoVK'
res=uploader.create(alboum)

print('Записываем фотки к нам на компьютер')
if not os.path.isdir(temp_dir):
   os.mkdir(temp_dir)
save_photo(number_photo)

print('теперь будем загружать их на Яндекс.Диск')
os.chdir(temp_dir)
upload(number_photo)

