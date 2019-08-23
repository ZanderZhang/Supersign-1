#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, os

from coroweb import get, post

from models import App, AppDeviceRecord, next_id

@get('/api/saveApp')
async def api_save_app_info(*, id):
    app = App(name = '彩票500万', status = 1, size = 5.2)
    await app.save()

    return dict()

@get('/api/appInfo')
async def api_get_app_info(*, id):
    app = await App.find(id)
    app.icon_path = 'https://www.kmjskj888.com/images/icon_' + app.id + '.png'
    images = ['http://www.kmjskj888.com/resource/image/slide_1.png', 'http://www.kmjskj888.com/resource/image/slide_2.png']
    extendedInfos = [{'title' : '开发商', 'value' : app.developer},
                     {'title' : '大小', 'value' : str(app.size) + 'MB'},
                     {'title' : '类别', 'value' : '工具'},
                     {'title' : '兼容性', 'value' : '需要iOS 9.0 或更高版本'},
                     {'title' : '语言', 'value' : 'En'},
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

    location = 'http://www.kmjskj888.com/app.html?id=' + appid + '&udid=' + udid

    return dict(Location = location)

@post('/api/registerUdid')
async def api_register_udid(*, appid, udid):
    exit = False
    records = await AppDeviceRecord.findAll()
    print(records)
    for r in records:
        if r.app_id == appid and r.udid == udid:
            exit = True
            break

    account = 'zdn59v@163.com'
    password = 'Weak4367'

    if exit:
        pass
    else:
        bundle_id = "com.kmjskj888.app." + appid
        rubyStr = 'ruby static/sign/download.rb 0 ' + account + ' ' + password + ' ' + udid + ' ' + appid + ' '+ bundle_id
        os.system(rubyStr)

        loginStr = "static/sign/ausign -email 'zdn59v@163.com' -p 'Weak4367'"
        os.system(loginStr)

        resignStr = "static/sign/ausign -sign static/ipas/" + appid + ".ipa -c static/sign/Certificates.p12 -m static/sign/ios.mobileprovision -p '' -o static/ipas/" + appid + ".ipa -id " + bundle_id
        os.system(resignStr)

        record = AppDeviceRecord(app_id = appid, udid = udid)
        await record.save()

    service_url = 'itms-services://?action=download-manifest&url=https://www.kmjskj888.com/plists/' + appid + '.plist'

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