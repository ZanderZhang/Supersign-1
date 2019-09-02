#!/usr/bin/ruby -w
require "spaceship"

# "zdn59v@163.com" "Weak4367"

account = ARGV[0]
password = ARGV[1]
udid = ARGV[2]
appid = ARGV[3]
bundle_id = ARGV[4]

time = Time.now.to_i.to_s

# 先登录
Spaceship.login(account, password)

profile_name = appid

# 生成描述文件
# 先获取对应的证书
cert = Spaceship::Portal.certificate.development.all.last

devices = Spaceship.device.all
# 创建指定的APP
# 创建对应的描述文件

profiles = Spaceship::Portal.provisioning_profile.development.all

profiles.each do |p|
	if p.name == profile_name
		p.devices = devices
        p.update!
	end
end

# 获取更新后的描述文件
profiles = Spaceship::Portal.provisioning_profile.development.all
profiles.each do |p|
	if p.name == profile_name
		profile = p
	end
end

File.write("static/sign/" + appid + "test.mobileprovision", profile.download)