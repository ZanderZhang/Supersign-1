#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, os, uuid
import xml.etree.cElementTree as ET
from sign import get_signed_service_url
from coroweb import get, post
from models import App, AppDeviceRecord, Account, AppAccountRecord

def get_current_time():
    return int(time.time() * 1000)

def create_mobile_config(app_id, app_name):
    default_config_path = 'static/configs/udid.mobileconfig'
    templete_config_path = 'static/configs/templete.mobileconfig'
    new_config_path = 'static/configs/' + app_id + '.mobileconfig'
    tree = ET.parse(default_config_path)
    root = tree.getroot()

    index = 0
    for item in root.iter('string'):
        if index == 0:
            item.text = 'https://www.kmjskj888.com/api/parseUdid/' + app_id
        if index == 7:
            item.text = app_name
        if index == 8:
            item.text = str(uuid.uuid4())
        index = index + 1

    tree.write(templete_config_path, encoding="utf-8")

    # 签名
    script = 'openssl smime -sign -in ' + templete_config_path + ' -out ' + new_config_path + ' -signer cert/service.crt -inkey cert/service.key -certfile cert/service_nginx.crt -outform der -nodetach'
    os.system(script)


@get('/api/test')
async def api_test():
    apps = await App.findAll()
    for app in apps:
        create_mobile_config(app.id, app.name)

    return dict()

@get('/api/saveApp')
async def api_save_app_info(*, name, size, count):
    app = App(name = name, size = size, status = 1, surplus_count = count, add_time = get_current_time())
    app.id = 'adhasjdhasjdhasjdhajkdhajkhd'
    # await app.save()

    create_mobile_config(app.id, app.name)

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
    for app in apps:
        recordCount = await AppDeviceRecord.findNumber('count(id)', where="app_id = '" + app.id + "'")
        app.installed_count = recordCount
    
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

@post('/api/uploadIcon')
async def api_upload_icon(request):
    reader = request.content
    data = await reader.read()
    print(data)

    try:
        with open('mm_copy.png', 'wb') as fs2:
            fs2.write(data)
    except FileNotFoundError as e:
        print('指定的文件无法打开')
    except IOError as e:
        print('读写文件时出现错误.')

    return dict()

@get('/api/resignApp')
async def api_resigrn_app(*, app_id):
    allRecords = await AppAccountRecord.findAll()
    records = []

    for r in allRecords:
        if r.app_id == app_id:
            records.append(r)

    for r in records:
        account = await Account.find(r.account_id)

        profile_name = app_id + '_' + account.account.replace('.', '_')
        profile_path = '/usr/local/nginx/html/python/static/sign/mobileprovision/' + profile_name + '.mobileprovision'
        profile_exist = os.path.exists(profile_path)

        if profile_exist == False:
            # 下载证书
            register_udid_script = 'ruby static/sign/resign.rb ' + account.account + ' ' + account.password + ' ' + app_id + ' ' + profile_name
            os.system(register_udid_script)

        # 登录签名脚本
        login_script = "static/sign/ausign -email 'zdn59v@163.com' -p 'Weak4367'"
        os.system(login_script)

        # 重签名
        resign_script = "static/sign/ausign -sign static/ipas/" + app_id + ".ipa -c static/sign/p12/" + account.id + ".p12 -m static/sign/mobileprovision/" + profile_name + ".mobileprovision -p '' -o static/ipas/" + r.ipa_name + ".ipa"
        os.system(resign_script)

    return dict()
