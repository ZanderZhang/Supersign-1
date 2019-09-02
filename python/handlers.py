#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Michael Liao'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio, os, uuid
from sign import get_signed_service_url
from coroweb import get, post
from models import App, AppDeviceRecord, Account, AppAccountRecord
from iPhoneMap import get_iphone_name

def get_current_time():
    return int(time.time() * 1000)

@get('/api/saveApp')
async def api_save_app_info(*, name, size, buy_count, bundle_id):
    app = App(name = name, size = size, status = 1, add_time = get_current_time(), buy_count = buy_count, bundle_id = bundle_id)

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

    total_install_count = 0
    show_apps = []
    for app in apps:
        if app.hidden == 0:
            recordCount = await AppDeviceRecord.findNumber('count(id)', where="app_id = '" + app.id + "'")
            app.installed_count = recordCount
            total_install_count = total_install_count + recordCount
            show_apps.append(app)

    show_apps = sorted(show_apps, reverse=True, key=lambda a: a.installed_count)
    index = 1
    for app in show_apps:
        app.index = index
        app.icon_url = 'https://www.kmjskj888.com/images/icon_' + app.id + '.png'
        if app.slide_images != None:
            app.slide_images = app.slide_images.split(',')

        if app.add_time != None and app.add_time > 0:
            timeArray = time.localtime(app.add_time / 1000 + 12 * 60 * 60)
            app.add_time = time.strftime("%Y.%m.%d %H:%M:%S", timeArray)

        index = index + 1

    download_url_prefix = 'https://www.kmjskj888.com/manager/app.html?id='
    slide_image_url_prefix = 'https://www.kmjskj888.com/images/'
    manager_url = 'https://www.kmjskj888.com/manager/deviceRecord.html'
    return dict(status = 0, download_url_prefix = download_url_prefix, slide_image_url_prefix = slide_image_url_prefix, manager_url = manager_url, total_install_count = total_install_count, total_count = len(show_apps), apps = show_apps)

@get('/api/allAccount')
async def api_get_all_account():
    accounts = await Account.findAll()
    for a in accounts:
        a.password = '******'

    accounts = sorted(accounts, reverse=True, key=lambda a: a.surplus_count)
    index = 1
    for account in accounts:
        account.index = index

        timeArray = time.localtime(account.add_time / 1000 + 12 * 60 * 60)
        account.add_time = time.strftime("%Y.%m.%d %H:%M:%S", timeArray)

        index = index + 1

    return dict(status = 0, total_count = len(accounts), accounts = accounts)

@get('/api/saveAccount')
async def api_save_account_info(*, account, password, count):
    account = Account(account = account, password = password, surplus_count = count, add_time = get_current_time())

    await account.save()

    return dict(account = account)

@get('/api/appInfo')
async def api_get_app_info(*, id):
    app = await App.find(id)
    app.icon_path = 'https://www.kmjskj888.com/images/icon_' + id + '.png'
    if app.slide_images != None:
        image_names = app.slide_images.split(',')
        images = []
        for name in image_names:
            images.append('https://www.kmjskj888.com/images/' + name)
    else:
        images = ['https://www.kmjskj888.com/images/slide_default_1.png', 'https://www.kmjskj888.com/images/slide_default_2.png']
    extendedInfos = [{'title' : '开发商', 'value' : app.developer},
                     {'title' : '大小', 'value' : str(app.size) + 'MB'},
                     {'title' : '类别', 'value' : '工具'},
                     {'title' : '兼容性', 'value' : '需要iOS 9.0 或更高版本'},
                     {'title' : '语言', 'value' : '简体中文'},
                     {'title' : '年龄分级', 'value' : '4+'},
                     {'title' : '版权', 'value' : app.name}]
    udid_url = 'https://www.kmjskj888.com/configs/' + app.id + '.mobileconfig'
    jump_url = 'https://www.dibaqu.com/embedded.mobileprovision'
    video_url = 'https://vod.y1f1.cn/sv/14b45e8c-16b503055cb/14b45e8c-16b503055cb.mp4'
    banner_url = app.banner_image
    if banner_url != None:
        banner_url = 'https://www.kmjskj888.com/images/' + banner_url

    return dict(appInfo = app, images = images, extendedInfos = extendedInfos, udid_url = udid_url, jump_url = jump_url, video_url = video_url, banner_url = banner_url)

def parse_udid(xmlString):
    xml_decode_str = xmlString.decode('utf-8', errors='ignore')
    str = xml_decode_str[xml_decode_str.index('<key>UDID</key>'): xml_decode_str.index('</plist>') + 8]
    str = str.replace('\n', '')
    str = str.replace('\t', '')
    udid = str[len('<key>UDID</key><string>'): str.index('</string>')]

    str = xml_decode_str[xml_decode_str.index('<key>PRODUCT</key>'): xml_decode_str.index('</plist>') + 8]
    str = str.replace('\n', '')
    str = str.replace('\t', '')
    models = str[len('<key>PRODUCT</key><string>'): str.index('</string>')]

    return (udid, models)

@post('/api/parseUdid/{appid}')
async def api_parser_udid(appid, request):
    reader = request.content
    xmlString = await reader.read()
    udid = ''
    models = ''
    if xmlString:
        results = parse_udid(xmlString)
        udid = results[0]
        models = results[1]

    location = 'https://www.kmjskj888.com/manager/app.html?id=' + appid + '&udid=' + udid + '&models=' + models

    return dict(Location = location)

@post('/api/registerUdid')
async def api_register_udid(*, appid, udid, models):
    service_url = await get_signed_service_url(appid, udid, models)

    error_string = ''
    if service_url == '':
        error_string = '该App下载数量已满'

    return dict(service_url = service_url, error_string = error_string)

@get('/api/appDeviceRecord')
async def api_get_app_device_record(*, app_id):
    allRecords = await AppDeviceRecord.findAll()
    records = []

    for r in allRecords:
        if r.app_id == app_id:
            records.append(r)

    records = sorted(records, reverse = True, key = lambda a: a.add_time)

    index = 1
    for r in records:
        r.index = index
        r.models = get_iphone_name(r.models)

        if r.add_time == 0:
            r.add_time = None
        else:
            timeArray = time.localtime(r.add_time / 1000 + 12 * 60 * 60)
            r.add_time = time.strftime("%Y.%m.%d %H:%M:%S", timeArray)

        index = index + 1

    return dict(status = 0, total = len(records), data = records)

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

