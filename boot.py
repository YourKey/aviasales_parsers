#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, logging, traceback
from multiprocessing import Process, Queue
from _importlib import import_module

##############################################
# Функии логирования
#
# Флаги
#
#   CRITICAL - в случае подения сервера
#   ERROR - в случае ошибки парсинга
#   WARNING - ???
#   INFO - ???
#   DEBUG - отладочная инфа (включена в дебаг рефиме)
#   NOTSET - ???
#

DEBUG_LOGGING = True

LOGGER_CONFIG = {
    'name':'Aviasales Parser',
    'mode':logging.DEBUG,
    'formatting':'%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'handlers': [{
        'target':'file',
        'mode':logging.DEBUG,
        'logfile':'logs/access.log'
    },{
        'target':'file',
        'mode':logging.WARN,
        'logfile':'logs/errors.log'
    }, {
        'target':'stream',
        'mode':logging.DEBUG if DEBUG_LOGGING else logging.WARN
    }]
}

logger = None

def refresh_logger():
    _init_logging(LOGGER_CONFIG)

def _init_logging(config):
    global logger
    # create logger
    logger = logging.getLogger(config['name'])
    logger.setLevel(config['mode'])

    # create formatter
    formatter = logging.Formatter(config['formatting'])

    for x in config['handlers']:
        if x['target'] == 'file':
            # create file handler
            h = logging.FileHandler(x['logfile'])
        else:
            # create console handler
            h = logging.StreamHandler()
        # set level
        h.setLevel(x['mode'])
        # add formatter to fh
        h.setFormatter(formatter)
        # add fh to logger
        logger.addHandler(h)

    return logger

_init_logging(LOGGER_CONFIG)

##############################################
# Форматирование ответа
#

def failed_xml_response(error_message):
    '''
    Server Error Response
    '''
    return '<?xml version="1.0"?>\n<search_result error_message="%s" />' % (error_message, )

def successful_xml_response(response):
    '''
    Преобразует словарь или массив в xml
    Возвращает ответ сервера в виде строки в формате xml
    '''
    if not response:
        # Nothing Found Response
        body = '<search_result />\n'
    else:
        proposals = []
        for x in response:
            proposal = '<proposals main_airline="%(main_airline)s" total="%(total)s" currency="%(currency)s" id="uniq_proposal_id">\n' % x
            for z in x['flights']:
                proposal += '<flights number="%(number)s" airline="%(airline)s" origin="%(origin)s" ' \
                            'destination="%(destination)s" departure="%(departure)s" arrival="%(arrival)s" ' \
                            'duration="%(duration)s" route_leg="%(route_leg)s" aircraft="%(aircraft)s" />\n' % z
            proposal += '</proposals>'
            proposals.append(proposal)
        body = '<search_result>\n' + '\n'.join(proposals) + '</search_result>'
    return '<?xml version="1.0"?>\n' + body

def _check_type(v, t, var_name):
    if type(v).__name__ != t:
        raise TypeError('variable "%s" does not match the specified type "%s"' % (var_name, t))
    return True

def _dict_isset(v, attr, var_name):
    if v.get(attr, '--false--') == '--false--':
        raise ValueError('in the "%s" dictionary not found the attribute "%s" ' % (var_name, attr))
    return True

def check_response(host_name, response):
    '''
    Проверяем формат ответа парсера на валидность
    '''

    try:
        _check_type(response, 'list', 'response')
        for x in response:
            _check_type(x, 'dict', 'proposal')
            _dict_isset(x, 'total', 'proposal')
            _dict_isset(x, 'currency', 'proposal')
            _dict_isset(x, 'main_airline', 'proposal')
            _dict_isset(x, 'flights', 'proposal')
            _check_type(x['flights'], 'list', 'flights')
            for y in x['flights']:
                _check_type(y, 'dict', 'flight')
                _dict_isset(y, 'number', 'flight')
                _dict_isset(y, 'airline', 'flight')
                _dict_isset(y, 'origin', 'flight')
                _dict_isset(y, 'destination', 'flight')
                _dict_isset(y, 'departure', 'flight')
                _dict_isset(y, 'duration', 'flight')
                _dict_isset(y, 'route_leg', 'flight')
                _dict_isset(y, 'aircraft', 'flight')
    except Exception, e:
        logger.error('Error Response Formatting For "%s"! %s' % (host_name, str(e), ))
        return False
    else:
        return True

##############################################
# запуск парсера оформленного в виде python модуля
#

PARSER_DIR = "avsl_parsers"

AVAILABLE_HOSTS = ["webjet.com.au", "webjet.com"]

sys.path.append(os.path.abspath(""))

def import_parser_by_host(host):
    parser_name = host.replace('.','_')
    return import_module(PARSER_DIR + "." + parser_name)

class ParserError(Exception):
    pass

def run_parse(host_name, request):
    '''
    Запускаем парсер в отдельном потоке
    '''

    try:
        if host_name not in AVAILABLE_HOSTS:
            # сообщаем в лог о неправильном запросе
            raise ValueError("Unavailable Host " + host_name)

        queue = Queue()
        queue.put(request)
        parser = import_parser_by_host(host_name)
        p = Process(target=parser.parse, args=(queue,))
        p.start()
        p.join()
        response = False
        try:
            response = queue.get_nowait()
        finally:
            error_message = "Runtime Parser Error"

            if response.get('response', False) is False:
                raise ParserError(error_message)

            if not response.get('success', False):
                raise ParserError(response.get('response', error_message))

        results = response.get('response')

        flags = response.get('flags', False)
        if flags and type(flags) == type([]):
            if 'no_range' in flags and request['range']:
                try:
                    min_value, max_value = map(float, request['range'].split(','))
                    temp = filter(lambda value: min_value <= value['total'] <= max_value, results)
                except Exception:
                    pass
                else:
                    results = temp

        response = results

    except Exception, e:
        # Ошибка выполнения модуля, записываем ошибку в лог выводим в консоль
        error_message = ''
        if DEBUG_LOGGING:
            error_message = '\n' +\
                traceback.format_exc()
        error_message += str(e)
        logger.critical(error_message)
        return False, e

    return True, response

def main():
    print 'No direct script access'

if __name__ == "__main__":
    main()
