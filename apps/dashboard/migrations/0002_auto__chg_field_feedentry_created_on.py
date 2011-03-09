# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'FeedEntry.created_on'
        db.alter_column('dashboard_feedentry', 'created_on', self.gf('django.db.models.fields.DateTimeField')())


    def backwards(self, orm):
        
        # Changing field 'FeedEntry.created_on'
        db.alter_column('dashboard_feedentry', 'created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))


    models = {
        'dashboard.feedentry': {
            'Meta': {'object_name': 'FeedEntry'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'checksum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['dashboard']
