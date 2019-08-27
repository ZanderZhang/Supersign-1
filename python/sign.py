#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'PerTerbin'

import os, time, plistlib
from models import App, AppDeviceRecord, Account, AppAccountRecord

# 查找当前可用账号
async def get_current_account():
    accounts = await Account.findAll()
    accounts = sorted(accounts, key=lambda a:a.add_time)

    current_account = None
    for a in accounts:
        if a.surplus_count > 0:
            current_account = a
            break

    return current_account

# 查找当前可用账号里的 app 记录，没有返回 None
async def get_current_account_app_record(current_account, appid):
    all_records = await AppAccountRecord.findAll()

    record = None
    for r in all_records:
        if r.app_id == appid and r.account_id == current_account.id:
            record = r
            break

    return record

async def save_app_account_record(account_id, app_id, ipa_name):
    record = AppAccountRecord(app_id = app_id, account_id = account_id, ipa_name = ipa_name)

    await record.save()


async def save_app_device_record(app_id, udid, ipa_name):
    record = AppDeviceRecord(app_id = app_id, udid = udid, ipa_name = ipa_name, add_time = int(time.time() * 1000))

    await record.save()

async def increasing_app_count(app_id):
    app = App.find(app_id)
    app.surplus_count = app.surplus_count - 1
    app.installed_count = app.installed_count + 1
    await app.update()

def create_new_plist(app_id, ipa_name, app_name):
    plist_path = 'static/plists/' + ipa_name + '.plist'
    copy_plist_script = 'cp static/plists/default.plist ' + plist_path
    os.system(copy_plist_script)

    plist = plistlib.readPlist(plist_path)
    assets = plist['items'][0]['assets']
    assets[0]['url'] = 'https://www.kmjskj888.com/ipas/' + ipa_name + '.ipa'
    assets[1]['url'] = 'https://www.kmjskj888.com/images/icon_' + app_id + '.png'
    assets[2]['url'] = 'https://www.kmjskj888.com/images/icon_' + app_id + '.png'
    metadata = plist['items'][0]['metadata']
    metadata['bundle-identifier'] = 'com.kmjskj888.app.' + ipa_name
    metadata['subtitle'] = app_name
    metadata['title'] = app_name

    plistlib.writePlist(plist, plist_path)


async def get_signed_service_url(appid, udid):
    records = await AppDeviceRecord.findAll()

    exitRecord = None
    for r in records:
        if r.app_id == appid and r.udid == udid:
            exitRecord = r
            break

    # 该设备已经下载过该App，直接给包
    if exitRecord != None:
        new_ipa_name = exitRecord.ipa_name
    else:
        current_account = await get_current_account()
        if current_account is None:
            return ''

        current_record = await get_current_account_app_record(current_account, appid)

        if current_record != None:
            # 当前账号已经签过该 App
            need_create_new_app = '0'
            old_ipa_name = current_record.ipa_name
            new_ipa_name = current_record.ipa_name
            bundle_id = "com.kmjskj888.app." + new_ipa_name
        else:
            need_create_new_app = '1'
            old_ipa_name = appid
            new_ipa_name = appid + '_' + str(int(time.time() * 1000))
            bundle_id = "com.kmjskj888.app." + new_ipa_name
            await save_app_account_record(current_account.id, appid, new_ipa_name)
            # 生成plist
            app = await App.find(appid)
            create_new_plist(appid, new_ipa_name, app.name)

        # 往苹果后台注册 udid
        register_udid_script = 'ruby static/sign/download.rb ' + need_create_new_app + ' ' + current_account.account + ' ' + current_account.password + ' ' + udid + ' ' + appid + ' '+ bundle_id
        os.system(register_udid_script)

        # 登录签名脚本
        login_script = "static/sign/ausign -email 'zdn59v@163.com' -p 'Weak4367'"
        os.system(login_script)

        # 重签名
        resign_script = "static/sign/ausign -sign static/ipas/" + old_ipa_name + ".ipa -c static/sign/" + current_account.id + ".p12 -m static/sign/" + appid + ".mobileprovision -p '' -o static/ipas/" + new_ipa_name + ".ipa -id " + bundle_id
        os.system(resign_script)

        flie = None
        try:
            file_name = 'static/sign/devicecount/' + current_account.account.replace('.', '_') + '.txt'
            flie = open(file_name, 'r')
            current_account.surplus_count = 100 - int(flie.read())
            await current_account.update()
        finally:
            if flie != None:
                flie.close()

        await save_app_device_record(appid, udid, new_ipa_name)
        await increasing_app_count(appid)
        
    if new_ipa_name is None:
        new_ipa_name = appid

    service_url = 'itms-services://?action=download-manifest&url=https://www.kmjskj888.com/plists/' + new_ipa_name + '.plist'

    return service_url
