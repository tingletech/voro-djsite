# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ThemedCollection'
        db.create_table('themed_collection_themedcollection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255, db_index=True)),
            ('questions', self.gf('django.db.models.fields.TextField')()),
            ('markup', self.gf('richtext.fields.AdminRichTextField')(default='', blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('themed_collection', ['ThemedCollection'])

        # Adding M2M table for field arksets on 'ThemedCollection'
        db.create_table('themed_collection_themedcollection_arksets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('themedcollection', models.ForeignKey(orm['themed_collection.themedcollection'], null=False)),
            ('arkset', models.ForeignKey(orm['xtf.arkset'], null=False))
        ))
        db.create_unique('themed_collection_themedcollection_arksets', ['themedcollection_id', 'arkset_id'])

        # Adding M2M table for field mosaic_members on 'ThemedCollection'
        db.create_table('themed_collection_themedcollection_mosaic_members', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('themedcollection', models.ForeignKey(orm['themed_collection.themedcollection'], null=False)),
            ('arksetmember', models.ForeignKey(orm['xtf.arksetmember'], null=False))
        ))
        db.create_unique('themed_collection_themedcollection_mosaic_members', ['themedcollection_id', 'arksetmember_id'])

        # Adding model 'ThemedCollectionSidebar'
        db.create_table('themed_collection_themedcollectionsidebar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('themed_collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['themed_collection.ThemedCollection'])),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('themed_collection', ['ThemedCollectionSidebar'])

        # Adding unique constraint on 'ThemedCollectionSidebar', fields ['title', 'themed_collection']
        db.create_unique('themed_collection_themedcollectionsidebar', ['title', 'themed_collection_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ThemedCollectionSidebar', fields ['title', 'themed_collection']
        db.delete_unique('themed_collection_themedcollectionsidebar', ['title', 'themed_collection_id'])

        # Deleting model 'ThemedCollection'
        db.delete_table('themed_collection_themedcollection')

        # Removing M2M table for field arksets on 'ThemedCollection'
        db.delete_table('themed_collection_themedcollection_arksets')

        # Removing M2M table for field mosaic_members on 'ThemedCollection'
        db.delete_table('themed_collection_themedcollection_mosaic_members')

        # Deleting model 'ThemedCollectionSidebar'
        db.delete_table('themed_collection_themedcollectionsidebar')


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
        'themed_collection.themedcollection': {
            'Meta': {'object_name': 'ThemedCollection'},
            'arksets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['xtf.ARKSet']", 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('richtext.fields.AdminRichTextField', [], {'default': "''", 'blank': 'True'}),
            'mosaic_members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['xtf.ARKSetMember']", 'null': 'True', 'blank': 'True'}),
            'questions': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'themed_collection.themedcollectionsidebar': {
            'Meta': {'unique_together': "(('title', 'themed_collection'),)", 'object_name': 'ThemedCollectionSidebar'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'themed_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['themed_collection.ThemedCollection']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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

    complete_apps = ['themed_collection']
