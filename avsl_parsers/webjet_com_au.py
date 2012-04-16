#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

sys.path.append(os.path.abspath(".."))

import utils

# перенаправляем стандартный вывод в лог файл
utils.redirect_stdout('webjet.com.au')

import re
import json
import datetime
from grab import Grab

def parse(queue):
    utils.log('start...')
    request = queue.get()
    success, response = page_hybridflightresults_aspx(request)
    print success, response
    utils.log('done')
    queue.put({ 'success': success, 'flags':['no_range'], 'response': response })

# функции даты-времени

def get_date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%dT%H:%M:%S' if "T" in str else '%Y-%m-%d')

def get_ampm_time(str):
    return datetime.datetime.strptime(str, '%I:%M %p').timetz()

def get_full_date(date, time):
    return datetime.datetime.combine(
        get_date(date) if type(date) is str else date,
        get_ampm_time(time) if type(time) is str else time
    )

def get_str_date(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')

def get_hour_minute_time(str):
    '''
    Возвращает объект время, спарсенный из входной строки str (пример строки, '16hrs 40mins').
    Если парсинг закончился ошибкой - возвращает строку '???'
    '''
    try:
        r = r'(\d+)hrs (\d+)mins'
        m = re.match(r, str)
        return datetime.timedelta(hours=int(m.group(1)), minutes=int(m.group(2))).seconds
    except Exception, e:
        return '???'

def page_hybridflightresults_aspx(request):
    '''
    Функция парсинга страницы результатов
    '''

    if request["return_date"] is None:
        request["return_date"] = request["depart_date"]

    get_params = {
        'TripType':'Return',
        'CityFrom':request['origin_iata'],
        'DateOut':request['depart_date'].replace('-', '%2F'),
        'CityTo':request['destination_iata'].replace(' ', '+'),
        'DateBack':request['return_date'].replace('-', '%2F'),
        'TravelClass':request['trip_class'],
        'NumAdult':request['adults'],
        'NumChild':request['children'],
        'NumInfant':request['infants'],
        'EntryPoint':'Flight',
        'RequestFrom':'Outside'
    }

    temp = []
    for k,v in get_params.items():
        temp.append(k + '=' + v)
    get_params = '&'.join(temp)

    content = utils.run_php_script('avsl_parsers/webjet_com_au_get_content.php', get_params)
    if content.strip() == 'timeout':
        return False, "Airline server is not responding"

    try:
        g = Grab()
        g.response.body = content
        pt = '<span id="devFooter".*jQuery\.parseJSON\(\'(.*)\'\), jQuery\.parseJSON\(\'(.*)\'\)\];'
        m = g.rex(re.compile(pt, re.M|re.S))
    except Exception:
        return False, 'Has Been A Changes in Airline Service'

    r = []
    try:
        r.extend(page_hybridflightresults_aspx_parse_json(request, m.group(1), 0))
        if m.group(2) != 'null':
            r.extend(page_hybridflightresults_aspx_parse_json(request, m.group(2), 1))
    except Exception, e:
        print "Parsing Exception " + str(e)
    finally:
        pass

    return True, r

def page_hybridflightresults_aspx_parse_json(request, v, route_leg):
    '''
    транслируем словарь, полученный из json"а в выходной массив данных
    '''

    d = json.loads(v)
    print request
    request_departure = get_date(request["depart_date"])
    proposals = []
    for ff in d[u'Fares']:
        for f in ff[u'FlightFares']:
            proposal = {
                "total":f[u'PriceValue'],
                "currency":"AUD",
                "main_airline":f[u'FlightCarrier'],
                "flights":None
            }
            info = f[u'FlightFareInfo']
            flights = []
            for item in info[u'Items']:
                # todo для каждого рейса возвращаем duration, который указан для всего перелета
                # дата вылета
                departure_date = get_full_date(request_departure, str(item[u'DepartureTime']))
                # дата прибытия
                arrival_date = get_full_date(request_departure, str(item[u'ArrivalTime']))
                # если дата вылета больше, чем дата прилета, то увеличиваем дату прилета на день
                #if departure_date >= arrival_date:
                #    arrival_date += datetime.timedelta(days=1)

                flights.append({
                    "number":item[u'FlightNumber'],
                    "airline":item[u'AirlineName'],
                    "origin": item[u'ArrivalCity'],
                    "destination":item[u'DepartureCity'],
                    "departure":get_str_date(departure_date),
                    "arrival":get_str_date(arrival_date),
                    "duration":str(get_hour_minute_time(str(info[u'FlightTime']))),
                    "route_leg":str(route_leg),
                    "aircraft":item[u'Plane']
                })
            proposal['flights'] = flights
            proposals.append(proposal)

    return proposals

def main():
    request = {
        "origin_iata":None,
        "destination_iata":None,
        "depart_date":'2012-04-20T00:00:00',
        "return_date":None,
        "adults":None,
        "children":None,
        "infants":None,
        "trip_class":None,
        "range":None
    }
    response = page_hybridflightresults_aspx(request)
    if not response:
        utils.log('not response')
    else:
        utils.log(response)

if __name__ == "__main__":
    main()
