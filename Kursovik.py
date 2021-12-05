import requests
import os
import json

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create(self, name_path: str):
        Create_url = 'https://cloud-api.yandex.net/v1/disk/resources?path='+name_path
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}
        response = requests.put(Create_url, headers=headers)
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
    for num_photo in list_photo:
        height = num_photo['height']
        width = num_photo['width']
        if size < height + width:
            size = height + width
            type = num_photo['type']
            url = num_photo['url']
    return url, type


print('Читаем токен VK')
with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()

vk_client = VkUser(token, '5.131')
id = int(vk_client.search_people('begemot_korovin')['response'][0]['id'])
print('Загружаем фотки со страницы VK')

Photo = vk_client.find_photo(id)
Number = Photo['count']
Photo = Photo['items']

dim = []
n = 0

print('Обробатываем фотки')
for num in Photo:
    n += 1
    likes = str(num['likes']['count'])
    name, type = find_photo_max(num['sizes'])
    if n == 1:
        dim = [likes + '.jpg', name, type]
    else:
        flag = 0
        for i in range(n-1):
            if dim[i * 3] == likes + '.jpg':
                flag = 1
        if flag:
            likes += '_'+str(n)
        dim += [likes + '.jpg', name, type]


print('Создаем папку на Яндекс.Диск')

TOKEN_Yandex = ""
uploader = YaUploader(token=TOKEN_Yandex)
Alboum = 'VK_Alboum'
TempDir = 'PhotoVK'
res=uploader.create(Alboum)

if not os.path.isdir(TempDir):
   os.mkdir(TempDir)

print('Записываем фотки к нам на компьютер')
for i in range(n):
    print('сохраняем фотку:', i)
    path_to_file = dim[i * 3 + 1]
    req = requests.get(path_to_file)
    with open(TempDir+'/' + dim[i * 3], 'wb') as file:
        file.write(req.content)

print('теперь будем загружать их на Яндекс.Диск')
os.chdir(TempDir)
Json_file= []
for i in range(n):
    path_to_file = dim[i * 3]
    print('Передаем фотку:', path_to_file)
    uploader.upload(path_to_file, Alboum)
    sc = {}
    sc['file_name'] = path_to_file
    sc['size'] = dim[i * 3 + 2]
    Json_file.append(sc)
jsonData = json.dumps(Json_file)
with open("data.json", "w") as file:
    file.write(jsonData)


