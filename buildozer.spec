[app]
title = AlNisr
package.name = alnisr
package.domain = org.alnisr
source.dir = .
version = 2.0
requirements = python3,kivy,requests,pillow,android
orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.accept_sdk_license = True
android.gradle_dependencies = 'com.android.support:support-v4:28.0.0'

[buildozer]
log_level = 2
warn_on_root = 1
