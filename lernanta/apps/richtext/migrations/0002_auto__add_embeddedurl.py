# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'EmbeddedUrl'
        db.create_table('richtext_embeddedurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('original_url', self.gf('django.db.models.fields.URLField')(max_length=1023)),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('extra_data', self.gf('richtext.models.JSONField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('richtext', ['EmbeddedUrl'])


    def backwards(self, orm):
        
        # Deleting model 'EmbeddedUrl'
        db.delete_table('richtext_embeddedurl')


    models = {
        'richtext.embeddedurl': {
            'Meta': {'object_name': 'EmbeddedUrl'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('richtext.models.JSONField', [], {}),
            'html': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'original_url': ('django.db.models.fields.URLField', [], {'max_length': '1023'})
        }
    }

    complete_apps = ['richtext']
