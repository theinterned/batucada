# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Relationship.created_on'
        db.add_column('relationships_relationship', 'created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2010, 11, 29), auto_now_add=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Relationship.created_on'
        db.delete_column('relationships_relationship', 'created_on')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'relationships.relationship': {
            'Meta': {'unique_together': "(('source_content_type', 'target_content_type', 'source_object_id', 'target_object_id'),)", 'object_name': 'Relationship'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.date(2010, 11, 29)', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_relationships'", 'to': "orm['contenttypes.ContentType']"}),
            'source_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target_relationships'", 'to': "orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['relationships']
