[app]
title = Brain Boost 2000
package.name = brainboost2000
package.domain = org.brainboost
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,wav
source.exclude_dirs = bin,.buildozer,.venv,venv,__pycache__,.git
version = 1.0.0

# Kivy 2.4.0 as requested; everything else is the Python standard library
requirements = python3,kivy==2.4.0

orientation = portrait
fullscreen = 0
android.presplash_color = #0A0D1F

# No special permissions are needed (progress is saved in app-private storage)
android.permissions =

android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 0
