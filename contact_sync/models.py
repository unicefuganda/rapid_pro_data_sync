import json
from django.db import models
import psycopg2.extras
import requests
import time
from contact_sync.utils import UreportApp, DateEncoder


class Sync(models.Model):
    app_name = models.CharField(max_length=100)
    last_pk = models.IntegerField()
    last_sync = models.DateTimeField(auto_now=True)
    first_sync = models.DateTimeField(auto_now_add=True)

    GET_CONNECTIONS_SQL = 'SELECT "rapidsms_connection"."identity", "rapidsms_connection"."contact_id", ' \
                          '"rapidsms_connection"."created_on", "rapidsms_connection"."id"' \
                          'FROM "rapidsms_connection" WHERE "rapidsms_connection"."id" > %d  ' \
                          'ORDER BY "rapidsms_connection"."id" ASC'

    GET_GROUPS_SQL = 'SELECT "auth_group"."name" FROM "auth_group" INNER JOIN "rapidsms_contact_groups" ON ' \
                     '("auth_group"."id" = "rapidsms_contact_groups"."group_id") ' \
                     'WHERE "rapidsms_contact_groups"."contact_id" = %d'

    def _generate_contact_sql(self, contact_pk):
        sql = 'SELECT "rapidsms_contact"."reporting_location_id"'
        for v in self.app.contact_fields.values():
            sql += ', "rapidsms_contact"."%s"' % v
        sql += ' FROM "rapidsms_contact" WHERE "rapidsms_contact"."id" = %d' % contact_pk
        return sql

    def get_connections(self):
        cur = self.app.connect().cursor()
        cur.execute(self.GET_CONNECTIONS_SQL % self.last_pk)
        return cur.fetchall()

    def get_groups(self, contact_pk):
        cur = self.app.connect().cursor()
        cur.execute(self.GET_GROUPS_SQL % contact_pk)
        return [x[0] for x in cur.fetchall()]

    def get_contact(self, row):
        q = {'phone': "+"+row[0]}
        contact_pk = row[1]
        print "Contact Pk ===>  ", contact_pk
        if not contact_pk:
            return None
        cur = self.app.connect().cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(self._generate_contact_sql(contact_pk))
        c = dict(cur.fetchone())
        q.update({'name': c.pop('name')})
        fields = {}
        for k, v in self.app.contact_fields.items():
            try:
                if c[v] == None:
                    fields[k] = " "
                else:
                    fields[k] = c[v]
            except KeyError as e:
                #Name is taken out of results dict so it will always raise a key error so I'll just pass
                pass
        q['fields'] = fields
        q['groups'] = self.get_groups(contact_pk)
        return q

    def push_contacts(self, rate_limit=0):
        for row in self.get_connections():
            x = self.get_contact(row)
            if not x:
                continue
            q = x
            _q = json.dumps(q, cls=DateEncoder)
            print _q
            print _q
            response = self.post_request(_q)
            if not 'modified_on' in json.loads(response.text):
                print "Response: %s" % response.text
                print "Request: %s" % _q
                print "Connection with phone: %s not synced" % q['phone']
            if rate_limit:
                time.sleep(rate_limit)
        self.last_pk = q['field']['id']
        self.save()

    def post_request(self, contact):
        URL = 'https://api.rapidpro.io/api/v1/contacts.json'
        response = requests.post(URL, data=contact,
                                 headers={'Content-type': 'application/json',
                                          'Authorization': 'Token %s' % self.app.token})
        return response

    def sync(self, rate_limit):
        self.app = UreportApp(self.app_name)
        self.push_contacts(rate_limit=rate_limit)