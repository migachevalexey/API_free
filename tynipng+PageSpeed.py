import requests
import tinify
import os
from PIL import Image
import piexif
import re

'''
Забираем картинки с сайта по URL(URL получаем по API или берем из файла links.txt).
Сохраняем их в ./links/big/ (на всякий случай)
Отправляем картинку в сервис tinypng.com - сжимаем там и сохраняем в ./links/small/
'''

google_api_key = '123'
tinify.key = "123"
page_url = 'https://my_site.ru/cat/248-479-452282'  # URL страницы, по которой запускаем тест скорости
site= re.findall(r'\/\w+', page_url)[0][1:]
print (site)

def PageSpeedOnline(page_url):

    # Через API получаем картинки, которые нужно оптимизировать
    # На выходе список из URL-картинок

    r = requests.get('https://www.googleapis.com/pagespeedonline/v2/runPagespeed',
                     params={'url': page_url, 'key': google_api_key}).json()
    z = dict(r['formattedResults']['ruleResults']['OptimizeImages']['urlBlocks'][0])
    image_links = [i['result']['args'][0]['value'] for i in z['urls']]

    return image_links

def del_exif(file):
    im = Image.open(f'./links/{site}'+f'/small/{file}')
    piexif.remove(f'./links/{site}/small/{file}')
    im.save(f'./links/{site}/small/oneexif/{file}')

def images_working():

    image_links = PageSpeedOnline(page_url)
    # with open('./links/links_us.txt','r') as f:
    path_big = fr'C:\Python\API_REAL\links\{site}\big'
    path_small = fr'C:\Python\API_REAL\links\{site}\small'
    if not os.path.exists(path_big):
        os.makedirs(path_big)
    if not os.path.exists(path_small):
        os.makedirs(path_small)
    for line in image_links:
        # url=line.split()[0] - если берем из файла. См. сам файл и все станет ясно
        url = line
        r = requests.get(url)
        file_name = url.split('/')[-1]
        try:
            with open(path_big+'/'+file_name, 'bw') as fw:
                fw.write(r.content)
            source = tinify.from_file(path_big+'/'+file_name)
            source.to_file(path_small+'/'+file_name)
            # del_exif(file_name) # удаляем метадата
            big_size = round(os.path.getsize(path_big+'/'+file_name) / 1024, 2)
            small_size = round(os.path.getsize(path_small +'/'+file_name) / 1024, 2)
            print(f'Начальный: {big_size}Kb, конечный: {small_size}Kb, разница: {round(big_size-small_size, 2)}Kb')
        except: continue

images_working()