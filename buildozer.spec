[app]
title = Controle AOC Pro
package.name = controleaocpro
package.domain = org.ag40459
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,urllib3,charset-normalizer,idna

orientation = all
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
