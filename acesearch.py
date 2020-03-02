# coding=utf-8
# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error, os, configparser, ssl, json

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

#####Парсинг JSON-файла#########

url_ace_json = 'https://search.acestream.net/all?api_version=1.0&api_key=test_api_key'
gcontext = ssl.SSLContext()  # Only for gangstars
ace_req = urllib.request.urlopen(url_ace_json, context=gcontext).read()
ace_json = ace_req.decode() #Долбаный юникод...
ace_json_str_split = json.loads(ace_json)

k = 0 #Счетчик
name = [] #Список названий каналов
cat = [] #Список названий категорий каналов
infohash = [] #Список инфохешей каналов
number_of_favorite_channels = [] #Список порядковых номеров каналов отобраных в избранное 

for string in ace_json_str_split:
    name.append(string['name'].strip())

    if 'categories' in string:
        cat.append(string['categories'])
    else:
        cat.append('')

    infohash.append(string['infohash'])
    if createfavorite == '1' or createfavoriteproxy == '1':
        for channel in favoritechannales_split:
            if name[k].find(channel) != -1:
                number_of_favorite_channels.append(k)
    k = k + 1

print("Найдено каналов: " + str(len(name)))

################################

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

while n != k:
    print(name[n])
    if createplaylistall == '1':
        if usecontentid == '1' and int_serv_work:
            content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
            result = json.loads(urllib.request.urlopen(content_id_gen_url).read())
            output.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + '" ,' +  name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?id=' + result['result']['content_id'] + '&.mp4\n')
        else:
            output.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + ',' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')
            
    if createfavorite == '1':
        for i in number_of_favorite_channels:
            if n == i:
                if usecontentid == '1' and int_serv_work:
                    content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
                    result = json.loads(urllib.request.urlopen(content_id_gen_url).read())
                    output.write('#EXTINF:-1, group-title="' + ','.join(cat[n]) + '" ,' +  name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?id=' + result['result']['content_id'] + '&.mp4\n')
                else:
                    output_favorite.write('#EXTINF:-1 group-title="' + ','.join(cat[n]) + '" ,' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')
            
    n = n + 1

#####Отдельно создание прокси плейлиста#####

if createfavoriteproxy == '1':
    content_id = []
    k = 0
    for n in number_of_favorite_channels:
        content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
        content_id.append(str(urllib.request.urlopen(content_id_gen_url).read())[29:])
        content_id[k] = content_id[k][:40]
        print(content_id[k])
        k = k + 1
        
    outputproxy = open(outputfolder + playlistfavoriteproxyfilename, 'w', encoding='utf-8')
    outputproxy.write('#EXTM3U\n')
    n = 0
    for id in content_id:
        outputproxy.write('#EXTINF:-1 group-title="' + cat[number_of_favorite_channels[n]] + ',' + name[number_of_favorite_channels[n]] + '\n' + 'http://' + aceproxyserveradressport + '/pid/' + str(id) + '/stream.mp4' + '\n')
        n = n + 1
    outputproxy.close()
	
############################################
	
if createplaylistall == '1':
    output.close()
    print("Список всех каналов подготовлен.")
if createfavorite == '1':
    output_favorite.close()
    print("Список избранных каналов подготовлен.")
