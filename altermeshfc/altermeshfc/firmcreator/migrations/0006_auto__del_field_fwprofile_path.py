# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'FwProfile.path'
        db.delete_column('firmcreator_fwprofile', 'path')

        # Adding M2M table for field ssh_keys on 'FwProfile'
        db.create_table('firmcreator_fwprofile_ssh_keys', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('fwprofile', models.ForeignKey(orm['firmcreator.fwprofile'], null=False)),
            ('sshkey', models.ForeignKey(orm['firmcreator.sshkey'], null=False))
        ))
        db.create_unique('firmcreator_fwprofile_ssh_keys', ['fwprofile_id', 'sshkey_id'])


    def backwards(self, orm):
        # Adding field 'FwProfile.path'
        db.add_column('firmcreator_fwprofile', 'path',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Removing M2M table for field ssh_keys on 'FwProfile'
        db.delete_table('firmcreator_fwprofile_ssh_keys')


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
            'Meta': {'ordering': "['-pk']", 'object_name': 'FwJob'},
            'build_log': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_data': ('altermeshfc.firmcreator.fields.JSONField', [], {'default': "'{}'"}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.FwProfile']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'WAITING'", 'max_length': '10'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'firmcreator.fwprofile': {
            'Meta': {'ordering': "['network__name', 'name']", 'unique_together': "(('network', 'name'),)", 'object_name': 'FwProfile'},
            'based_on': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.FwProfile']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_files': ('altermeshfc.firmcreator.fields.JSONField', [], {'default': "'{}'"}),
            'include_packages': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'default': "'node'", 'max_length': '15'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['firmcreator.Network']"}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'ssh_keys': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['firmcreator.SSHKey']", 'symmetrical': 'False'})
        },
        'firmcreator.network': {
            'Meta': {'ordering': "['name']", 'object_name': 'Network'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'firmcreator.sshkey': {
            'Meta': {'object_name': 'SSHKey'},
            'auto_add': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('altermeshfc.firmcreator.fields.PublicKeyField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['firmcreator']