#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, os, uuid
import xml.etree.cElementTree as ET
from sign import get_signed_service_url
from coroweb import get, post
from models import App, AppDeviceRecord, Account

def get_current_time():
    return int(time.time() * 1000)

@get('/api/saveApp')
async def api_save_app_info(*, name, size):
    app = App(name = name, size = size, status = 1)

    await app.save()

    return dict(app = app)

@get('/api/updateApp')
async def api_update_app_info(*, app_id, app_name):
    app = await App.find(app_id)
    app.name = app_name
    await app.update()

    return dict(app = app)

@get('/api/allApp')
async def api_get_all_app():
    apps = await App.findAll()

    return dict(apps = apps)

@get('/api/allAccount')
async def api_get_all_account():
    accounts = await Account.findAll()
    for a in accounts:
        a.password = '******'

    return dict(accounts = accounts)

@get('/api/saveAccount')
async def api_save_account_info(*, account, password, count):
    account = Account(account = account, password = password, surplus_count = count, add_time = get_current_time())

    await account.save()

    return dict(account = account)

@get('/api/appInfo')
async def api_get_app_info(*, id):
    app = await App.find(id)
    app.icon_path = 'https://www.kmjskj888.com/images/icon_' + id + '.png'
    images = ['http://www.kmjskj888.com/resource/image/slide_1.png', 'http://www.kmjskj888.com/resource/image/slide_2.png']
    extendedInfos = [{'title' : '开发商', 'value' : app.developer},
                     {'title' : '大小', 'value' : str(app.size) + 'MB'},
                     {'title' : '类别', 'value' : '工具'},
                     {'title' : '兼容性', 'value' : '需要iOS 9.0 或更高版本'},
                     {'title' : '语言', 'value' : '简体中文'},
                     {'title' : '年龄分级', 'value' : '4+'},
                     {'title' : '版权', 'value' : app.name}]
    udid_url = 'https://www.kmjskj888.com/configs/' + app.id + '.mobileconfig'
    jump_url = 'https://www.dibaqu.com/embedded.mobileprovision'
    return dict(appInfo = app, images = images, extendedInfos = extendedInfos, udid_url = udid_url, jump_url = jump_url)

def parse_udid(xmlString):
    str = xmlString.decode('utf-8', errors='ignore')
    str = str[str.index('<key>UDID</key>'): str.index('</plist>') + 8]
    str = str.replace('\n', '')
    str = str.replace('\t', '')
    udid = str[len('<key>UDID</key><string>'): str.index('</string>')]
    return udid

@post('/api/parseUdid/{appid}')
async def api_parser_udid(appid, request):
    reader = request.content
    xmlString = await reader.read()
    udid = ''
    if xmlString:
        udid = parse_udid(xmlString)

    location = 'https://www.kmjskj888.com/manager/app.html?id=' + appid + '&udid=' + udid

    return dict(Location = location)

@post('/api/registerUdid')
async def api_register_udid(*, appid, udid):
    service_url = await get_signed_service_url(appid, udid)

    return dict(service_url = service_url)

@get('/api/appDeviceRecord')
async def api_get_app_device_record(*, app_id):
    allRecords = await AppDeviceRecord.findAll()
    records = []
    index = 1
    for r in allRecords:
        if r.app_id == app_id:
            r.index = index
            records.append(r)
            index = index + 1

    return dict(status = 0, total = len(records), data = records)