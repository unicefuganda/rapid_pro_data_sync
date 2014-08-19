RapidPro Data Sync
===================

Syncing data from rapidsms ureport to rapidpro ureport(Migration) 

Configuration
=============

Add this config to **UREPORT_APPS** setting

UREPORT_APPS = {

    'ureport': {
    
        'TOKEN': 'API_TOKEN',
        
        'ENGINE': 'psycopg2',
        
        'NAME': 'ureport',
        
        'HOST': 'localhost',
        
        'USER': 'postgres',
        
        'contact_fields': {
        
            'Name': 'name',
            
            'Language': 'language',
            
            'Occupation': 'occupation',
            
            'Created On': 'created_on',
            
            'Birth Date': 'birthdate',
            
            'Gender': 'gender',
            
            'Village Name': 'village_name'
            
        }
        
    }
    
}


Execution
=========

Run *python manage.py push_to_rapidpro --app=app_name --rate=10*

app_name = One of the UREPORT_APPS in the config above

rate = (int) Number of seconds to sleep before making another hit on the rapidpro server