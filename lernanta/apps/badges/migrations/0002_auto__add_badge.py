# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Badge'
        db.create_table('badges_badge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=225)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=110, db_index=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=225)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, null=True, blank=True)),
            ('criteria', self.gf('django.db.models.fields.CharField')(max_length=225)),
            ('assessment_type', self.gf('django.db.models.fields.CharField')(default='self', max_length=30, null=True)),
            ('badge_type', self.gf('django.db.models.fields.CharField')(default='completion/aggregate', max_length=30, null=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('badges', ['Badge'])


    def backwards(self, orm):
        
        # Deleting model 'Badge'
        db.delete_table('badges_badge')


    models = {
        'badges.badge': {
            'Meta': {'object_name': 'Badge'},
            'assessment_type': ('django.db.models.fields.CharField', [], {'default': "'self'", 'max_length': '30', 'null': 'True'}),
            'badge_type': ('django.db.models.fields.CharField', [], {'default': "'completion/aggregate'", 'max_length': '30', 'null': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'criteria': ('django.db.models.fields.CharField', [], {'max_length': '225'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '225'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '225'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '110', 'db_index': 'True'})
        }
    }

    complete_apps = ['badges']
