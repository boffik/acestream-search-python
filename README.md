# acestream-search-python®

По существу: скрипт берет json файл с сервера acestream оттуда же откуда и в оригинальном скрипте и может преобразовывать его в плейлисты:

1)Полный список каналов. 

2)Список избранных каналов.

3)Список избранных каналов для прокси от Pepsik в виде http://address:port/pid/content_id/stream.mp4

Список избранных каналов формируется поиском по ключевым словам (например если в виде ключевого слова выбрать символ "D", то в избранное попадут ВСЕ каналы в названии которых хоть один раз содержится символ "D" с учетом регистра).
Также можно из избранных каналов исключать каналы в названии которых есть ключевая фраза.

IP адреса сервера acestream и proxy, папка для плейлистов, названия файлов плейлистов и какие из них создавать или нет, формат ссылок плейлиста http://address:port/ace/getstream?infohash=hash или http://address:port/ace/getstream?id=content_id а также список ключевых слов через запятую прописываются в файле config.cfg лежащий в одной папке с основным файлом. В случае отсутствия конфигурационного файла скрипт создаст новый дефолтный.

Реализация плейлиста для прокси (в частности нахождение content_id по infohash) сделана с помощью локального сервера acestream способом найденным на этом же форуме. 
