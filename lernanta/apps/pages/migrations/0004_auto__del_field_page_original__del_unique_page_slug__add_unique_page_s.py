# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Page', fields ['slug']
        db.delete_unique('pages_page', ['slug'])

        # Deleting field 'Page.original'
        db.delete_column('pages_page', 'original_id')

        # Adding unique constraint on 'Page', fields ['slug', 'language']
        db.create_unique('pages_page', ['slug', 'language'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Page', fields ['slug', 'language']
        db.delete_unique('pages_page', ['slug', 'language'])

        # Adding field 'Page.original'
        db.add_column('pages_page', 'original', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pages.Page'], null=True), keep_default=False)

        # Adding unique constraint on 'Page', fields ['slug']
        db.create_unique('pages_page', ['slug'])


    models = {
        'pages.page': {
            'Meta': {'unique_together': "(('slug', 'language'),)", 'object_name': 'Page'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '16'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '110', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['pages']
