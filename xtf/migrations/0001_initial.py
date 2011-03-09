# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GeoPoint'
        db.create_table('xtf_geopoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('lat', self.gf('django.db.models.fields.FloatField')(default=37.808690599999998)),
            ('lon', self.gf('django.db.models.fields.FloatField')(default=-122.2675416)),
            ('place', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('exact', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('xtf', ['GeoPoint'])

        # Adding unique constraint on 'GeoPoint', fields ['object_id', 'content_type']
        db.create_unique('xtf_geopoint', ['object_id', 'content_type_id'])

        # Adding model 'DublinCoreTerm'
        db.create_table('xtf_dublincoreterm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('term', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('qualifier', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('xtf', ['DublinCoreTerm'])

        # Adding model 'ARKObject'
        db.create_table('xtf_arkobject', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ark', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('xtf', ['ARKObject'])

        # Adding model 'ARKSet'
        db.create_table('xtf_arkset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('public', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('markup', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('xtf', ['ARKSet'])

        # Adding model 'ARKSetMember'
        db.create_table('xtf_arksetmember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xtf.ARKSet'])),
            ('object', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['xtf.ARKObject'])),
            ('annotation', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('xtf', ['ARKSetMember'])

        # Adding unique constraint on 'ARKSetMember', fields ['set', 'object']
        db.create_unique('xtf_arksetmember', ['set_id', 'object_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ARKSetMember', fields ['set', 'object']
        db.delete_unique('xtf_arksetmember', ['set_id', 'object_id'])

        # Removing unique constraint on 'GeoPoint', fields ['object_id', 'content_type']
        db.delete_unique('xtf_geopoint', ['object_id', 'content_type_id'])

        # Deleting model 'GeoPoint'
        db.delete_table('xtf_geopoint')

        # Deleting model 'DublinCoreTerm'
        db.delete_table('xtf_dublincoreterm')

        # Deleting model 'ARKObject'
        db.delete_table('xtf_arkobject')

        # Deleting model 'ARKSet'
        db.delete_table('xtf_arkset')

        # Deleting model 'ARKSetMember'
        db.delete_table('xtf_arksetmember')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'xtf.arkobject': {
            'Meta': {'object_name': 'ARKObject'},
            'ark': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'xtf.arkset': {
            'Meta': {'object_name': 'ARKSet'},
            'ark_objects': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['xtf.ARKObject']", 'through': "orm['xtf.ARKSetMember']", 'symmetrical': 'False'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'xtf.arksetmember': {
            'Meta': {'unique_together': "(('set', 'object'),)", 'object_name': 'ARKSetMember'},
            'annotation': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['xtf.ARKObject']"}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['xtf.ARKSet']"}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'xtf.dublincoreterm': {
            'Meta': {'object_name': 'DublinCoreTerm'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'qualifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'xtf.geopoint': {
            'Meta': {'unique_together': "(('object_id', 'content_type'),)", 'object_name': 'GeoPoint'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exact': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'default': '37.808690599999998'}),
            'lon': ('django.db.models.fields.FloatField', [], {'default': '-122.2675416'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'place': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['xtf']
