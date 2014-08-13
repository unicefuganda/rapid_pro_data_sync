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
                      '"rapidsms_contact"."gender", "rapidsms_contact"."village_name",' \
                      'FROM "rapidsms_contact" WHERE "rapidsms_contact"."id" = %d'

    def get_connections(self, app):
        cur = app.connect().cursor()
        cur.excute(self.GET_CONNECTIONS_SQL % self.last_pk)
        return cur.fetchall()

    def get_contacts(self, app):
        contacts = []
        for row in self.get_connections(app):
            q = {'phone': row[0]}
            contact_pk = row[1]
            cur = app.connect().cursor()
            cur.excute(self.GET_CONTACT_SQL % contact_pk)
            c = cur.fetchone()
            q.update({'name': c[0]})
            fields = {'language': c[1], 'occupation': c[2], 'birth_date': c[5], 'gender': c[6], 'village_name': c[7],
                      'joined_ureport': row[2], 'id': row[3]}
            q['fields'] = fields
            contacts.append(q)
        return contacts

    def post_request(self, app, contact):
        URL = 'https://api.rapidpro.io/api/v1/contacts.json'
        response = requests.post(URL, data=contact,
                                 headers={'Content-type': 'application/json', 'Authorization': 'Token %s' % app.token})
        return response.json

    def sync(self):
        app = UreportApp(self.app_name)
        contacts = self.get_contacts(app)
        for contact in contacts:
            _contact = json.dumps(contact)
            response = self.post_request(app, _contact)
            if not response == _contact:
                print "Connection with phone: %s not synced" % contact['phone']
                #Todo Handle this scenario
        self.last_pk = contact['field']['id']
        self.save()