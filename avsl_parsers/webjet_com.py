#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os

import re
from grab import Grab
from lxml import etree
import datetime

import time, urllib

if __name__ == "__main__":
    script_path = os.path.realpath(__file__)
    sys.path.append(os.path.normpath(os.path.dirname(script_path) + "/../utils"))
    import utils
    import ptime
else:
    from utils import utils
    from utils import ptime

# перенаправляем стандартный вывод в лог файл
utils.redirect_stdout('webjet.com')


def parse(queue):
    print "start.."
    request = queue.get()
    response = page_results(request, search_results_content(request))
    queue.put({ 'success': True, 'flags':[], 'response':response })
    print "finish..."

def search_results_content(request):

    g = Grab(reuse_cookies = True, reuse_referer=True)

    request = request.copy()

    one_way = False

    if not request.get("return_date", False):
        one_way = True
        request["return_date"] = request["depart_date"]

    request["depart_date"] = ptime.input2mdY(request["depart_date"])
    request["return_date"] = ptime.input2mdY(request["return_date"])

    g.setup(post = {
        'EntryPoint':	'Flight',
        'RequestFrom':	'Outside',
        'TripType': 'rdbOneWay' if one_way else 'rdbRoundTrip',
        'WebSiteId':	'189',
        'arrival_label':	request['destination_iata'],
        'btnSubmitAir':	'Search for flights',
        'ddlCabin':	'Y',
        'ddlPaxADT':	request['adults'],
         'ddlPaxCHD':	request['children'],
        'ddlPaxINF':	request['infants'],
        'departure_label':	request['origin_iata'],
        'flight_search_action':	'http://res.webjet.com/process.aspx',
        'txtArrCity1':	request['destination_iata'],
        'txtArrCity2':	request['origin_iata'],
        'txtDepCity1':	request['origin_iata'],
        'txtDepCity2':	request['destination_iata'],
        'txtdate1': request["depart_date"],
        'txtdate2': request["return_date"]
    })

    print 'request post data'
    g.setup(user_agent = "Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0")
    g.go("http://res.webjet.com/process.aspx?agentid=189&" +
         "txtDepCity1=" + request['origin_iata'] +
         "&txtArrCity1=" + request['destination_iata'] +
         "&TripType=" + ("rdbOneWay" if one_way else "rdbRoundTrip") +
         "&txtDate1=" + request["depart_date"] +
         "&txtDate2=" + request["return_date"] +
         "&txtDepCity2=" + request['destination_iata'] +
         "&txtArrCity2=" + request['origin_iata'] +
         "&ddlPaxADT=" + request['adults'] +
         "&ddlPaxCHD=" + request['children'] +
         "&ddlPaxINF=" + request['infants']
    )

    print 'check cookie'
    if not g.response.cookies.get("ASP.NET_SessionId", False):
        print "not auth"
        sys.exit(0)

    print 'response body length=', len(g.response.body)
    print 'response headers length=', g.response.headers

    print 'check location'
    loc = g.response.headers.get("Location")
    if not loc or loc.find("result=nothing") >= 0:
        print "not results"
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

    print 'waiting...'

    while True:
        g.setup(post= {
            "scp": "updServer|timeControl",
            "Destination_airport": "bkk/", #request["destination_iata"].upper() + "/",
            "Destination_country": "TH/", #_dc,
            "Origin_airport":  "syd/", #request["origin_iata"].upper() + "/",
            "Origin_country": "AU", #_oc,
            "Departure_date": request["depart_date"] + "/",
            "__EVENTTARGET": "timeControl",
            "__EVENTARGUMENT": "",
            "__VIEWSTATE": _vs,
            "__ASYNCPOST": "true"
        })
        g.go("http://res.webjet.com" + loc)

        if i == 9:
            break

        if re.search(re.compile('pageRedirect'), g.response.body):
            status = True
            break

        time.sleep(1)
        i += 1

    print 'check status'
    if not status:
        return False

    print 'prices request'
    g.setup(user_agent="User-Agent	Mozilla/5.0 (Ubuntu; X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0")
    g.go("http://res.webjet.com/prices.aspx?page=flightprices&air=Air&id1=" + urllib.quote(id1, ''))

    print "Response Body Length: ", len(g.response.body)

    return g.response.body


