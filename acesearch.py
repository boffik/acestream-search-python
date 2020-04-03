#!/usr/bin/python3
# coding=utf-8
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error, os, configparser, ssl, json, uuid

def createConfig(path): #Создание стандартного конфиг файла

    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "acestreamserveradressport", "127.0.0.1:6878") #Адрес:Порт AceStream сервера
    config.set("Settings", "aceproxyserveradressport", "192.168.0.199:8000") #Адрес:Порт proxy сервера от Pepsik
    config.set("Settings", "outputfolder", "") #Адрес папки где будут создаваться плейлисты (если отсутствует то создастся)
    config.set("Settings", "createplaylistall", "1") #Создание плейлиста со всеми найдеными каналами (1 или 0)
    config.set("Settings", "playlistallfilename", "All.m3u") #Название файла плейлиста со всеми найдеными каналами
    config.set("Settings", "createfavorite", "0") #Создание плейлиста с избранными каналами
    config.set("Settings", "playlistfavoritefilename", "Favorite.m3u") #Название файла плейлиста с избранными каналами
    config.set("Settings", "createfavoriteproxy", "0") #Создание плейлиста с избранными каналами с использованием proxy сервера от Pepsik
    config.set("Settings", "playlistfavoriteproxyfilename", "Favorite_proxy.m3u") #Название файла плейлиста с избранными каналами с использованием proxy сервера от Pepsik
    config.set("Settings", "favoritechannels", "Discovery,Eurosport,Моя Планета") #Ключевые слова для подбора каналов в плейлист избранного (регистр имеет значение)
    config.set("Settings", "contentid", "1") #Использовать content_id в плейлистах, иначе будут infohash
    
    with open(path, "w", encoding='utf-8') as config_file:
        config.write(config_file)

#####Работа с конфиг файлом#####

if not os.path.exists('settings.cfg'):
        createConfig('settings.cfg')

config = configparser.ConfigParser()
config.read('settings.cfg', encoding='utf-8')
acestreamserveradressport = config.get("Settings", "acestreamserveradressport")
aceproxyserveradressport = config.get("Settings", "aceproxyserveradressport")
outputfolder = config.get("Settings", "outputfolder")
createplaylistall = config.get("Settings", "createplaylistall")
playlistallfilename = config.get("Settings", "playlistallfilename")
createfavorite = config.get("Settings", "createfavorite")
playlistfavoritefilename = config.get("Settings", "playlistfavoritefilename")
createfavoriteproxy = config.get("Settings", "createfavoriteproxy")
playlistfavoriteproxyfilename = config.get("Settings", "playlistfavoriteproxyfilename")
favoritechannales = config.get("Settings", "favoritechannels")
usecontentid = config.get("Settings", "contentid")
favoritechannales_split = favoritechannales.split(',')

################################

if outputfolder != '':
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder) #Проверка наличия и создание папки для плейлистов


################################

def test_connection(test_url):
    try:
        urllib.request.urlopen(test_url, timeout=1)
        return True
    except urllib.request.URLError as err:
        print('Адрес ' + test_url + ' недоступен')
        return False

################################


def sort_dict(dict):
    sorted_pairs = [(k, dict[k]) for k in sorted(dict.keys(), key=dict.get, reverse=False)]
    return sorted_pairs


#####Парсинг JSON-файла#########

url_ace_json = 'https://search.acestream.net/all?api_version=1.0&api_key=test_api_key'
gcontext = ssl.SSLContext()  # Only for gangstars
ace_json = urllib.request.urlopen(url_ace_json, context=gcontext).read().decode()
ace_json_items = json.loads(ace_json)

name = {} #Словарь названий каналов
cat = {} #Словарь названий категорий каналов
infohash = {} #Словарь инфохешей каналов

favorite_channels = [] #Список порядковых номеров каналов отобраных в избранное

for item in ace_json_items:
    item_name = item['name'].strip()
    item_uuid = uuid.uuid5(uuid.NAMESPACE_X500, item_name)

 #   print(item_uuid , item_name)
    name.update({item_uuid : item_name})

    if 'categories' in item:
        cat.update({item_uuid : item['categories']})
    else:
        cat.update({item_uuid : ''})

    infohash.update({item_uuid : item['infohash']})

    if createfavorite == '1' or createfavoriteproxy == '1':
        for channel in favoritechannales_split:
            if item_name.find(channel) != -1:
                favorite_channels.append(item_uuid)

print("Найдено каналов: " + str(len(name)))

################################

s_dict = sort_dict(name)

#####Создание плейлистов########

int_serv_work = test_connection('http://' + acestreamserveradressport + '/server/api/')

if createplaylistall == '1':
    output = open(outputfolder + playlistallfilename, 'w', encoding='utf-8')
    output.write('#EXTM3U\n')
if createfavorite == '1':
    output_favorite = open(outputfolder + playlistfavoritefilename, 'w', encoding='utf-8')
    output_favorite.write('#EXT3U\n')

n = 0

print("Начинаем обработку найденных каналов.")

print("Заполняем общий плейлист")
for n, k in s_dict:
    if createplaylistall == '1':
        if usecontentid == '1' and int_serv_work:
            content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
            content_id = json.loads(urllib.request.urlopen(content_id_gen_url).read())['result']['content_id']
            output.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + '" ,' +  name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?id=' + content_id + '&.mp4\n')
        else:
            output.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + '" ,' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')

output.close()
print("Плейлист всех каналов подготовлен.")

if createfavorite == '1':
    print("Заполняем плейлист избранных каналов")
    for n in favorite_channels:
        if usecontentid == '1' and int_serv_work:
            content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
            content_id = json.loads(urllib.request.urlopen(content_id_gen_url).read())['result']['content_id']
            output_favorite.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + '" ,' +  name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?id=' + content_id + '&.mp4\n')
        else:
            output_favorite.write('#EXTINF:-1 group-title="' + ','.join(cat[n]) + '" ,' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')

output_favorite.close()
print("Плейлист избранных каналов подготовлен.")
#####Отдельно создание прокси плейлиста#####

if createfavoriteproxy == '1':

    outputproxy = open(outputfolder + playlistfavoriteproxyfilename, 'w', encoding='utf-8')
    outputproxy.write('#EXTM3U\n')
    print("Заполняем плейлист прокси")
    for n in favorite_channels:
        content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
        content_id = json.loads(urllib.request.urlopen(content_id_gen_url).read())['result']['content_id']
        outputproxy.write('#EXTINF:-1 group-title="' + ','.join(cat[n]) + '" ,' + name[n] + '\n' + 'http://' + aceproxyserveradressport + '/pid/' + str(content_id) + '/stream.mp4' + '\n')

outputproxy.close()
print("Плейлист каналов для прокси подготовлен.")
############################################
