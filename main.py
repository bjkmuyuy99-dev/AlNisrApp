from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.clock import Clock
import requests
import threading
import json
import socket
import os
import subprocess
from PIL import Image as PILImage
from PIL.ExifTags import TAGS, GPSTAGS

# ===================================================
# FEATURE 1: EMAIL HUNTER - فاحص الايميلات
# ===================================================
class EmailHunter:
    def __init__(self):
        self.sites = {
            "Twitter": {"url": "https://api.twitter.com/i/users/email_available.json?email={}", "method": "api"},
            "Instagram": {"url": "https://www.instagram.com/accounts/web_create_ajax/attempt/", "method": "post"},
            "GitHub": {"url": "https://api.github.com/search/users?q={}+in:email", "method": "api"},
            "Spotify": {"url": "https://spclient.wg.spotify.com/signup/public/v1/account?validate=1&email={}", "method": "api"},
            "Pinterest": {"url": "https://www.pinterest.com/_ngjs/resource/EmailExistsResource/get/?source_url=/&data={{\"options\":{{\"email\":\"{}\"}}}}", "method": "api"},
            "Samsung": {"url": "https://account.samsung.com/accounts/v1/Samsung/checkEmailIDAvailability?email={}", "method": "api"},
            "Adobe": {"url": "https://account.adobe.com/check/email?email={}", "method": "api"},
            "Tumblr": {"url": "https://www.tumblr.com/register/check/email?email={}", "method": "api"},
            "WordPress": {"url": "https://public-api.wordpress.com/rest/v1.1/users/suggest?q={}", "method": "api"},
            "Gravatar": {"url": "https://en.gravatar.com/{}.json", "method": "hash"},
            "Duolingo": {"url": "https://www.duolingo.com/2017-06-30/users?email={}", "method": "api"},
            "Snapchat": {"url": "https://accounts.snapchat.com/accounts/login", "method": "post"},
            "TikTok": {"url": "https://www.tiktok.com/api/user/detail/?uniqueId={}", "method": "api"},
            "LinkedIn": {"url": "https://www.linkedin.com/sales/gmail/profile/proxy/{}", "method": "api"},
            "Facebook": {"url": "https://www.facebook.com/recover/initiate/?email={}", "method": "recover"},
            "Amazon": {"url": "https://www.amazon.com/ap/signin", "method": "post"},
            "Apple": {"url": "https://iforgot.apple.com/password/verify/appleid?appleid={}", "method": "api"},
            "Steam": {"url": "https://store.steampowered.com/join/ajaxcheckemailverified?email={}", "method": "api"},
            "Yahoo": {"url": "https://login.yahoo.com/account/module/create?validateField=yid&yid={}", "method": "api"},
            "Microsoft": {"url": "https://login.live.com/GetCredentialType.srf", "method": "post_json"},
            "Netflix": {"url": "https://www.netflix.com/in/LoginHelp", "method": "post"},
            "Discord": {"url": "https://discord.com/api/v9/auth/register", "method": "post_json"},
            "Twitch": {"url": "https://passport.twitch.tv/usernames/{}", "method": "api"},
            "Reddit": {"url": "https://www.reddit.com/api/check_email.json?email={}", "method": "api"},
            "PayPal": {"url": "https://www.paypal.com/signup/existinguser?email={}", "method": "api"},
            "eBay": {"url": "https://signin.ebay.com/ws/eBayISAPI.dll?SignIn&email={}", "method": "api"},
            "Zoom": {"url": "https://zoom.us/account/user/email/check?email={}", "method": "api"},
            "Dropbox": {"url": "https://www.dropbox.com/exists?email={}", "method": "api"},
            "Slack": {"url": "https://slack.com/api/users.getPresence?email={}", "method": "api"},
            "Telegram": {"url": "https://t.me/{}", "method": "scrape"}
        }

    def check_email(self, email):
        results = []
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        for site_name, config in self.sites.items():
            try:
                url = config["url"].format(email)
                if config["method"] == "api":
                    r = requests.get(url, headers=headers, timeout=8)
                    results.append(f"[+] مسجل في: {site_name}" if r.status_code == 200 else f"[-] غير موجود: {site_name}")
                elif config["method"] == "post":
                    r = requests.post(url, data={"email": email}, headers=headers, timeout=8)
                    results.append(f"[+] مسجل في: {site_name}" if r.status_code == 200 else f"[-] غير موجود: {site_name}")
                elif config["method"] == "post_json":
                    r = requests.post(url, json={"username": email}, headers=headers, timeout=8)
                    if r.status_code == 200:
                        body = r.json()
                        results.append(f"[+] مسجل في: {site_name}" if "IfExistsResult" in str(body) else f"[-] غير موجود: {site_name}")
                elif config["method"] == "recover":
                    r = requests.get(url, headers=headers, timeout=8, allow_redirects=False)
                    results.append(f"[+] مسجل في: {site_name}" if r.status_code in [200, 302] else f"[-] غير موجود: {site_name}")
                elif config["method"] == "hash":
                    import hashlib
                    email_hash = hashlib.md5(email.strip().lower().encode()).hexdigest()
                    r = requests.get(f"https://en.gravatar.com/{email_hash}.json", headers=headers, timeout=8)
                    results.append(f"[+] مسجل في: {site_name}" if r.status_code == 200 else f"[-] غير موجود: {site_name}")
                elif config["method"] == "scrape":
                    r = requests.get(url, headers=headers, timeout=8)
                    results.append(f"[+] مسجل في: {site_name}" if r.status_code == 200 and "tgme_page_title" in r.text else f"[-] غير موجود: {site_name}")
            except Exception as e:
                results.append(f"[!] خطأ بـ {site_name}: {str(e)[:30]}")
        return results


