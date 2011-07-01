# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting model 'FeedEntry'
        db.delete_table('dashboard_feedentry')


    def backwards(self, orm):
        
        # Adding model 'FeedEntry'
        db.create_table('dashboard_feedentry', (
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('checksum', self.gf('django.db.models.fields.CharField')(max_length=32, unique=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dashboard', ['FeedEntry'])


    models = {
        
    }

    complete_apps = ['dashboard']
