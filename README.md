По существу: скрипт берет json файл с сервера acestream оттуда же откуда и в оригинальном скрипте и может преобразовывать его в плейлисты:
1)Полный список каналов в виде http://адрес:порт/ace/getstream?infohash=хеш
2)Список избранных каналов в виде http://адрес:порт/ace/getstream?infohash=хеш
3)Список избранных каналов для прокси от Pepsik в виде http://адрес:порт/pid/контент_ид/stream.mp4
Список избранных каналов формируется поиском по ключевым словам (например если в виде ключевого слова выбрать символ "D", то в избранное попадут ВСЕ каналы в названии которых хоть один раз содержится символ "D" с учетом регистра). IP адреса сервера acestream и proxy, папка для плейлистов, названия файлов плейлистов и какие из них создавать или нет, а также список ключевых слов через запятую прописываются в файле config.ini лежащий в одной папке с основным файлом. В случае отсутствия конфигурационного файла скрипт создаст новый дефолтный (по умолчанию настроено только создание избранного плейлиста).
Реализация плейлиста для прокси (в частности нахождение content_id по infohesh) сделана с помощью локального сервера acestream способом найденным на этом же форуме, но занимает некоторое время, поэтому сделал только для избранных каналов (во время работы скрипта в терминале можно наблюдать список content_id, использовал для дебага, но оставил чтобы наглядно было видно что скрипт работает а не висит).
