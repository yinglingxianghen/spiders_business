import logging.config
import os

from .json_formatter import JSONFormatter

log_schedule = logging.getLogger(__name__)
log_schedule.setLevel(logging.DEBUG)

# write log to file
handler_schedule = logging.FileHandler(os.path.dirname(os.path.abspath('.')) + r'/crawlframe/logs/schedule.log')
handler_schedule.setLevel(logging.INFO)
# write log to console
handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)
# set formatter
handler_schedule.setFormatter(JSONFormatter())
handler_console.setFormatter(JSONFormatter("pretty"))
# add handler
log_schedule.addHandler(handler_schedule)
log_schedule.addHandler(handler_console)