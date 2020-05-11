# -*- coding: utf-8 -*-
import logging
import json
import datetime
import socket,platform,os,re

class HostIp:
    host_name = None
    host_ip = None

    @classmethod
    def get_host_ip(cls):
        if not cls.host_name or not HostIp.host_ip:
            try:
                if platform.system() == 'Windows':
                    cls.host_name = socket.gethostname()
                    cls.host_ip = socket.gethostbyname(cls.host_name)
                elif platform.system() == 'Linux':
                    csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    csock.connect(('8.8.8.8', 80))
                    (addr, port) = csock.getsockname()
                    csock.close()
                    cls.host_name = socket.gethostname()
                    cls.host_ip = addr
            except ConnectionError:
                cls.host_name = "unknown hostname"
                cls.host_ip = "unknown ip"
        return cls.host_name, cls.host_ip


REMOVE_ATTR = ["filename", "module", "exc_text", "stack_info", "created", "msecs", "relativeCreated", "exc_info", "msg", "args"]


import inspect
class JSONFormatter(logging.Formatter):
    service="gongzhonghao-1.0.2"

    host_name, host_ip = HostIp.get_host_ip()

    def format(self, record):
        extra = self.build_record(record)

        extra["logger_name"] = extra.pop("name")
        self.set_host_ip(extra)
        self.set_service(extra)

        if isinstance(record.msg, dict):
            extra['data'] = record.msg
        else:
            if record.args:
                extra['msg'] = "'" + record.msg + "'," + str(record.args).strip('()')
            else:
                extra['msg'] = record.msg
        if record.exc_info:
            extra['exc_info'] = self.formatException(record.exc_info)
        if self._fmt == 'pretty':
            return json.dumps(extra, indent=1, ensure_ascii=False)
        else:
            return json.dumps(extra, ensure_ascii=False)

    @classmethod
    def build_record(cls, record):
        return {
            attr_name: record.__dict__[attr_name]
            for attr_name in record.__dict__
            if attr_name not in REMOVE_ATTR
        }

    @classmethod
    def set_format_time(cls, extra):
        now = datetime.datetime.now()
        format_time = now.strftime("%Y-%m-%dT%H:%M:%S" + ".%03d" % (now.microsecond / 1000) + "Z")
        extra['@timestamp'] = format_time
        return format_time

    @classmethod
    def set_host_ip(cls, extra):
        extra['host_name'] = JSONFormatter.host_name
        extra['host_ip'] = JSONFormatter.host_ip


    @classmethod
    def set_service(cls, extra):
        extra['service'] = cls.service
