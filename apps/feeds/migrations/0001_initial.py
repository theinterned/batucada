# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeedEntry'
        db.create_table('feeds_feedentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('page', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('checksum', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('feeds', ['FeedEntry'])


    def backwards(self, orm):
        
        # Deleting model 'FeedEntry'
        db.delete_table('feeds_feedentry')


    models = {
        'feeds.feedentry': {
            'Meta': {'object_name': 'FeedEntry'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'checksum': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'page': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['feeds']
