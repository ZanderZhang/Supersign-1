#!/usr/bin/ruby -w
require "spaceship"

# "zdn59v@163.com" "Weak4367"

account = ARGV[0]
password = ARGV[1]
appid = ARGV[2]
profile_file = ARGV[3]
bundle_id = 'com.developer.pujing.PuJing.*'

# 先登录
Spaceship.login(account, password)

profile_name = appid

devices = Spaceship.device.all

# app = ''
# appid_exist = 0
# apps = Spaceship.app.all
# apps.each do |a|
#     if a.bundle_id == bundle_id
#         app = a
#         appid_exist = 1
#     end
# end
#
# # 已经存在的id不再重新注册，兼容发多个App，但使用同一个bundle id的客户
# if appid_exist != 1
# 	app = Spaceship.app.create!(bundle_id: bundle_id, name: appid + 'id')
# end

# cert = Spaceship::Portal.certificate.development.all.last
# profile = Spaceship::Portal.provisioning_profile.development.create!(bundle_id: bundle_id, certificate: cert, name: profile_name)

profiles = Spaceship::Portal.provisioning_profile.development.all

profiles.each do |p|
	if p.name == profile_name
		p.devices = devices
        p.update!
	end
end

profile = ''
# 获取更新后的描述文件
profiles = Spaceship::Portal.provisioning_profile.development.all
profiles.each do |p|
	if p.name == profile_name
		profile = p
	end
end

File.write("static/sign/mobileprovision/" + profile_file + ".mobileprovision", profile.download)