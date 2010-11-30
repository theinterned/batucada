# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Relationship'
        db.create_table('relationships_relationship', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='source_relationships', to=orm['contenttypes.ContentType'])),
            ('source_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('target_content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name='target_relationships', to=orm['contenttypes.ContentType'])),
            ('target_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('relationships', ['Relationship'])

        # Adding unique constraint on 'Relationship', fields ['source_content_type', 'target_content_type', 'source_object_id', 'target_object_id']
        db.create_unique('relationships_relationship', ['source_content_type_id', 'target_content_type_id', 'source_object_id', 'target_object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Relationship', fields ['source_content_type', 'target_content_type', 'source_object_id', 'target_object_id']
        db.delete_unique('relationships_relationship', ['source_content_type_id', 'target_content_type_id', 'source_object_id', 'target_object_id'])

        # Deleting model 'Relationship'
        db.delete_table('relationships_relationship')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source_relationships'", 'to': "orm['contenttypes.ContentType']"}),
            'source_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'target_content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target_relationships'", 'to': "orm['contenttypes.ContentType']"}),
            'target_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['relationships']
