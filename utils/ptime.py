#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

def get_date(str):
    return datetime.datetime.strptime(str, '%Y-%m-%dT%H:%M:%S' if "T" in str else '%Y-%m-%d')

def get_ampm_time(str):
    return datetime.datetime.strptime(str, '%I:%M %p').timetz()

def get_full_date(date, time):
    return datetime.datetime.combine(
        get_date(date) if type(date) is str else date,
        get_ampm_time(time) if type(time) is str else time
    )

def response_date(date):
    return date.strftime('%Y-%m-%dT%H:%M:%S')

def str_timedelta(b, e):
    b = datetime.datetime.strptime(b, '%Y-%m-%d %H:%M:%S') if type(b) == str else b
    e = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M:%S') if type(e) == str else e
    return (e-b).seconds

def input2mdY(date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    return date.strftime("%m/%d/%Y")

