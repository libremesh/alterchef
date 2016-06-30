# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Network'
        db.create_table('firmcreator_network', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from='name', blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('firmcreator', ['Network'])

        # Adding model 'FwProfile'
        db.create_table('firmcreator_fwprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['firmcreator.Network'])),
            ('name', self.gf('django.db.models.fields.SlugField')(default='default', max_length=15)),
            ('slug', self.gf('autoslug.fields.AutoSlugField')(unique_with=(), max_length=50, populate_from=None)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('based_on', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['firmcreator.FwProfile'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('include_packages', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('include_files', self.gf('altermeshfc.firmcreator.fields.JSONField')(default='{}')),
        ))
        db.send_create_signal('firmcreator', ['FwProfile'])

        # Adding unique constraint on 'FwProfile', fields ['network', 'name']
        db.create_unique('firmcreator_fwprofile', ['network_id', 'name'])

        # Adding model 'FwJob'
        db.create_table('firmcreator_fwjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='WAITING', max_length=10)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['firmcreator.FwProfile'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('job_data', self.gf('altermeshfc.firmcreator.fields.JSONField')(default='{}')),
        ))
        db.send_create_signal('firmcreator', ['FwJob'])


    def backwards(self, orm):
        # Removing unique constraint on 'FwProfile', fields ['network', 'name']
        db.delete_unique('firmcreator_fwprofile', ['network_id', 'name'])

        # Deleting model 'Network'
        db.delete_table('firmcreator_network')

        # Deleting model 'FwProfile'
        db.delete_table('firmcreator_fwprofile')

        # Deleting model 'FwJob'
        db.delete_table('firmcreator_fwjob')


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
        'firmcreator.fwjob': {
            'Meta': {'object_name': 'FwJob'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_data': ('altermeshfc.firmcreator.fields.JSONField', [], {'default': "'{}'"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.FwProfile']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'WAITING'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'firmcreator.fwprofile': {
            'Meta': {'unique_together': "(('network', 'name'),)", 'object_name': 'FwProfile'},
            'based_on': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.FwProfile']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_files': ('altermeshfc.firmcreator.fields.JSONField', [], {'default': "'{}'"}),
            'include_packages': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'default': "'default'", 'max_length': '15'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.Network']"}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': 'None'})
        },
        'firmcreator.network': {
            'Meta': {'object_name': 'Network'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'", 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['firmcreator']