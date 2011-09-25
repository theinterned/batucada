# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding M2M table for field prerequisites on 'Badge'
        db.create_table('badges_badge_prerequisites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_badge', models.ForeignKey(orm['badges.badge'], null=False)),
            ('to_badge', models.ForeignKey(orm['badges.badge'], null=False))
        ))
        db.create_unique('badges_badge_prerequisites', ['from_badge_id', 'to_badge_id'])


    def backwards(self, orm):
        
        # Removing M2M table for field prerequisites on 'Badge'
        db.delete_table('badges_badge_prerequisites')


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
            'prerequisites': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['badges.Badge']", 'null': 'True', 'blank': 'True'}),
            'rubrics': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'rubrics'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['badges.Rubric']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '110', 'db_index': 'True'})
        },
        'badges.rubric': {
            'Meta': {'object_name': 'Rubric'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['badges']
