import os
import telebot
import re
import base64
import requests
from urllib.parse import urlparse, parse_qs

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ALLOWED_USERNAME = os.getenv("ALLOWED_USERNAME")

bot = telebot.TeleBot(TOKEN)

def is_allowed_user(message):
    return message.from_user.username == ALLOWED_USERNAME

def get_geoip_country(ip):
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}")
        data = resp.json()
        country_code = data.get("countryCode", "")
        country = data.get("country", "ناشناخته")
        emoji = {
            "IR": "🇮🇷", "DE": "🇩🇪", "US": "🇺🇸", "RU": "🇷🇺",
            "NL": "🇳🇱", "FR": "🇫🇷", "TR": "🇹🇷", "GB": "🇬🇧",
            "JP": "🇯🇵", "SG": "🇸🇬"
        }.get(country_code, "🌍")
        return f"{emoji} {country}"
    except:
        return "🌍 ناشناس"

def extract_country_from_v2ray(link):
    try:
        if link.startswith("vmess://"):
            decoded = base64.b64decode(link[8:] + "===").decode("utf-8", errors="ignore")
            match = re.search(r'"(add|host|sni)"\s*:\s*"([^"]+)"', decoded)
            if match:
                host = match.group(2).lower()
                return match_country_from_host(host)
        elif link.startswith("vless://"):
            parsed = urlparse(link)
            host = (parsed.hostname or "").lower()
            return match_country_from_host(host)
    except:
        pass
    return "🌍 ناشناس"

def match_country_from_host(host):
    mapping = {
        ".ir": "🇮🇷 ایران",
        ".de": "🇩🇪 آلمان",
        ".us": "🇺🇸 آمریکا",
        ".ru": "🇷🇺 روسیه",
        ".nl": "🇳🇱 هلند",
        ".fr": "🇫🇷 فرانسه",
        ".tr": "🇹🇷 ترکیه",
        ".uk": "🇬🇧 انگلیس",
        ".jp": "🇯🇵 ژاپن",
        ".sg": "🇸🇬 سنگاپور"
    }
    for key, val in mapping.items():
        if key in host:
            return val
    return "🌍 ناشناس"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_allowed_user(message):
        bot.reply_to(message, "❌ دسترسی ندارید.")
        return
    bot.reply_to(message, "سلام! لینک V2Ray یا پروکسی‌تو بفرست تا برات پست بسازم.")

@bot.message_handler(commands=['add'])
def ask_link(message):
    if not is_allowed_user(message):
        bot.reply_to(message, "❌ دسترسی ندارید.")
        return
    bot.reply_to(message, "لینک رو بفرست:")

@bot.message_handler(func=lambda m: True)
def make_post(message):
    if not is_allowed_user(message):
        bot.reply_to(message, "❌ دسترسی ندارید.")
        return

    link = message.text.strip()
    markup = telebot.types.InlineKeyboardMarkup()

    if link.startswith(("vmess://", "vless://")):
        country = extract_country_from_v2ray(link)
        post = f"""
🚀 اتصال امن و پرسرعت V2Ray فعال شد!

🌐 موقعیت سرور: {country}
🔐 پروتکل: V2Ray
📡 وضعیت: آنلاین و تست‌شده
⏰ اعتبار: ۲۴ ساعت

📎 لینک اتصال:
{link}

منتشر شده توسط: HMProxyNet
#HMProxyNet #V2ray #SecureVPN
        """
        btn = telebot.types.InlineKeyboardButton("📋 کپی لینک", url=f"https://t.me/share/url?url={link}")
        markup.add(btn)

    elif link.startswith("tg://proxy?"):
        params = parse_qs(urlparse(link).query)
        ip = params.get("server", [""])[0]
        country = get_geoip_country(ip) if ip else "🌍 ناشناس"
        post = f"""
🌐 پروکسی پرسرعت برای تلگرام

🌍 موقعیت: {country}
📶 وضعیت: فعال

🔗 لینک اتصال:
{link}

منتشر شده توسط: HMProxyNet
#HMProxyNet #Proxy #Telegram
        """
        btn = telebot.types.InlineKeyboardButton("📲 اتصال سریع", url=link)
        markup.add(btn)

    else:
        bot.reply_to(message, "❌ لینک نامعتبره")
        return

    bot.send_message(CHANNEL_ID, post, reply_markup=markup)
    bot.reply_to(message, "✅ پست ارسال شد به کانال.")

bot.infinity_polling()
