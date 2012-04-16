#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

import httplib
import boot

class BaseHandler(tornado.web.RequestHandler):
    def error_response(self, status_code, message):
        self.set_status(status_code)
        error_message = httplib.responses[status_code] + ': ' + str(message).capitalize()
        boot.logger.error(error_message)
        self.write(boot.failed_xml_response(error_message))

class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello, world")

class ProposalsHandler(BaseHandler):
    def get(self, proposal_id=None):
        self.set_header("Content-Type", "text/xml")
        if proposal_id is None:
            host_name = self.get_argument('host')

            request = {
                "origin_iata":None,
                "destination_iata":None,
                "depart_date":None,
                "return_date":None,
                "adults":None,
                "children":None,
                "infants":None,
                "trip_class":None,
                "range":None
            }

        #    request = {
        #        "origin_iata":'SYD',
        #        "destination_iata":'Los Angeles',
        #        "depart_date":'2012-04-26',
        #        "return_date":'2012-04-29',
        #        "adults":'1',
        #        "children":'0',
        #        "infants":'0',
        #        "trip_class":'ECONOMY',
        #        "range":None
        #    }

            for key in request.keys():
                request[key] = self.get_argument(key)

            response, obj = boot.run_parse(host_name, request)
            if not response:
                # сервер не может запустить парсер
                return self.error_response(500, str(obj))

            if not boot.check_response(host_name, obj):
                # записываем сообщение об ошибке в логи и возвращаем в теле ответа
                return self.error_response(500, "Invalid parser response format")

            try:
                # формируем xml ответ
                response = boot.successful_xml_response(obj)
            except Exception, e:
                # ошибка формирования успешного xml ответа
                self.error_response(500, 'Error is the formation of a successful response xml! ' + str(e))
            else:
                # выводим в теле ответ и пишем в лог об успешном парсинге
                boot.logger.info('Successful Response For "%s" Host (Content-Length: %d)' % (host_name, len(response)))
                self.write(response)

        else:
            print("/proposals/:proposal_id.xml\n")

class RunTestHandler(BaseHandler):
    def get(self):
        if boot.run_parse(self.get_argument('h'), {}) is False:
            self.write("FAILED EXECUTION!!!")
        self.write('DONE')

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/proposals\/?\.xml", ProposalsHandler),
        (r"/proposals/([0-9]+)\/?\.xml", ProposalsHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
