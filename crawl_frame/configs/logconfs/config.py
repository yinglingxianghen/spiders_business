# -*- coding: utf-8 -*-
import logging
import os

from json_formatter import JSONFormatter

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# write log to file
handler = logging.FileHandler(os.path.dirname(os.path.abspath('.')))
handler.setLevel(logging.INFO)
# write log to console

handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
# set formatter

handler.setFormatter(JSONFormatter())
handler_console.setFormatter(JSONFormatter("pretty"))
# add handler

log.addHandler(handler)
log.addHandler(handler_console)