# ===================================================
# FEATURE 2: IP TRACER - تعقب IP
# ===================================================
class IPTracer:
    def trace(self, ip):
        results = []
        try:
            r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719&lang=ar", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get('status') == 'success':
                    results.append("=" * 40)
                    results.append(f"🌍 الدولة: {data.get('country', 'غير معروف')}")
                    results.append(f"🏙️ المدينة: {data.get('city', 'غير معروف')}")
                    results.append(f"📍 المنطقة: {data.get('regionName', 'غير معروف')}")
                    results.append(f"📮 الرمز البريدي: {data.get('zip', 'غير معروف')}")
                    results.append(f"🌐 مزود الخدمة: {data.get('isp', 'غير معروف')}")
                    results.append(f"🏢 المنظمة: {data.get('org', 'غير معروف')}")
                    results.append(f"📡 AS: {data.get('as', 'غير معروف')}")
                    results.append(f"📌 خط العرض: {data.get('lat', 'غير معروف')}")
                    results.append(f"📌 خط الطول: {data.get('lon', 'غير معروف')}")
                    results.append(f"⏰ المنطقة الزمنية: {data.get('timezone', 'غير معروف')}")
                    results.append(f"📱 موبايل: {'نعم' if data.get('mobile') else 'لا'}")
                    results.append(f"🔒 بروكسي/VPN: {'نعم' if data.get('proxy') else 'لا'}")
                    results.append(f"🏠 استضافة: {'نعم' if data.get('hosting') else 'لا'}")
                    results.append("=" * 40)
                    lat = data.get('lat')
                    lon = data.get('lon')
                    if lat and lon:
                        results.append(f"🗺️ خريطة: https://www.google.com/maps?q={lat},{lon}")
                else:
                    results.append(f"[-] فشل: {data.get('message', 'IP غير صالح')}")
            r2 = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
            if r2.status_code == 200:
                data2 = r2.json()
                results.append("\n--- معلومات اضافية ---")
                results.append(f"🏷️ Hostname: {data2.get('hostname', 'غير معروف')}")
                results.append(f"🔗 Anycast: {data2.get('anycast', 'غير معروف')}")
            try:
                hostname = socket.gethostbyaddr(ip)
                results.append(f"🖥️ DNS العكسي: {hostname[0]}")
            except:
                results.append("🖥️ DNS العكسي: غير متوفر")
            results.append("\n--- فحص المنافذ ---")
            common_ports = {21: "FTP", 22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 3389: "RDP", 8080: "Proxy", 8443: "Alt-HTTPS"}
            for port, service in common_ports.items():
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        results.append(f"  [مفتوح] المنفذ {port} ({service})")
                    s.close()
                except:
                    pass
        except Exception as e:
            results.append(f"[!] خطأ: {str(e)}")
        return results


