import json
from django.db import models
import requests
from contact_sync.utils import UreportApp


class Sync(models.Model):
    app_name = models.CharField(max_length=100)
    last_pk = models.IntegerField()
    last_sync = models.DateTimeField(auto_now=True)
    first_sync = models.DateTimeField(auto_now_add=True)

    GET_CONNECTIONS_SQL = 'SELECT "rapidsms_connection"."identity", "rapidsms_connection"."contact_id", ' \
                          '"rapidsms_connection"."created_on", "rapidsms_connection"."id"' \
                          'FROM "rapidsms_connection" WHERE "rapidsms_connection"."id" > %d  ' \
                          'ORDER BY "rapidsms_connection"."id" ASC'

    GET_CONTACT_SQL = 'SELECT "rapidsms_contact"."name", "rapidsms_contact"."language", ' \
                      '"rapidsms_contact"."occupation", "rapidsms_contact"."created_on",' \
                      ' "rapidsms_contact"."reporting_location_id", "rapidsms_contact"."birthdate", ' \
                      '"rapidsms_contact"."gender", "rapidsms_contact"."village_name"' \
                      'FROM "rapidsms_contact" WHERE "rapidsms_contact"."id" = %d'

    GET_GROUPS_SQL = 'SELECT "auth_group"."name" FROM "auth_group" INNER JOIN "rapidsms_contact_groups" ON ' \
                     '("auth_group"."id" = "rapidsms_contact_groups"."group_id") ' \
                     'WHERE "rapidsms_contact_groups"."contact_id" = %d'

    def get_connections(self, app):
        cur = app.connect().cursor()
        cur.execute(self.GET_CONNECTIONS_SQL % self.last_pk)
        return cur.fetchall()

    def get_groups(self, app, contact_pk):
        cur = app.connect().cursor()
        cur.execute(self.GET_GROUPS_SQL % contact_pk)
        return [x[0] for x in cur.fetchall()]

    def get_and_push_contacts(self, app):
        for row in self.get_connections(app):
            q = {'phone': row[0]}
            contact_pk = row[1]
            cur = app.connect().cursor()
            cur.execute(self.GET_CONTACT_SQL % contact_pk)
            c = cur.fetchone()
            q.update({'name': c[0]})
            fields = {'language': c[1], 'occupation': c[2], 'birth_date': c[5], 'gender': c[6], 'village_name': c[7],
                      'id': row[3]}
            q['fields'] = fields
            q['groups'] = self.get_groups(app, contact_pk)
            q = json.dumps(q)
            print q
            response = self.post_request(app, q)
            if not response == q:
                print "Connection with phone: %s not synced" % q['phone']
        self.last_pk = q['field']['id']
        self.save()

    def post_request(self, app, contact):
        URL = 'https://api.rapidpro.io/api/v1/contacts.json'
        response = requests.post(URL, data=contact,
                                 headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % app.token})
        return response.json

    def sync(self):
        app = UreportApp(self.app_name)
        self.get_and_push_contacts(app)