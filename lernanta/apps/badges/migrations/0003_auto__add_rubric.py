# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Rubric'
        db.create_table('badges_rubric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('badge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.Badge'])),
        ))
        db.send_create_signal('badges', ['Rubric'])


    def backwards(self, orm):
        
        # Deleting model 'Rubric'
        db.delete_table('badges_rubric')


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
        },
        'badges.rubric': {
            'Meta': {'object_name': 'Rubric'},
            'badge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.Badge']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['badges']
