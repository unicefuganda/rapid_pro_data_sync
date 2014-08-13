RapidPro Data Sync
===================

Syncing data from rapidsms ureport to rapidpro ureport(Migration) 

Configuration
=============

Add this config to UREPORT_APPS setting

UREPORT_APPS = {
    'ureport': {
         'TOKEN': 'API_TOKEN',
         'ENGINE': 'psycopg2',
         'NAME': 'ureport',
         'HOST': 'localhost',
         'USER': 'postgres',
    }
}
