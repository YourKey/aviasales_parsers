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
import hash
import click

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

    def get_list(self):
        hostname = self.get_argument('host')

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

        for key in request.keys():
            request[key] = self.get_argument(key)

        response, obj = boot.run_parse(hostname, request)
        if not response:
            # сервер не может запустить парсер
            return self.error_response(500, str(obj))

        if not boot.check_response(hostname, obj):
            # записываем сообщение об ошибке в логи и возвращаем в теле ответа
            return self.error_response(500, "Invalid parser response format")

        if not obj or len(obj) == 0:
            # выдаем 400 bad request если нет выходных данных
            self.error_response(400, 'No result available try another search...')
            return

        try:
            # производим хеширование успешного ответа
            hashable_list = []
            for i, v in enumerate(obj):
                hashable = dict()
                hashable["hostname"] = hostname
                hashable["request"] = request
                hashable["proposal"] = obj[i].copy()
                hashable["index"] = i
                hashable_list.append(hashable)
            print hashable_list
            ids = hash.set_each('avsl_proposals', hashable_list)

            if not ids:
                raise hash.WriteException('hashing failed - key list is empty')

            for i, v in enumerate(obj):
                obj[i]['id'] = ids[i]

            # формируем xml ответ
            response = boot.successful_xml_response(obj)
        except hash.WriteException, e:
            self.error_response(500, 'Ошибка записи данных в хеш! ' + str(e))
            return
        except Exception, e:
            # ошибка формирования успешного xml ответа
            self.error_response(500, 'Error the formation of a successful response xml! ' + str(e))
            return
        else:
            # выводим в теле ответ и пишем в лог об успешном парсинге
            boot.logger.info('Successful Response For "%s" Host (Content-Length: %d)' % (hostname, len(response)))
            self.write(response)

    def get_issue(self, proposal_id):
        origin = hash.get('avsl_proposals', proposal_id)
        if not origin:
            self.error_response(404, "proposal by id #%d not found" % int(proposal_id))
            return

        obj = hash.decode_dict(origin)
        info = click.url_info(obj["hostname"], obj)

        if not info:
            self.error_response(404, "domain %s cannot generate click url" % obj["hostname"])
            return

        self.write(boot.click_xml_response(info))

    def get(self, proposal_id=None):
        self.set_header("Content-Type", "text/xml")
        if proposal_id is None:
            self.get_list()
        else:
            self.get_issue(proposal_id)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/proposals\/?\.xml", ProposalsHandler),
        (r"/proposals/(\d+)\/?\.xml", ProposalsHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
