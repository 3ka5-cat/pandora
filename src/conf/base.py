# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import tornado
from tornado.options import define

from motor import MotorClient


define("port", default=8000, help="run on the given port", type=int)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")
tornado.options.parse_command_line()

uri = "mongodb://localhost:27017/pandora"
client = MotorClient(uri, tz_aware=True)
db = client.get_default_database()

settings = {
}