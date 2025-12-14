[app]
title = Auto-Aim Detector
package.name = autoaimdetector
package.domain = org.autoaim
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,opencv,numpy,ultralytics,android
orientation = portrait
fullscreen = 1
android.permissions = CAMERA,INTERNET,ACCESS_NETWORK_STATE
android.features = android.hardware.camera
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1