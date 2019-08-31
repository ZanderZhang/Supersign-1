#!/usr/bin/ruby -w
require "spaceship"

# "zdn59v@163.com" "Weak4367"


is_first_device = ARGV[0]
account = ARGV[1]
password = ARGV[2]
udid = ARGV[3]
appid = ARGV[4]
bundle_id = ARGV[5]
profile_file = ARGV[6]

time = Time.now.to_i.to_s

puts "======Hello, Write Start======"

# 先登录
Spaceship.login(account, password)

# 新增设备的UDID
Spaceship::Portal.device.create!(name: time, udid: udid)

profile_name = appid

# 生成描述文件
# 先获取对应的证书
cert = Spaceship::Portal.certificate.development.all.last

devices = Spaceship.device.all
# 创建指定的APP
# 创建对应的描述文件
if is_first_device == '1'
	app = Spaceship.app.create!(bundle_id: bundle_id, name: appid)
	profile = Spaceship::Portal.provisioning_profile.development.create!(bundle_id: bundle_id, certificate: cert, name: profile_name)
else
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
end

File.write("static/sign/mobileprovision/" + profile_file + ".mobileprovision", profile.download)

count_file_name = 'static/sign/devicecount/' + account.gsub('.', '_') + '.txt'
if File.exist?(count_file_name)
    File.delete(count_file_name)
end
file = File.new(count_file_name, "w+")
if file
   file.syswrite(devices.length.to_s)
end
file.close

puts "====== Hello, Write End! ======"