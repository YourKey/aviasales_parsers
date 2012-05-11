# -*- coding: utf-8 -*-
__author__ = 'vit'

import time
import redis
import json

LIFETIME = 900 # 15 minutes

class ReadException(Exception):
    pass

class WriteException(Exception):
    pass

_rc = None

def _redis_connection():
    global _rc
    if not _rc:
        # Получаем доступ к пулу соединений
        pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
#        pool = redis.ConnectionPool(host='localhost', port=8013, db=0)
        # Получаем объект доступа к апи сервера redis
        _rc = redis.Redis(connection_pool=pool)
    return _rc

def encode_dict(dct):
    return json.dumps(dct)

def decode_dict(str):
    return json.loads(str)

def set_each(prefix, arr):
    '''
    записываем массив значений в хеш
    Возвращает массив ключей в хеше для входных значений
    '''

    # Получаем объект доступа к апи сервера redis
    r = _redis_connection()
    # получаем часть таймстампа
    t = ("%.5f" % time.time()).replace('.', '')[5:]
    # todo: начинаем транзакцию
    try:
        # устанавливаем значения элементов массива в хеш
        names = []
        for i, v in enumerate(arr):
            j = ("%4d" % i).replace(' ', '0')
            ck = prefix + ':' + t + j
            cv = encode_dict(v) if type(v) == dict else v
            r.setex(ck, cv, LIFETIME)
            names.append(t + j)

        # todo: выполняем транзакцию
    except Exception, e:
        # todo: записываем в лог ошибку установки хеша
        return False
    else:
        return names

def get(prefix, id):
    # Получаем объект доступа к апи сервера redis
    r = _redis_connection()
    # Получаем значение из хеша по ключу
    return r.get(prefix + ":" + id)

def main():
    '''
    Пример использования

    d = {
        "a": 1,
        "b": "value",
        "c": {
            "d":"other value"
        }
    }

    prefix = 'av_proposals'
    names= set_each(prefix, [1,'test','ololo', json.dumps(d)])
    if not names:
        print "empty or error"
    else:
        print json.loads(get(prefix, names[3]))
    '''
    pass

if __name__ == "__main__":
    main()