# ===================================================
# FEATURE 4: EXIF ANALYZER - محلل صور
# ===================================================
class EXIFAnalyzer:
    def get_decimal_coords(self, gps_coords, gps_ref):
        decimal_degrees = gps_coords[0] + gps_coords[1] / 60 + gps_coords[2] / 3600
        if gps_ref == "S" or gps_ref == "W":
            decimal_degrees = -decimal_degrees
        return decimal_degrees

    def analyze(self, image_path):
        results = []
        try:
            img = PILImage.open(image_path)
            exif_data = img._getexif()
            if not exif_data:
                results.append("[-] لا توجد بيانات EXIF في هذه الصورة")
                return results
            results.append("=" * 40)
            results.append("📸 بيانات EXIF المستخرجة:")
            results.append("=" * 40)
            gps_info = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "GPSInfo":
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = value[gps_tag_id]
                elif tag == "Make": results.append(f"📱 الشركة المصنعة: {value}")
                elif tag == "Model": results.append(f"📱 موديل الجهاز: {value}")
                elif tag == "DateTime": results.append(f"📅 تاريخ الالتقاط: {value}")
                elif tag == "DateTimeOriginal": results.append(f"📅 التاريخ الاصلي: {value}")
                elif tag == "Software": results.append(f"💻 البرنامج: {value}")
                elif tag == "ImageWidth": results.append(f"📐 العرض: {value}")
                elif tag == "ImageLength": results.append(f"📐 الطول: {value}")
                elif tag == "ExposureTime": results.append(f"⚡ وقت التعريض: {value}")
                elif tag == "FNumber": results.append(f"🔍 فتحة العدسة: f/{value}")
                elif tag == "ISOSpeedRatings": results.append(f"🎯 ISO: {value}")
                elif tag == "FocalLength": results.append(f"🔭 البعد البؤري: {value}mm")
                elif tag == "Flash": results.append(f"💡 الفلاش: {value}")
                elif tag == "LensModel": results.append(f"🔭 العدسة: {value}")
                elif tag == "Artist": results.append(f"👤 المصور: {value}")
                elif tag == "Copyright": results.append(f"©️ حقوق النشر: {value}")
            if gps_info:
                results.append("\n" + "=" * 40)
                results.append("🛰️ بيانات الموقع GPS:")
                results.append("=" * 40)
                try:
                    lat = self.get_decimal_coords(gps_info.get("GPSLatitude", (0, 0, 0)), gps_info.get("GPSLatitudeRef", "N"))
                    lon = self.get_decimal_coords(gps_info.get("GPSLongitude", (0, 0, 0)), gps_info.get("GPSLongitudeRef", "E"))
                    results.append(f"📍 خط العرض: {lat}")
                    results.append(f"📍 خط الطول: {lon}")
                    results.append(f"📏 الارتفاع: {gps_info.get('GPSAltitude', 'غير متوفر')}م")
                    results.append(f"🗺️ الموقع على الخريطة:")
                    results.append(f"   https://www.google.com/maps?q={lat},{lon}")
                    try:
                        geo_r = requests.get(f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json", headers={"User-Agent": "AlNisr-OSINT"}, timeout=10)
                        if geo_r.status_code == 200:
                            address = geo_r.json().get("display_name", "غير متوفر")
                            results.append(f"🏠 العنوان الكامل: {address}")
                    except:
                        pass
                except Exception as e:
                    results.append(f"[!] خطأ بقراءة GPS: {str(e)}")
            else:
                results.append("\n[-] لا توجد بيانات GPS في الصورة")
        except Exception as e:
            results.append(f"[!] خطأ: {str(e)}")
        return results


# ===================================================
# FEATURE 6: PHONE LOOKUP - فاحص ارقام الهاتف
# ===================================================
class PhoneLookup:
    def __init__(self):
        self.country_codes = {
            "+1": "🇺🇸 امريكا/كندا", "+7": "🇷🇺 روسيا", "+20": "🇪🇬 مصر",
            "+44": "🇬🇧 بريطانيا", "+49": "🇩🇪 المانيا", "+33": "🇫🇷 فرنسا",
            "+39": "🇮🇹 ايطاليا", "+34": "🇪🇸 اسبانيا", "+81": "🇯🇵 اليابان",
            "+82": "🇰🇷 كوريا", "+86": "🇨🇳 الصين", "+91": "🇮🇳 الهند",
            "+55": "🇧🇷 البرازيل", "+52": "🇲🇽 المكسيك", "+90": "🇹🇷 تركيا",
            "+966": "🇸🇦 السعودية", "+971": "🇦🇪 الامارات", "+962": "🇯🇴 الاردن",
            "+961": "🇱🇧 لبنان", "+964": "🇮🇶 العراق", "+965": "🇰🇼 الكويت",
            "+974": "🇶🇦 قطر", "+973": "🇧🇭 البحرين", "+968": "🇴🇲 عمان",
            "+967": "🇾🇪 اليمن", "+963": "🇸🇾 سوريا", "+970": "🇵🇸 فلسطين",
            "+218": "🇱🇾 ليبيا", "+213": "🇩🇿 الجزائر", "+216": "🇹🇳 تونس",
            "+212": "🇲🇦 المغرب", "+249": "🇸🇩 السودان", "+254": "🇰🇪 كينيا",
            "+234": "🇳🇬 نيجيريا", "+27": "🇿🇦 جنوب افريقيا", "+60": "🇲🇾 ماليزيا",
            "+62": "🇮🇩 اندونيسيا", "+63": "🇵🇭 الفلبين", "+66": "🇹🇭 تايلند",
            "+84": "🇻🇳 فيتنام", "+380": "🇺🇦 اوكرانيا", "+48": "🇵🇱 بولندا",
            "+31": "🇳🇱 هولندا", "+46": "🇸🇪 السويد", "+47": "🇳🇴 النرويج",
            "+45": "🇩🇰 الدنمارك", "+358": "🇫🇮 فنلندا", "+41": "🇨🇭 سويسرا",
            "+43": "🇦🇹 النمسا", "+32": "🇧🇪 بلجيكا", "+351": "🇵🇹 البرتغال",
            "+30": "🇬🇷 اليونان", "+40": "🇷🇴 رومانيا", "+36": "🇭🇺 هنغاريا",
            "+420": "🇨🇿 التشيك", "+61": "🇦🇺 استراليا", "+64": "🇳🇿 نيوزيلندا",
            "+65": "🇸🇬 سنغافورة", "+852": "🇭🇰 هونغ كونغ", "+886": "🇹🇼 تايوان",
            "+92": "🇵🇰 باكستان", "+93": "🇦🇫 افغانستان", "+98": "🇮🇷 ايران",
            "+972": "🇮🇱 اسرائيل"
        }
        self.carrier_prefixes_iq = {
            "750": "آسياسيل", "751": "آسياسيل", "770": "زين",
            "771": "زين", "780": "كورك", "781": "كورك",
            "790": "آسياسيل", "783": "كورك"
        }

    def lookup(self, phone):
        results = []
        phone = phone.strip().replace(" ", "").replace("-", "")
        results.append("=" * 40)
        results.append(f"📞 تحليل الرقم: {phone}")
        results.append("=" * 40)
        detected_country = "غير معروف"
        for code, country in sorted(self.country_codes.items(), key=lambda x: -len(x[0])):
            if phone.startswith(code):
                detected_country = country
                results.append(f"🌍 الدولة: {country}")
                results.append(f"📡 مفتاح الاتصال: {code}")
                if code == "+964":
                    local = phone.replace("+964", "")
                    prefix = local[:3]
                    carrier = self.carrier_prefixes_iq.get(prefix, "غير معروف")
                    results.append(f"📱 شركة الاتصالات: {carrier}")
                break
        if detected_country == "غير معروف":
            results.append("⚠️ مفتاح الاتصال غير معروف")
        results.append(f"📱 نوع الخط: موبايل (تقدير)")
        try:
            r = requests.get(f"http://apilayer.net/api/validate?access_key=YOUR_KEY&number={phone}&format=1", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("valid"):
                    results.append(f"✅ الرقم صالح: نعم")
                    results.append(f"📱 النوع: {data.get('line_type', 'غير معروف')}")
                    results.append(f"🏢 الشركة: {data.get('carrier', 'غير معروف')}")
                    results.append(f"🌍 الدولة: {data.get('country_name', 'غير معروف')}")
                    results.append(f"📍 الموقع: {data.get('location', 'غير معروف')}")
        except:
            pass
        try:
            r2 = requests.get(f"https://numverify.com/php_helper_scripts/phone_api.php?secret_key=&number={phone}", timeout=10)
            if r2.status_code == 200:
                data2 = r2.json()
                if data2.get("valid"):
                    results.append(f"\n--- معلومات اضافية ---")
                    results.append(f"📍 الموقع: {data2.get('location', 'N/A')}")
                    results.append(f"🏢 الشركة: {data2.get('carrier', 'N/A')}")
                    results.append(f"📱 النوع: {data2.get('line_type', 'N/A')}")
        except:
            pass
        results.append("=" * 40)
        return results


# ===================================================
# NEW FEATURE 7: NETWORK RADAR - رادار الشبكة
# ===================================================
class NetworkRadar:
    def __init__(self):
        self.found_devices = []

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    def get_mac_vendor(self, mac):
        try:
            r = requests.get(f"https://api.macvendors.com/{mac}", timeout=5)
            if r.status_code == 200:
                return r.text.strip()
            return "غير معروف"
        except:
            return "غير معروف"

    def scan_device(self, ip, results_widget):
        try:
            param = "-n" if os.name == "nt" else "-c"
            command = ["ping", param, "1", "-W", "1", ip]
            response = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if response == 0:
                device_info = f"\n{'='*35}\n"
                device_info += f"✅ جهاز مكتشف: {ip}\n"
                # محاولة الحصول على اسم الجهاز
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    device_info += f"🖥️ اسم الجهاز: {hostname}\n"
                except:
                    device_info += f"🖥️ اسم الجهاز: غير متوفر\n"
                # فحص المنافذ المفتوحة على الجهاز
                open_ports = []
                ports_to_check = {
                    80: "HTTP", 443: "HTTPS", 22: "SSH", 23: "Telnet",
                    21: "FTP", 8080: "HTTP-Alt", 8443: "HTTPS-Alt",
                    3389: "RDP", 5900: "VNC", 8888: "HTTP-Dev",
                    53: "DNS", 137: "NetBIOS", 445: "SMB", 139: "NetBIOS",
                    25: "SMTP", 110: "POP3", 143: "IMAP", 3306: "MySQL",
                    5432: "PostgreSQL", 27017: "MongoDB", 6379: "Redis",
                    1883: "MQTT", 5555: "ADB-Android", 62078: "iPhone-Sync"
                }
                for port, service in ports_to_check.items():
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        result = s.connect_ex((ip, port))
                        if result == 0:
                            open_ports.append(f"    [🔓 مفتوح] {port} ({service})")
                        s.close()
                    except:
                        pass
                if open_ports:
                    device_info += f"🔍 المنافذ المفتوحة:\n"
                    device_info += "\n".join(open_ports) + "\n"
                else:
                    device_info += f"🔒 لا توجد منافذ مفتوحة شائعة\n"
                # كشف نوع الجهاز من TTL
                try:
                    ping_result = subprocess.run(
                        ["ping", param, "1", ip],
                        capture_output=True, text=True, timeout=3
                    )
                    output = ping_result.stdout
                    if "ttl=64" in output.lower() or "ttl=63" in output.lower():
                        device_info += f"📱 نوع النظام: Linux/Android/iOS\n"
                    elif "ttl=128" in output.lower() or "ttl=127" in output.lower():
                        device_info += f"💻 نوع النظام: Windows\n"
                    elif "ttl=255" in output.lower() or "ttl=254" in output.lower():
                        device_info += f"🔌 نوع النظام: Router/Cisco\n"
                except:
                    pass
                device_info += f"{'='*35}\n"
                self.found_devices.append(ip)
                Clock.schedule_once(lambda dt: setattr(results_widget, 'text', results_widget.text + device_info), 0)
        except Exception as e:
            pass

    def start_scan(self, results_widget):
        self.found_devices = []
        local_ip = self.get_local_ip()
        if not local_ip:
            results_widget.text += "[-] فشل في تحديد الشبكة\n"
            return
        base_ip = ".".join(local_ip.split(".")[:-1]) + "."
        Clock.schedule_once(lambda dt: setattr(results_widget, 'text',
            results_widget.text + f"[*] IP الجهاز: {local_ip}\n[*] شبكة الهدف: {base_ip}0/24\n[*] جاري المسح...\n"), 0)
        threads = []
        for i in range(1, 255):
            ip = base_ip + str(i)
            t = threading.Thread(target=self.scan_device, args=(ip, results_widget))
            t.daemon = True
            threads.append(t)
            t.start()
            if len(threads) % 50 == 0:
                for thread in threads[-50:]:
                    thread.join(timeout=3)
        def finish(dt):
            results_widget.text += f"\n[✓] اكتمل المسح. تم اكتشاف {len(self.found_devices)} جهاز.\n"
        Clock.schedule_once(finish, 8)


# ===================================================
# NEW FEATURE 8: DEEP WEB SCRAPER - صائد الديب ويب
# ===================================================
class DeepWebScraper:
    def __init__(self):
        self.all_nodes = [
            # السوشيال الرئيسية
            "https://www.instagram.com/{}", "https://www.twitter.com/{}",
            "https://www.facebook.com/{}", "https://www.tiktok.com/@{}",
            "https://www.snapchat.com/add/{}", "https://t.me/{}",
            "https://www.linkedin.com/in/{}", "https://www.pinterest.com/{}",
            "https://www.youtube.com/@{}", "https://www.twitch.tv/{}",
            "https://www.reddit.com/user/{}", "https://www.threads.net/@{}",
            # منصات التقنية
            "https://www.github.com/{}", "https://www.gitlab.com/{}",
            "https://www.bitbucket.org/{}", "https://www.stackoverflow.com/users/{}",
            "https://www.hackerrank.com/{}", "https://www.leetcode.com/{}",
            "https://www.codepen.io/{}", "https://www.replit.com/@{}",
            "https://www.tryhackme.com/p/{}", "https://www.hackthebox.com/profile/{}",
            "https://www.hackerone.com/{}", "https://www.bugcrowd.com/{}",
            # منصات الابداع
            "https://www.behance.net/{}", "https://www.dribbble.com/{}",
            "https://www.deviantart.com/{}", "https://www.artstation.com/{}",
            "https://www.medium.com/@{}", "https://www.substack.com/@{}",
            # منصات الموسيقى
            "https://www.soundcloud.com/{}", "https://www.mixcloud.com/{}",
            "https://open.spotify.com/user/{}", "https://www.last.fm/user/{}",
            "https://www.bandcamp.com/{}", "https://www.audiomack.com/{}",
            # منصات الفيديو
            "https://www.vimeo.com/{}", "https://www.dailymotion.com/{}",
            "https://www.rumble.com/user/{}", "https://www.odysee.com/@{}",
            "https://www.kick.com/{}", "https://www.trovo.live/{}",
            # منصات التسوق
            "https://www.etsy.com/shop/{}", "https://www.ebay.com/usr/{}",
            "https://www.amazon.com/seller/{}",
            # منصات الشبكات الاجتماعية الاخرى
            "https://www.vk.com/{}", "https://www.ok.ru/{}",
            "https://www.flickr.com/people/{}", "https://www.tumblr.com/{}",
            "https://www.myspace.com/{}", "https://www.ask.fm/{}",
            "https://www.quora.com/profile/{}", "https://www.wattpad.com/user/{}",
            "https://www.goodreads.com/{}", "https://www.producthunt.com/@{}",
            # منصات الالعاب
            "https://www.steamcommunity.com/id/{}", "https://www.roblox.com/user/{}",
            "https://www.xbox.com/profile/{}", "https://www.twitch.tv/{}",
            "https://www.chess.com/member/{}", "https://www.kongregate.com/accounts/{}",
            # منصات الدفع والعملات
            "https://www.paypal.com/{}", "https://www.cash.app/${}",
            "https://www.patreon.com/{}", "https://www.ko-fi.com/{}",
            # مواقع البحث والارشفة
            "https://www.pastebin.com/u/{}", "https://www.archive.org/details/@{}",
            "https://www.scribd.com/{}", "https://www.slideshare.net/{}",
            # مواقع التواصل المهني
            "https://www.about.me/{}", "https://www.keybase.io/{}",
            "https://www.angel.co/{}", "https://www.crunchbase.com/person/{}",
            # مواقع OSINT متخصصة
            "https://www.namechk.com/{}", "https://www.checkusernames.com/{}",
            "https://www.knowem.com/{}",
            # مواقع الاخبار والمجتمعات
            "https://www.mastodon.social/@{}", "https://news.ycombinator.com/user?id={}",
            "https://www.disqus.com/by/{}", "https://www.blogger.com/profile/{}",
            # مواقع الديب ويب والمنتديات المخفية (Surface Web Links)
            "https://www.exploit-db.com/search?q={}", "https://www.shodan.io/search?query={}",
            "https://www.censys.io/search?q={}", "https://www.zoomeye.org/searchResult?q={}",
            "https://www.hunter.io/search/{}", "https://www.pipl.com/search/?q={}",
            "https://www.spokeo.com/{}", "https://www.peekyou.com/{}",
            "https://www.been-verified.com/f/search/people?q={}",
            "https://www.whitepages.com/name/{}", "https://www.radaris.com/p/{}",
            "https://www.intelius.com/search/people/results?firstName={}",
            # مواقع الصور العكسية
            "https://www.tineye.com/search?url={}", "https://yandex.com/images/search?text={}",
            "https://www.pimeyes.com/",
            # مواقع اخرى متنوعة
            "https://www.gravatar.com/{}", "https://www.npmjs.com/~{}",
            "https://www.pypi.org/user/{}", "https://www.docker.com/u/{}",
            "https://hub.docker.com/u/{}", "https://www.terraform.io/{}",
            "https://www.figma.com/@{}", "https://www.notion.so/@{}",
            "https://www.producthunt.com/@{}", "https://www.angellist.com/{}",
        ]

    def deep_hunt(self, target, results_widget):
        total = len(self.all_nodes)
        found = [0]
        checked = [0]

        def check_node(url_template):
            url = url_template.format(target)
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                r = requests.get(url, headers=headers, timeout=6, allow_redirects=True)
                checked[0] += 1
                if r.status_code == 200:
                    page_text = r.text.lower()
                    if (target.lower() in page_text and
                        "not found" not in page_text and
                        "doesn't exist" not in page_text and
                        "page not found" not in page_text and
                        "404" not in page_text[:500]):
                        found[0] += 1
                        result_line = f"[+++] 🎯 وجدناه: {url}\n"
                        Clock.schedule_once(lambda dt: setattr(results_widget, 'text', results_widget.text + result_line), 0)
                progress = f"[{checked[0]}/{total}] جاري البحث...\n"
            except Exception as e:
                checked[0] += 1

        def run_all():
            threads = []
            for node in self.all_nodes:
                t = threading.Thread(target=check_node, args=(node,))
                t.daemon = True
                threads.append(t)
                t.start()
                if len(threads) % 30 == 0:
                    for thread in threads[-30:]:
                        thread.join(timeout=8)
            for t in threads:
                t.join(timeout=10)
            finish_msg = f"\n{'='*40}\n[✓] اكتمل البحث العميق!\n[+] وجدنا الهدف في {found[0]} موقع من أصل {total}\n{'='*40}\n"
            Clock.schedule_once(lambda dt: setattr(results_widget, 'text', results_widget.text + finish_msg), 0)

        threading.Thread(target=run_all, daemon=True).start()


# ===================================================
# MAIN APP - التطبيق الرئيسي الكامل
# ===================================================
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.email_hunter = EmailHunter()
        self.ip_tracer = IPTracer()
        self.exif_analyzer = EXIFAnalyzer()
        self.phone_lookup = PhoneLookup()
        self.network_radar = NetworkRadar()
        self.deep_scraper = DeepWebScraper()

        root_layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        root_layout.add_widget(Label(
            text="AL-NISR OSINT MOBILE",
            font_size='30sp',
            color=(0, 1, 0.8, 1),
            size_hint_y=None, height=60
        ))

        self.tab_panel = TabbedPanel(do_default_tab=False, tab_width=130)

        # --- تاب 1: بحث اليوزرنيم (الاصلي) ---
        tab_user = TabbedPanelItem(text="Username")
        user_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.user_in = TextInput(hint_text="Target Username", multiline=False, size_hint_y=None, height=80)
        user_layout.add_widget(self.user_in)
        btn = Button(text="EXECUTE GLOBAL RECON", background_color=(1, 0, 0.2, 1), size_hint_y=None, height=100)
        btn.bind(on_press=self.start_scan)
        user_layout.add_widget(btn)
        self.results = TextInput(readonly=True, text="Ready for action, boss man...")
        user_layout.add_widget(self.results)
        tab_user.add_widget(user_layout)
        self.tab_panel.add_widget(tab_user)

        # --- تاب 2: فحص الايميل ---
        tab_email = TabbedPanelItem(text="Email")
        email_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.email_in = TextInput(hint_text="target@email.com", multiline=False, size_hint_y=None, height=80)
        email_layout.add_widget(self.email_in)
        email_btn = Button(text="PIERCE EMAIL", background_color=(0.8, 0, 0.8, 1), size_hint_y=None, height=100)
        email_btn.bind(on_press=self.start_email_scan)
        email_layout.add_widget(email_btn)
        self.email_results = TextInput(readonly=True, text="ادخل ايميل الهدف...")
        email_layout.add_widget(self.email_results)
        tab_email.add_widget(email_layout)
        self.tab_panel.add_widget(tab_email)

        # --- تاب 3: تعقب IP ---
        tab_ip = TabbedPanelItem(text="IP Trace")
        ip_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.ip_in = TextInput(hint_text="Enter Target IP...", multiline=False, size_hint_y=None, height=80)
        ip_layout.add_widget(self.ip_in)
        ip_btn = Button(text="TRACE IP NODE", background_color=(0, 0.5, 1, 1), size_hint_y=None, height=100)
        ip_btn.bind(on_press=self.start_ip_trace)
        ip_layout.add_widget(ip_btn)
        self.ip_results = TextInput(readonly=True, text="ادخل IP الهدف...")
        ip_layout.add_widget(self.ip_results)
        tab_ip.add_widget(ip_layout)
        self.tab_panel.add_widget(tab_ip)

        # --- تاب 4: تحليل الصور ---
        tab_exif = TabbedPanelItem(text="EXIF")
        exif_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.exif_path = TextInput(hint_text="مسار الصورة: /sdcard/photo.jpg", multiline=False, size_hint_y=None, height=80)
        exif_layout.add_widget(self.exif_path)
        exif_btn = Button(text="EXTRACT METADATA", background_color=(1, 0.5, 0, 1), size_hint_y=None, height=100)
        exif_btn.bind(on_press=self.start_exif)
        exif_layout.add_widget(exif_btn)
        self.exif_results = TextInput(readonly=True, text="ادخل مسار الصورة...")
        exif_layout.add_widget(self.exif_results)
        tab_exif.add_widget(exif_layout)
        self.tab_panel.add_widget(tab_exif)

        # --- تاب 5: فحص رقم الهاتف ---
        tab_phone = TabbedPanelItem(text="Phone")
        phone_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.phone_in = TextInput(hint_text="+964XXXXXXXXXX", multiline=False, size_hint_y=None, height=80)
        phone_layout.add_widget(self.phone_in)
        phone_btn = Button(text="ANALYZE NUMBER", background_color=(0, 0.8, 0.2, 1), size_hint_y=None, height=100)
        phone_btn.bind(on_press=self.start_phone)
        phone_layout.add_widget(phone_btn)
        self.phone_results = TextInput(readonly=True, text="ادخل رقم الهدف...")
        phone_layout.add_widget(self.phone_results)
        tab_phone.add_widget(phone_layout)
        self.tab_panel.add_widget(tab_phone)

        # --- تاب 6: رادار الشبكة (جديد) ---
        tab_net = TabbedPanelItem(text="Net Radar")
        net_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        net_layout.add_widget(Label(
            text="رادار الشبكة - اكتشاف الأجهزة المتصلة",
            size_hint_y=None, height=50, color=(0, 1, 1, 1)
        ))
        net_btn = Button(
            text="🔍 بدء مسح الشبكة",
            background_color=(0, 0.7, 1, 1),
            size_hint_y=None, height=100
        )
        net_btn.bind(on_press=self.start_net_scan)
        net_layout.add_widget(net_btn)
        self.net_results = TextInput(
            readonly=True,
            text="اضغط على الزر لبدء مسح الشبكة...\n",
            font_size='13sp'
        )
        net_layout.add_widget(self.net_results)
        tab_net.add_widget(net_layout)
        self.tab_panel.add_widget(tab_net)

        # --- تاب 7: صائد الديب ويب (جديد) ---
        tab_deep = TabbedPanelItem(text="Deep Hunt")
        deep_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        deep_layout.add_widget(Label(
            text="صائد الحسابات العميق - 100+ موقع",
            size_hint_y=None, height=50, color=(1, 0.3, 0.3, 1)
        ))
        self.deep_in = TextInput(
            hint_text="Username / Name / Email",
            multiline=False, size_hint_y=None, height=80
        )
        deep_layout.add_widget(self.deep_in)
        deep_btn = Button(
            text="🕷️ DEEP WEB HUNT",
            background_color=(0.8, 0, 0, 1),
            size_hint_y=None, height=100
        )
        deep_btn.bind(on_press=self.start_deep_hunt)
        deep_layout.add_widget(deep_btn)
        self.deep_results = TextInput(
            readonly=True,
            text="جاهز للصيد العميق...\n",
            font_size='13sp'
        )
        deep_layout.add_widget(self.deep_results)
        tab_deep.add_widget(deep_layout)
        self.tab_panel.add_widget(tab_deep)

        root_layout.add_widget(self.tab_panel)
        self.add_widget(root_layout)

    # === الكود الاصلي (Username Search) - بدون اي تغيير ===
    def start_scan(self, instance):
        target = self.user_in.text
        self.results.text = f"[*] Engaging nodes for: {target}\n"
        threading.Thread(target=self.run_logic, args=(target,)).start()

    def run_logic(self, target):
        sites = [
            "github.com/", "instagram.com/", "twitter.com/", "t.me/",
            "facebook.com/", "tiktok.com/@", "reddit.com/user/",
            "pinterest.com/", "linkedin.com/in/", "snapchat.com/add/",
            "twitch.tv/", "youtube.com/@", "medium.com/@",
            "vk.com/", "flickr.com/people/", "soundcloud.com/",
            "open.spotify.com/user/", "steamcommunity.com/id/",
            "behance.net/", "dribbble.com/", "deviantart.com/",
            "patreon.com/", "ko-fi.com/", "cash.app/$",
            "keybase.io/", "about.me/", "gitlab.com/",
            "bitbucket.org/", "hackerrank.com/", "leetcode.com/",
            "codepen.io/", "replit.com/@", "tryhackme.com/p/",
            "hackerone.com/", "bugcrowd.com/", "producthunt.com/@",
            "mastodon.social/@", "threads.net/@", "rumble.com/user/",
            "odysee.com/@", "dailymotion.com/", "vimeo.com/",
            "myspace.com/", "quora.com/profile/", "ask.fm/",
            "wattpad.com/user/", "goodreads.com/", "last.fm/user/",
            "mixcloud.com/", "slideshare.net/", "scribd.com/",
            "archive.org/details/@", "wikipedia.org/wiki/User:",
            "clubhouse.com/@", "signal.me/#p/", "line.me/ti/p/~"
        ]
        for s in sites:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                r = requests.get(f"https://www.{s}{target}", headers=headers, timeout=5)
                if r.status_code == 200:
                    if target.lower() in r.text.lower():
                        self.results.text += f"[+] FOUND: {s}{target}\n"
                    else:
                        self.results.text += f"[?] POSSIBLE: {s}{target}\n"
            except:
                pass
        self.results.text += "\n[✓] MISSION COMPLETE."

    def start_email_scan(self, instance):
        email = self.email_in.text
        self.email_results.text = f"[*] جاري فحص: {email}\n{'='*40}\n"
        threading.Thread(target=self.run_email, args=(email,)).start()

    def run_email(self, email):
        results = self.email_hunter.check_email(email)
        for line in results:
            self.email_results.text += line + "\n"
        self.email_results.text += f"\n{'='*40}\n[✓] فحص الايميل اكتمل."

    def start_ip_trace(self, instance):
        ip = self.ip_in.text
        self.ip_results.text = f"[*] جاري تعقب: {ip}\n"
        threading.Thread(target=self.run_ip, args=(ip,)).start()

    def run_ip(self, ip):
        results = self.ip_tracer.trace(ip)
        for line in results:
            self.ip_results.text += line + "\n"
        self.ip_results.text += "\n[✓] تعقب IP اكتمل."

    def start_exif(self, instance):
        path = self.exif_path.text
        self.exif_results.text = f"[*] جاري تحليل: {path}\n"
        threading.Thread(target=self.run_exif, args=(path,)).start()

    def run_exif(self, path):
        results = self.exif_analyzer.analyze(path)
        for line in results:
            self.exif_results.text += line + "\n"
        self.exif_results.text += "\n[✓] تحليل الصورة اكتمل."

    def start_phone(self, instance):
        phone = self.phone_in.text
        self.phone_results.text = f"[*] جاري تحليل: {phone}\n"
        threading.Thread(target=self.run_phone, args=(phone,)).start()

    def run_phone(self, phone):
        results = self.phone_lookup.lookup(phone)
        for line in results:
            self.phone_results.text += line + "\n"
        self.phone_results.text += "\n[✓] تحليل الرقم اكتمل."

    # === ميزة 7: رادار الشبكة (جديد) ===
    def start_net_scan(self, instance):
        self.net_results.text = "[*] تشغيل رادار الشبكة...\n"
        self.network_radar.start_scan(self.net_results)

    # === ميزة 8: صائد الديب ويب (جديد) ===
    def start_deep_hunt(self, instance):
        target = self.deep_in.text
        if not target:
            self.deep_results.text = "[!] ادخل اسم الهدف اول!\n"
            return
        self.deep_results.text = f"[*] بدء الصيد العميق للهدف: {target}\n{'='*40}\n"
        self.deep_scraper.deep_hunt(target, self.deep_results)


class AlNisrApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenu(name='menu'))
        return sm


if __name__ == '__main__':
    AlNisrApp().run()
