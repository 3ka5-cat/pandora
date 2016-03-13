#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import tornado.ioloop
from tornado.options import options
from tornado_json.routes import get_routes
from tornado_json.application import Application
from conf import settings, db
import handlers


def main():
    routes = get_routes(handlers)

    application = Application(routes=routes, settings=settings, db_conn=db)
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
