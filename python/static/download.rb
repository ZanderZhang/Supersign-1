#!/usr/bin/ruby -w
require "spaceship"

# "zdn59v@163.com" "Weak4367"


is_first_device = ARGV[0]
account = ARGV[1]
password = ARGV[2]
udid = ARGV[3]
appid = ARGV[4]
bundle_id = ARGV[5]

time = Time.now.to_i.to_s

puts "======Hello, Write Start======"
puts is_first_device
puts udid

# 先登录
Spaceship.login(account, password)

# 新增设备的UDID
Spaceship::Portal.device.create!(name: time, udid: udid)

profile_name = appid

# 生成描述文件
# 先获取对应的证书
cert = Spaceship.certificate.production.all.last

# 创建指定的APP
# 创建对应的描述文件
if is_first_device == '1'
	app = Spaceship.app.create!(bundle_id: bundle_id, name: appid)
	profile = Spaceship.provisioning_profile.ad_hoc.create!(bundle_id: bundle_id, certificate: cert, name: profile_name)
else
	profiles = Spaceship.provisioning_profile.ad_hoc.all
	
	devices = Spaceship.device.all
	profiles.each do |p|
		if p.name == profile_name
			p.devices = devices
        	p.update!	
		end
    end

	# 获取更新后的描述文件
	profiles = Spaceship.provisioning_profile.ad_hoc.all
	profiles.each do |p|
		if p.name == profile_name
			profile = p	
		end
    end
end

puts profile

File.write("static/sign/ios.mobileprovision", profile.download)

# fastlane sigh resign test.ipa --signing_identity "DAA8324FBE37EE66118AD69C9AB013B7A7DCC49E" -p "ios.mobileprovision"

puts "====== Hello, Write End! ======"