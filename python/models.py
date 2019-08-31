#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Michael Liao'

import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

def next_id():
    return '%s%d' % (uuid.uuid1().hex, int(time.time() * 1000))

class App(Model):
    __table__ = 'app'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    status = FloatField(default=0)
    size = FloatField(default=0)
    developer = StringField(default='AppleDeveloper')
    add_time = FloatField(default=0)
    buy_count = IntegerField(default=100)
    slide_images = StringField(ddl='varchar(100)')
    is_prt = IntegerField(default=0)
    bundle_id = StringField(ddl='varchar(100)')
    hidden = IntegerField(default=0)

class AppDeviceRecord(Model):
    __table__ = 'app_device_record'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    app_id = StringField(ddl='varchar(50)')
    udid = StringField(ddl='varchar(50)')
    ipa_name = StringField(ddl='varchar(100)')
    models = StringField(ddl='varchar(100)')
    add_time = FloatField(default=0)
    available = IntegerField(default=0)     # 0初始状态  2被封  1被封后重新签名

class Account(Model):
    __table__ = 'account'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    account = StringField(ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    surplus_count = IntegerField(default=100)
    add_time = FloatField(default=0)
    is_prt = IntegerField(default=0)

class AppAccountRecord(Model):
    __table__ = 'app_account_record'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    app_id = StringField(ddl='varchar(50)')
    account_id = StringField(ddl='varchar(50)')
    ipa_name = StringField(ddl='varchar(100)')