def page_results(request, content):
    g =  Grab()
    g.response.body = content

    print "start parsing..."

    # Example: <li><strong>Departure Time</strong> - 8:55 PM</li>
    flight_field_pattern = re.compile('<li><strong>[^<]+</strong> - ([^<]+)</li>')
    # Example: Sydney, Nsw (SYD) to Kuala Lumpur (KUL) May 8, 2012
    origin_destination_pattern = re.compile('[^\(]+ \(([^\)]+)\) [^\(]+ \(([^\)]+)\).*')
    # Example: <td id="paxAdtTd">1</td><td>$1296.87</td>
    total_propasal_price = re.compile('<td id="paxAdtTd">[^<]*</td><td>\\$([^<]+)</td>')

    # operation_airline = main airline, airline = airline

    def parse_flight(e, route_leg):
        g0 = Grab()
        g0.response.body = etree.tostring(e)

        results = []
        offset_days = 0
        for f0 in g0.xpath_list('./li'):

            g = Grab()
            g.response.body = etree.tostring(f0)

            f = g.css_list('ul>li')

            def ff(index):
                return re.match(flight_field_pattern, etree.tostring(f[index])).group(1)

            h = re.match(origin_destination_pattern, g.css_text('h5'))
            def hh(index):
                return h.group(index)

            arrival_pattern_plus_day = re.compile('(\d+:\d+ [AP]M) \\+ (\d+) [dD]ay')

            if route_leg:
                base_date = request["return_date"]
            else:
                base_date = request["depart_date"]

            departure = ptime.get_full_date(str(base_date), ff(2))
            departure += datetime.timedelta(days = offset_days)

            arrival_time = ff(3)
            arrival_date = ptime.get_date(base_date)
            arrival_plus_day = re.match(arrival_pattern_plus_day, arrival_time.strip())
            if arrival_plus_day:
                offset_days += 1
                arrival_time = arrival_plus_day.group(1)
            arrival_date += datetime.timedelta(days = offset_days)
            arrival = ptime.get_full_date(arrival_date, arrival_time)

            def sep_number(s):
                r = re.match(re.compile('([\w\d][\w\d])(\d+)'), str(s))
                return r.group(1), r.group(2)

            airline, number = sep_number(ff(5))

            results.append({
                "number":number,
                "airline":airline, #ff(4),
                "origin":hh(1),
                "destination":hh(2),
                "departure":ptime.response_date(departure),
                "arrival":ptime.response_date(arrival),
                "duration":None, #ptime.str_timedelta(departure, arrival),
                "route_leg":str(int(route_leg)) ,
                "aircraft":None,
                "__main_airline":airline, #ff(4)
            })

        return results



    def parse_proposal(e):
        try:
            global proposal_count
            print "start parse proposals #" + str(proposal_count)
            proposal_count += 1
            g = Grab()
            g.response.body = etree.tostring(e)
            flights = []
            departing = True
            for v in g.css_list('.info>.info>.clearfix'):
                flight = parse_flight(v, not departing)
                flights.extend(flight)
                departing = False

            print flights
            return {
                "total":re.search(total_propasal_price,etree.tostring(g.css('#paxAdtTd').find('..'))).group(1),
                "currency":"AUD",
                "main_airline":None if not flights else flights[0]["__main_airline"],
                "flights": flights
            }
        except Exception:
            return None

    list = g.css_list('.result-list>li')
    results = []
    for e in list:
        proposal = parse_proposal(e)
        if proposal:
            results.append(proposal)

    return results

proposal_count = 0

def main():

    request = {
       "origin_iata":'SYD',
       "destination_iata":'BKK',
       "depart_date":'2012-05-26',
       "return_date":'2012-05-29',
       "adults":'1',
       "children":'0',
       "infants":'0',
       "trip_class":'ECONOMY',
       "range":None
    }

    content = search_results_content(request)

    response = page_results(request, content)

if __name__ == "__main__":
    main()

