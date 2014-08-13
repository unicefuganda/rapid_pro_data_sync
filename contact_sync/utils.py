from django.conf import settings
import psycopg2

__author__ = 'kenneth'


class UreportContact(object):
    pass


class UreportApp(object):
    def __init__(self, app_name):
        ureport_app = getattr(settings, 'UREPORT_APP')[app_name]
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