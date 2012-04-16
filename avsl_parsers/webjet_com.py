#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

import re
from grab import Grab
from lxml import etree
import datetime

import time, urllib

script_path = os.path.realpath(__file__)
sys.path.append(os.path.normpath(os.path.dirname(script_path) + "/../utils"))

import ptime

def parse(queue):
    request = queue.get()
    response = page_results(request, search_results_content(request))
    queue.put({ 'success': True, 'flags':[], 'response':response })
    pass

def search_results_content(request):

    g = Grab(reuse_cookies = True, reuse_referer=True)

    request = request.copy()
    request["depart_date"] = request["depart_date"].replace('-', '/')
    request["return_date"] = request["return_date"].replace('-', '/')

    g.setup(post={
        'EntryPoint':	'Flight',
        'RequestFrom':	'Outside',
        'TripType':	'rdbRoundTrip',
        'WebSiteId':	'189',
        'arrival_label':	request['origin_iata'],
        'btnSubmitAir':	'Search for flights',
        'ddlCabin':	'Y',
        'ddlPaxADT':	request['adults'],
        'ddlPaxCHD':	request['children'],
        'ddlPaxINF':	request['infants'],
        'departure_label':	request['destination_iata'],
        'flight_search_action':	'http://res.webjet.com/process.aspx',
        'txtArrCity1':	request['origin_iata'],
        'txtArrCity2':	request['destination_iata'],
        'txtDepCity1':	request['destination_iata'],
        'txtDepCity2':	request['origin_iata'],
        'txtdate1':request["depart_date"],
        'txtdate2':request["return_date"],
    })

    g.setup(user_agent="User-Agent	Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0")
    g.go("http://res.webjet.com/process.aspx?agentid=189&" +
         "txtDepCity1=" + request['destination_iata'] +
         "&txtArrCity1=" + request['origin_iata'] +
         "&TripType=rdbRoundTrip" +
         "&txtDate1=" + urllib.quote(request["depart_date"], '') +
         "&txtDate2=" + urllib.quote(request["return_date"], '') +
         "&txtDepCity2=" + request['origin_iata'] +
         "&txtArrCity2=" + request['destination_iata'] +
         "&ddlPaxADT=" + request['adults'] +
         "&ddlPaxCHD=" + request['children'] +
         "&ddlPaxINF=" + request['infants']
    )

    if not g.response.cookies.get("ASP.NET_SessionId", False):
        print "not auth"
        sys.exit(0)

    g.setup(referer = "http://www.webjet.com/flights/")

    loc = g.response.headers.get('Location', False)

    id1 = loc[loc.rindex('=')+1:]

    g.setup(user_agent="User-Agent	Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0")

    g.go("http://res.webjet.com" + loc)

    pat = re.compile(r'id="__VIEWSTATE" value="([^"]+)"')
    _vs = re.search(pat, g.response.body).group(1)

    pat = re.compile(' id=\'Destination_country\' value =([^>]+)')
    _dc = re.search(pat, g.response.body).group(1)

    pat = re.compile(' id=\'Origin_airport\' value =([^>]+)')
    _oc = re.search(pat, g.response.body).group(1)

    print _vs.strip(), _dc.strip(), _oc.strip()

    i=0
    status = False
    while True:
        g.setup(post= {
            "scp": "updServer|timeControl",
            "Destination_airport": request["destination_iata"].upper() + "/",
            "Destination_country": _dc + "/",
            "Origin_airport":  request["origin_iata"].upper() + "/",
            "Origin_country": _oc + "/",
            "Departure_date": request["depart_date"],
            "__EVENTTARGET": "timeControl",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": _vs,
            "__ASYNCPOST": "true"
        })
        g.go("http://res.webjet.com" + loc)
        pat = re.compile('pageRedirect')
        if i==9 or re.search(pat, g.response.body):
            status = True
            break
        time.sleep(1)

    if not status:
        return False

    g.setup(user_agent="User-Agent	Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0")
    g.go("http://res.webjet.com/prices.aspx?page=flightprices&air=Air&id1=" + urllib.quote(id1, ''))

    print len(g.response.body)

    return g.response.body


def page_results(request, content):
    g =  Grab()
    g.response.body = content

    # Example: <li><strong>Departure Time</strong> - 8:55 PM</li>
    flight_field_pattern = re.compile('<li><strong>[^<]+</strong> - ([^<]+)</li>')
    # Example: Sydney, Nsw (SYD) to Kuala Lumpur (KUL) May 8, 2012
    origin_destination_pattern = re.compile('[^\(]+ \(([^\)]+)\) [^\(]+ \(([^\)]+)\).*')
    # Example: <td id="paxAdtTd">1</td><td>$1296.87</td>
    total_propasal_price = re.compile('<td id="paxAdtTd">[^<]*</td><td>\\$([^<]+)</td>')

    # operation_airline = main airline, airline = airline

    def parse_flight(e, route_leg):
        g = Grab()
        g.response.body = etree.tostring(e)

        f = g.css_list('li>ul>li')
        def ff(index):
            return re.match(flight_field_pattern, etree.tostring(f[index])).group(1)

        h = re.match(origin_destination_pattern, g.css_text('li>h5'))
        def hh(index):
            return h.group(index)

        arrival_pattern_plus_day = re.compile('(\d+:\d+ AM) \\+ (\d+) Day')

        arrival_time = ff(3)
        arrival_date = ptime.get_date(request["depart_date"])
        arrival_plus_day = re.match(arrival_pattern_plus_day, arrival_time.strip())
        if arrival_plus_day:
            arrival_time = arrival_plus_day.group(1)
            arrival_date += datetime.timedelta(days = int(arrival_plus_day.group(2)))

        departure = ptime.get_full_date(str(request["depart_date"]), ff(2))
        arrival = ptime.get_full_date(arrival_date, arrival_time)

        return {
            "number":ff(5),
            "airline":ff(4),
            "origin":hh(1),
            "destination":hh(2),
            "departure":ptime.response_date(departure),
            "arrival":ptime.response_date(arrival),
            "duration":ptime.str_timedelta(departure, arrival),
            "route_leg":int(route_leg),
            "aircraft":None,
            "__main_airline":ff(4)
        }

    def parse_proposal(e):
        g = Grab()
        g.response.body = etree.tostring(e)
        flights = []
        first_item = True
        for v in g.css_list('.info>.info>.clearfix'):
            flights.append(parse_flight(v, first_item))
            first_item = False

        return {
            "total":re.search(total_propasal_price,etree.tostring(g.css('#paxAdtTd').find('..'))).group(1),
            "currency":"USD",
            "main_airline":None if not flights else flights[0]["__main_airline"],
            "flights": flights
        }

    results = map(parse_proposal, g.css_list('.result-list>li'))

    return results


def main():
    request = {
       "origin_iata":'SYD',
       "destination_iata":'Los Angeles',
       "depart_date":'2012-04-26',
       "return_date":'2012-04-29',
       "adults":'1',
       "children":'0',
       "infants":'0',
       "trip_class":'ECONOMY',
       "range":None
   }

    content = search_results_content(request)

    response = page_results(request, content)
    print response

if __name__ == "__main__":
    main()

