[app]
title = BarGo
package.name = bargo
package.domain = com.bargor.app
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 1.0
requirements = python3,flet,httpx
orientation = portrait
fullscreen = 0
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
