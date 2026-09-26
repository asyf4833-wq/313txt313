[app]
title = Cyber Security App
package.name = cyberapp
package.domain = org.cyberapp
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy==2.2.1,cython==0.29.36,arabic-reshaper,python-bidi,urllib3,openssl,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 30
android.minapi = 21
android.archs = arm64-v8a
android.build_tools = 30.0.3
android.accept_sdk_license = True
android.allow_backup = True
p4a.branch = master
