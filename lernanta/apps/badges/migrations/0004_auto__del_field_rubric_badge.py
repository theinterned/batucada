# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Rubric.badge'
        db.delete_column('badges_rubric', 'badge_id')

        # Adding M2M table for field rubrics on 'Badge'
        db.create_table('badges_badge_rubrics', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('badge', models.ForeignKey(orm['badges.badge'], null=False)),
            ('rubric', models.ForeignKey(orm['badges.rubric'], null=False))
        ))
        db.create_unique('badges_badge_rubrics', ['badge_id', 'rubric_id'])


    def backwards(self, orm):
        
        # Adding field 'Rubric.badge'
        db.add_column('badges_rubric', 'badge', self.gf('django.db.models.fields.related.ForeignKey')(default=datetime.date(2011, 9, 24), to=orm['badges.Badge']), keep_default=False)

        # Removing M2M table for field rubrics on 'Badge'
        db.delete_table('badges_badge_rubrics')


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
