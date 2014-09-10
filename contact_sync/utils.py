import json
from datetime import date
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import psycopg2

__author__ = 'kenneth'


class MissingArgumentError(Exception):
    pass


class DateEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%dT%H:%M:%S.%s%Z')
        if obj == None:
            return "Empty Field"
        if str(obj).isdigit():
            return '+%s' % str(obj)
        return json.JSONEncoder.default(self, obj)


class UreportApp(object):
    def __init__(self, app_name):
        try:
            ureport_app = getattr(settings, 'UREPORT_APPS')[app_name]
        except KeyError:
            raise ImproperlyConfigured(
                "You must configure source ureport app in setting attribute UREPORT_APPS, See README.md file")
        for k, v in ureport_app.items():
            setattr(self, k.lower(), v)

    def connect(self):
        if self.engine == 'psycopg2':
            try:
                conn = psycopg2.connect("dbname='%s' user='%s' host='%s'" % (self.name, self.user, self.host))
                return conn
            except Exception as e:
                print "I am unable to connect to the database"
                print e
        else:
            print "Adaptor not supported"