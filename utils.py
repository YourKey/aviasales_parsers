# -*- coding: utf-8 -*-
__author__ = 'vit'

import sys, os
import datetime
import subprocess

PARSER_LOG_DIRECTORY = 'logs/parsers'

def redirect_stdout(host_name):
    dir = PARSER_LOG_DIRECTORY + '/' + host_name
    if not os.path.exists(dir):
        os.makedirs(dir)
    sys.stdout = open(dir + '/' + str(datetime.datetime.now().date()) + ".log", "at")

def run_php_script(path_to_script, request):
    p = subprocess.Popen('php ' + path_to_script + ' "' + request + '"',
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''
    for line in p.stdout.readlines():
        output+=line
    p.wait()
    return output

DEBUG_LOGGING = True

def log(message):
    time = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    if type(message) == str:
        print time + ' - ' + message
    else:
        print time
        print message

def debug(message):
    if DEBUG_LOGGING:
        log(message)
