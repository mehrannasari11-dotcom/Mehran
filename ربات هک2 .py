
import os
import threading
import json
import time
import re
import telebot
from telebot import types

# مشخصات اصلی ربات شما
BOT_TOKEN = "8966204193:AAE-H3YbIY4EMo8KiFwKqQzogs6xnVmJJzA"
ADMIN_ID = 6720524363
DB_FILE = "users_database4.json"
ITEMS_FILE = "bot_items.json"
ADMINS_FILE = "admins.json"

# بارگذاری ادمین‌ها
admins_list = [ADMIN_ID]
if os.path.exists(ADMINS_FILE):
    with open(ADMINS_FILE, "r", encoding="utf-8") as f:
        try: admins_list = json.load(f)
        except: admins_list = [ADMIN_ID]
if ADMIN_ID not in admins_list:
    admins_list.append(ADMIN_ID)

def save_admins():
    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
        json.dump(admins_list, f, ensure_ascii=False, indent=4)

def is_admin(user_id):
    return user_id in admins_list

# بارگذاری آیتم‌ها از فایل جداگانه
bot_items = {}
if os.path.exists(ITEMS_FILE):
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        try: bot_items = json.load(f)
        except: bot_items = {}

def save_items():
    with open(ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(bot_items, f, ensure_ascii=False, indent=4)

# متون چندزبانه سیستم (بدون پشتو)
LANG_TEXTS = {
    "select_lang": "لطفاً زبان خود را انتخاب کنید / Please choose your language:",
    "welcome": {
        "fa": "سلام! به ربات بزرگ ابزارهای هک و شماره مجازی خوش آمدید. از منوی زیر استفاده کنید:",
        "en": "Hello! Welcome to the Great Hacking Tools & Virtual Numbers Bot. Use the menu below:"
    },
    "btn_apps": {"fa": "📥 بخش برنامه‌ها", "en": "📥 Apps Section"},
    "btn_tutorials": {"fa": "🎥 بخش آموزش‌ها", "en": "🎥 Tutorials Section"},
    "btn_links": {"fa": "🤖 بخش ربات‌ها و لینک‌ها", "en": "🤖 Bots & Links"},
    "btn_daily": {"fa": "🎁 اطلاعات من و سکه‌ها", "en": "🎁 My Info & Coins"},
    "btn_support": {"fa": "📞 پشتیبانی مستقیم", "en": "📞 Direct Support"},
    "btn_changelang": {"fa": "🌐 تغییر زبان / Change Language", "en": "🌐 تغییر زبان / Change Language"},
    "btn_colorizer": {"fa": "🎨 بخش رنگ کردن دکمه‌ها", "en": "🎨 Button Colorizer Section"},
    "daily_success": {
        "fa": "🎁 تبریک! تعداد 2 امتیاز روزانه به شما تعلق گرفت.",
        "en": "🎁 Congratulations! You received 2 daily points."
    },
    "daily_fail": {
        "fa": "❌ شما امروز هدیه خود را دریافت کرده‌اید!",
        "en": "❌ You have already claimed your bonus today!"
    },
    "insufficient_points": {
        "fa": "❌ امتیاز شما کافی نیست!",
        "en": "❌ Insufficient points!"
    },
    "ask_buy": {
        "fa": "⚠️ آیا مطمئن هستید که می‌خواهید محصول **{}** را در ازای **{} امتیاز** دریافت کنید؟",
        "en": "⚠️ Are you sure you want to get **{}** for **{} points**?"
    },
    "security_warn": {
        "fa": "\n\n⚠️ هشدار امنیت: این پیام به دلیل حفظ امنیت بعد از ۳۰ ثانیه خودکار حذف خواهد شد!",
        "en": "\n\n⚠️ Security Warning: This message will be auto-deleted after 30 seconds for security reasons!"
    },
    "support_msg": {
        "fa": "✍️ لطفا پیام خود را بنویسید:\n\nربات پیام شما را مستقیم به دست مدیریت می‌رساند.",
        "en": "✍️ Please write your message:\n\nThe bot will deliver it directly to management."
    },
    "support_success": {
        "fa": "✅ پیام شما مستقیماً ارسال شد.",
        "en": "✅ Your message has been successfully sent."
    }
}

bot = telebot.TeleBot(BOT_TOKEN)
users_db = {}
user_state = {}
user_temp_data = {}
BOT_STATUS_FILE = "bot_status.json"
bot_status = {"active": True}

if os.path.exists(BOT_STATUS_FILE):
    with open(BOT_STATUS_FILE, "r") as f:
        try: bot_status = json.load(f)
        except: bot_status = {"active": True}

def save_status():
    with open(BOT_STATUS_FILE, "w") as f: json.dump(bot_status, f)

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        try: users_db = json.load(f)
        except: users_db = {}

def save_db():
    with open(DB_FILE, "w") as f: json.dump(users_db, f, indent=4)

def get_user_data(user_id):
    uid = str(user_id)
    if uid not in users_db:
        users_db[uid] = {"points": 100, "referred_by": None, "last_daily": None, "status": "normal", "referrals_count": 0, "lang": None}
        save_db()
    if "lang" not in users_db[uid]:
        users_db[uid]["lang"] = None
    return users_db[uid]

def is_bot_off(user_id):
    if not is_admin(user_id) and not bot_status.get("active", True):
        return True
    return False

def delayed_delete(chat_id, message_id, delay=30):
    def target():
        time.sleep(delay)
        try: bot.delete_message(chat_id, message_id)
        except: pass
    threading.Thread(target=target).start()

def lang_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🇦🇫 دری", callback_data="setlang_fa", style="primary"),
        types.InlineKeyboardButton("🇺🇸 English", callback_data="setlang_en", style="success")
    )
    return markup

def main_keyboard(lang):
    if not lang: lang = "fa"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(LANG_TEXTS["btn_tutorials"][lang], callback_data="menu_tutorials", style="primary"),
        types.InlineKeyboardButton(LANG_TEXTS["btn_apps"][lang], callback_data="menu_apps", style="success"),
        types.InlineKeyboardButton(LANG_TEXTS["btn_daily"][lang], callback_data="menu_daily", style="success"),
        types.InlineKeyboardButton(LANG_TEXTS["btn_links"][lang], callback_data="menu_links", style="success")
    )
    markup.add(
        types.InlineKeyboardButton(LANG_TEXTS["btn_support"][lang], callback_data="menu_support", style="success"),
        types.InlineKeyboardButton(LANG_TEXTS["btn_changelang"][lang], callback_data="menu_changelang", style="primary")
    )
    markup.add(
        types.InlineKeyboardButton(LANG_TEXTS["btn_colorizer"][lang], callback_data="menu_colorizer", style="danger")
    )
    return markup

def apps_keyboard(lang):
    if not lang: lang = "fa"
    markup = types.InlineKeyboardMarkup(row_width=1)
    has_item = False
    for item_id, info in bot_items.items():
        if info["type"] == "file":
            has_item = True
            name = info["name"][lang] if isinstance(info["name"], dict) else info["name"]
            pt_str = "امتیاز" if lang == "fa" else "Points"
            markup.add(types.InlineKeyboardButton(f"🔵 {name} | {info['points']} {pt_str}", callback_data=f"ask_{item_id}", style="primary"))
    if not has_item:
        markup.add(types.InlineKeyboardButton("❌ این بخش در حال حاضر خالی است.", callback_data="empty_notice", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main", style="danger"))
    return markup

def tutorials_keyboard(lang):
    if not lang: lang = "fa"
    markup = types.InlineKeyboardMarkup(row_width=1)
    has_item = False
    for item_id, info in bot_items.items():
        if info["type"] == "tutorial":
            has_item = True
            name = info["name"][lang] if isinstance(info["name"], dict) else info["name"]
            pt_str = "امتیاز" if lang == "fa" else "Points"
            markup.add(types.InlineKeyboardButton(f"🟢 {name} | {info['points']} {pt_str}", callback_data=f"ask_{item_id}", style="primary"))
    if not has_item:
        markup.add(types.InlineKeyboardButton("❌ این بخش در حال حاضر خالی است.", callback_data="empty_notice", style="danger"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main", style="danger"))
    return markup

def links_keyboard(lang):
    if not lang: lang = "fa"
    markup = types.InlineKeyboardMarkup(row_width=1)
    has_item = False
    for item_id, info in bot_items.items():
        if info["type"] == "link":
            has_item = True
            name = info["name"][lang] if isinstance(info["name"], dict) else info["name"]
            pt_str = "امتیاز" if lang == "fa" else "Points"
            markup.add(types.InlineKeyboardButton(f"🔴 {name} | {info['points']} {pt_str}", callback_data=f"ask_{item_id}", style="primary"))
    if not has_item:
        markup.add(types.InlineKeyboardButton("❌ این بخش در حال حاضر خالی است.", callback_data="empty_notice", style="primary"))
    markup.add(types.InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main", style="danger"))
    return markup

@bot.message_handler(commands=['turn'])
def toggle_bot(message):
    if not is_admin(message.from_user.id): return
    bot_status["active"] = not bot_status.get("active", True)
    save_status()
    status_str = "🟢 روشن و فعال" if bot_status["active"] else "🔴 خاموش (آف)"
    bot.reply_to(message, f"⚙️ وضعیت ربات تغییر یافت به: {status_str}")

@bot.message_handler(commands=['add'])
def add_new_admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ فقط مالک اصلی ربات می‌تواند این بخش را مدیریت کند.")
        return

    total_admins = len(admins_list)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ افزودن ادمین جدید", callback_data="admin_manage_add", style="success"),
        types.InlineKeyboardButton("🗑️ حذف ادمین", callback_data="admin_manage_remove", style="danger"),
        types.InlineKeyboardButton("📋 لیست ادمین‌ها", callback_data="admin_manage_list", style="primary"),
        types.InlineKeyboardButton("🔙 بازگشت به پنل مدیریت", callback_data="admin_back", style="danger")
    )

    text = (
        f"👑 **بخش مدیریت ادمین‌های ربات:**\n\n"
        f"👥 تعداد کل ادمین‌های فعلی: **{total_admins} نفر**\n\n"
        f"لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
    )
    bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_bot_off(user_id):
        bot.reply_to(message, "❌ ربات در حال حاضر خاموش است.")
        return

    try:
        username_str = f"@{message.from_user.username}" if message.from_user.username else "ندارد"
        profile_text = f"👤 **اطلاعات حساب کاربری شما:**\n\n🆔 آیدی عددی: `{user_id}`\n🔗 یوزرنیم: {username_str}\n نام: {message.from_user.first_name}"
        photos = bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            bot.send_photo(user_id, file_id, caption=profile_text, parse_mode="Markdown")
        else:
            bot.send_message(user_id, profile_text, parse_mode="Markdown")
    except Exception as e:
        pass

    parts = message.text.split()
    is_new = str(user_id) not in users_db
    user_data = get_user_data(user_id)

    if is_new and len(parts) > 1 and parts[1].isdigit() and int(parts[1]) != user_id:
        referrer_id = int(parts[1])
        ref_data = get_user_data(referrer_id)
        user_data["referred_by"] = referrer_id
        ref_data["points"] += 2
        ref_data["referrals_count"] = ref_data.get("referrals_count", 0) + 1
        save_db()
        try: bot.send_message(referrer_id, "🎉 یک کاربر از طریق لینک شما وارد شد و 2 امتیاز دریافت کردید!")
        except: pass

    user_data["lang"] = None
    save_db()
    bot.send_message(user_id, LANG_TEXTS["select_lang"], reply_markup=lang_keyboard())

@bot.message_handler(commands=['setpoint'])
def set_user_points(message):
    if not is_admin(message.from_user.id): return
    try:
        parts = message.text.split()
        if len(parts) == 3:
            target_id = int(parts[1])
            points_change = int(parts[2])
            user_data = get_user_data(target_id)
            old_points = user_data["points"]
            user_data["points"] += points_change
            if user_data["points"] < 0: user_data["points"] = 0
            new_points = user_data["points"]
            save_db()
            bot.reply_to(message, f"🟢 **عملیات موفقیت‌آمیز بود!**\n\n🆔 کاربر: `{target_id}`\n📥 تغییرات: {points_change:+} امتیاز\n💰 امتیاز قبلی: {old_points}\n💳 امتیاز جدید: {new_points}", parse_mode="Markdown")
            try:
                notify_msg = f"🔔 **اطلاعیه حساب شما:**\n\nحساب شما توسط مدیریت تغییر یافت:\n💳 کل امتیاز فعلی شما: **{new_points} امتیاز**"
                bot.send_message(target_id, notify_msg, parse_mode="Markdown")
            except: pass
    except Exception as e:
        bot.reply_to(message, "🔴 **خطا در انجام عملیات!**")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if not is_admin(message.from_user.id): return
    total_users = len(users_db)
    current_state = "🟢 روشن و فعال" if bot_status.get("active", True) else "🔴 خاموش (آف شده)"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("➕ افزودن برنامه / ربات / آموزش جدید", callback_data="admin_add_item", style="success"),
        types.InlineKeyboardButton("🗑️ حذف برنامه، ربات یا آموزش", callback_data="admin_delete_item", style="danger"),
        types.InlineKeyboardButton("📝 ارسال پیام دلخواه به همه", callback_data="admin_broadcast", style="primary"),
        types.InlineKeyboardButton("🔄 فوروارد پیام به همه", callback_data="admin_forward", style="primary")
    )
    panel_text = f"📊 **منوی مدیریت ربات:**\n\n🟢 کل کاربران فعال: **{total_users} نفر**\n🔴 وضعیت کنونی سیستم: **{current_state}**"
    bot.reply_to(message, panel_text, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    if is_bot_off(user_id):
        bot.answer_callback_query(call.id, "❌ ربات خاموش است.", show_alert=True)
        return
    user_data = get_user_data(user_id)
    lang = user_data["lang"] if user_data["lang"] else "fa"

    if call.data.startswith("setlang_"):
        selected_lang = call.data.replace("setlang_", "")
        user_data["lang"] = selected_lang
        save_db()
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(user_id, LANG_TEXTS["welcome"][selected_lang], reply_markup=main_keyboard(selected_lang))
        bot.answer_callback_query(call.id, "Language updated")
        return

    if call.data == "menu_apps":
        bot.edit_message_text("👇 Apps / برنامه‌ها:", call.message.chat.id, call.message.message_id, reply_markup=apps_keyboard(lang))
        return
    elif call.data == "menu_tutorials":
        bot.edit_message_text("👇 Tutorials / آموزش‌ها:", call.message.chat.id, call.message.message_id, reply_markup=tutorials_keyboard(lang))
        return
    elif call.data == "menu_links":
        bot.edit_message_text("👇 Links & Bots / ربات‌ها و لینک‌ها:", call.message.chat.id, call.message.message_id, reply_markup=links_keyboard(lang))
        return
    elif call.data == "menu_colorizer":
        user_state[user_id] = "colorizer_wait_file"
        user_temp_data[user_id] = {"color_mode": None, "custom_colors": {}}
        bot.send_message(user_id, "📥 لطفاً سورس‌کد یا فایل ربات خود را بفرستید تا دکمه‌های شیشه‌ای آن رنگی شوند:")
        bot.answer_callback_query(call.id)
        return
    elif call.data == "menu_daily":
        invite_link = f"https://t.me/Shahidjankhanbot?start={user_id}"
        referrals = user_data.get("referrals_count", 0)
        current_time = time.time()
        last_daily = user_data.get("last_daily")

        daily_status_text = ""
        if last_daily is None or (current_time - last_daily) >= 86400:
            user_data["points"] += 2
            user_data["last_daily"] = current_time
            save_db()
            daily_status_text = "\n🎁 هدیه روزانه شما (2 امتیاز) دریافت شد!"
        else:
            daily_status_text = "\n❌ هدیه روزانه امروز خود را قبلاً دریافت کرده‌اید."

        if lang == "fa":
            info_text = f"📊 **اطلاعات حساب و سکه‌های شما:**\n\n💰 امتیاز فعلی: **{user_data['points']}**\n👥 تعداد دعوت‌ها: **{referrals} نفر**{daily_status_text}\n\n🔗 لینک دعوت:\n{invite_link}"
        else:
            info_text = f"📊 **Account Info & Coins:**\n\n💰 Current Points: **{user_data['points']}**\n👥 Total Invites: **{referrals}**{daily_status_text}\n\n🔗 Referral Link:\n{invite_link}"

        bot.send_message(user_id, info_text, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return
    elif call.data == "menu_support":
        user_state[user_id] = "waiting_support"
        bot.send_message(user_id, LANG_TEXTS["support_msg"][lang])
        bot.answer_callback_query(call.id)
        return
    elif call.data == "menu_changelang":
        bot.send_message(user_id, LANG_TEXTS["select_lang"], reply_markup=lang_keyboard())
        bot.answer_callback_query(call.id)
        return
    elif call.data == "empty_notice":
        bot.answer_callback_query(call.id, "❌ این بخش در حال حاضر خالی است.", show_alert=True)
        return
    elif call.data == "back_main":
        try:
            bot.edit_message_text(LANG_TEXTS["welcome"][lang], call.message.chat.id, call.message.message_id, reply_markup=main_keyboard(lang))
        except:
            bot.send_message(call.message.chat.id, LANG_TEXTS["welcome"][lang], reply_markup=main_keyboard(lang))
        return

    if call.data.startswith("color_mode_"):
        mode = call.data.replace("color_mode_", "")
        if user_id in user_temp_data:
            user_temp_data[user_id]["color_mode"] = mode
            if mode in ["all_red", "all_blue", "all_green", "all_rainbow"]:
                # رنگارنگ کردن هوشمند تمام دکمه‌های پیدا شده در سورس کد کاربر
                file_content = user_temp_data[user_id].get("file_content", "")
                buttons = user_temp_data[user_id].get("buttons_list", [])

                for idx, btn in enumerate(buttons):
                    if mode == "all_red": emoji = "🔴"
                    elif mode == "all_blue": emoji = "🔵"
                    elif mode == "all_green": emoji = "🟢"
                    else: emoji = "🔴" if idx % 3 == 0 else (" 🔵" if idx % 3 == 1 else "🟢")

                    if not btn.startswith(("🔴", "🔵", "🟢")):
                        file_content = file_content.replace(f'"{btn}"', f'"{emoji} {btn}"').replace(f"'{btn}'", f"'{emoji} {btn}'")

                out_filename = f"colored_bot_{user_id}.py"
                with open(out_filename, "w", encoding="utf-8") as f_out:
                    f_out.write(file_content)

                caption_text = "✨ سورس‌کد شما با موفقیت رنگ‌آمیزی و کاملاً رنگی شد!" + LANG_TEXTS["security_warn"][lang]
                with open(out_filename, "rb") as f_send:
                    sent_msg = bot.send_document(user_id, f_send, caption=caption_text)

                if sent_msg:
                    delayed_delete(user_id, sent_msg.message_id, 30)
                try: os.remove(out_filename)
                except: pass

                if user_id in user_state: del user_state[user_id]
                if user_id in user_temp_data: del user_temp_data[user_id]
                bot.answer_callback_query(call.id, "✅ ربات شما با موفقیت رنگی شد!")
            elif mode == "custom":
                buttons = user_temp_data[user_id].get("buttons_list", [])
                if buttons:
                    user_temp_data[user_id]["current_btn_idx"] = 0
                    btn_name = buttons[0]
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    markup.add(
                        types.InlineKeyboardButton("🔴 سرخ", callback_data="colpick_red", style="danger"),
                        types.InlineKeyboardButton("🔵 آبی", callback_data="colpick_blue", style="success"),
                        types.InlineKeyboardButton("🟢 سبز", callback_data="colpick_green", style="primary")
                    )
                    bot.edit_message_text(f"🎨 دکمه: **{btn_name}**\nلطفاً رنگ مورد نظر را انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
                else:
                    bot.answer_callback_query(call.id, "❌ هیچ دکمه‌ای در فایل یافت نشد!", show_alert=True)
        return

    if call.data.startswith("colpick_"):
        color = call.data.replace("colpick_", "")
        if user_id in user_temp_data:
            idx = user_temp_data[user_id].get("current_btn_idx", 0)
            buttons = user_temp_data[user_id].get("buttons_list", [])
            btn_name = buttons[idx]
            user_temp_data[user_id]["custom_colors"][btn_name] = color

            idx += 1
            user_temp_data[user_id]["current_btn_idx"] = idx
            if idx < len(buttons):
                next_btn = buttons[idx]
                markup = types.InlineKeyboardMarkup(row_width=3)
                markup.add(
                    types.InlineKeyboardButton("🔴 سرخ", callback_data="colpick_red", style="danger"),
                    types.InlineKeyboardButton("🔵 آبی", callback_data="colpick_blue", style="primary"),
                    types.InlineKeyboardButton("🟢 سبز", callback_data="colpick_green", style="success")
                )
                bot.edit_message_text(f"🎨 دکمه: **{next_btn}**\nلطفاً رنگ مورد نظر را انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
            else:
                file_content = user_temp_data[user_id].get("file_content", "")
                custom_colors = user_temp_data[user_id].get("custom_colors", {})

                for btn, col in custom_colors.items():
                    emoji = "🔴" if col == "red" else ("🔵" if col == "blue" else "🟢")
                    file_content = file_content.replace(f'"{btn}"', f'"{emoji} {btn}"').replace(f"'{btn}'", f"'{emoji} {btn}'")

                out_filename = f"colored_bot_{user_id}.py"
                with open(out_filename, "w", encoding="utf-8") as f_out:
                    f_out.write(file_content)

                caption_text = "✨ سورس‌کد شما با موفقیت سفارشی‌سازی و رنگ‌آمیزی شد!" + LANG_TEXTS["security_warn"][lang]
                with open(out_filename, "rb") as f_send:
                    sent_msg = bot.send_document(user_id, f_send, caption=caption_text)

                if sent_msg:
                    delayed_delete(user_id, sent_msg.message_id, 30)
                try: os.remove(out_filename)
                except: pass

                try: bot.delete_message(call.message.chat.id, call.message.message_id)
                except: pass

                if user_id in user_state: del user_state[user_id]
                if user_id in user_temp_data: del user_temp_data[user_id]
                bot.answer_callback_query(call.id, "✅ با موفقیت رنگ شد!")
        return

    if call.data == "admin_manage_add" and user_id == ADMIN_ID:
        user_state[user_id] = "waiting_new_admin_id"
        bot.send_message(user_id, "✍️ لطفاً آیدی عددی (User ID) ادمین جدید را بفرستید:")
        bot.answer_callback_query(call.id)
        return

    if call.data == "admin_manage_remove" and user_id == ADMIN_ID:
        if len(admins_list) <= 1:
            bot.answer_callback_query(call.id, "⚠️ هیچ ادمین دیگری برای حذف وجود ندارد!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for adm in admins_list:
            if adm != ADMIN_ID:
                markup.add(types.InlineKeyboardButton(f"🗑️ حذف ادمین: {adm}", callback_data=f"remove_admin_{adm}", style="danger"))
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back", style="danger"))
        bot.edit_message_text("🗑️ لطفاً ادمینی که می‌خواهید حذف کنید را انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("remove_admin_") and user_id == ADMIN_ID:
        rem_id = int(call.data.replace("remove_admin_", ""))
        if rem_id in admins_list and rem_id != ADMIN_ID:
            admins_list.remove(rem_id)
            save_admins()
            bot.answer_callback_query(call.id, "✅ ادمین با موفقیت حذف شد!", show_alert=True)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
        return

    if call.data == "admin_manage_list" and user_id == ADMIN_ID:
        list_text = "📋 **لیست ادمین‌های ربات:**\n\n"
        for idx, adm in enumerate(admins_list, 1):
            role = "👑 (مالک اصلی)" if adm == ADMIN_ID else "🛡️ (ادمن)"
            list_text += f"{idx}. `{adm}` {role}\n"
        list_text += f"\n👥 تعداد کل ادمین‌ها: **{len(admins_list)} نفر**"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back", style="danger"))
        bot.edit_message_text(list_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if call.data == "admin_delete_item" and is_admin(user_id):
        if not bot_items:
            bot.answer_callback_query(call.id, "❌ هیچ آیتمی برای حذف وجود ندارد!", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for item_id, info in bot_items.items():
            name = info["name"]["fa"] if isinstance(info["name"], dict) else info["name"]
            markup.add(types.InlineKeyboardButton(f"🗑️ حذف: {name}", callback_data=f"delitem_{item_id}", style="danger"))
        markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back", style="danger"))
        bot.edit_message_text("🗑️ لطفاً برنامه‌ای، ربات یا آموزشی را که می‌خواهید حذف کنید انتخاب کنید:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("delitem_") and is_admin(user_id):
        item_id = call.data.replace("delitem_", "")
        if item_id in bot_items:
            del bot_items[item_id]
            save_items()
            bot.answer_callback_query(call.id, "✅ با موفقیت حذف شد!", show_alert=True)
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
        return

    if call.data == "admin_back" and is_admin(user_id):
        total_users = len(users_db)
        current_state = "🟢 روشن و فعال" if bot_status.get("active", True) else "🔴 خاموش (آف شده)"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("➕ افزودن برنامه / ربات / آموزش جدید", callback_data="admin_add_item", style="danger"),
            types.InlineKeyboardButton("🗑️ حذف برنامه، ربات یا آموزش", callback_data="admin_delete_item", style="danger"),
            types.InlineKeyboardButton("📝 ارسال پیام دلخواه به همه", callback_data="admin_broadcast", style="primary"),
            types.InlineKeyboardButton("🔄 فوروارد پیام به همه", callback_data="admin_forward", style="primary")
        )
        panel_text = f"📊 **منوی مدیریت ربات:**\n\n🟢 کل کاربران فعال: **{total_users} نفر**\n🔴 وضعیت کنونی سیستم: **{current_state}**"
        try:
            bot.edit_message_text(panel_text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except:
            bot.send_message(call.message.chat.id, panel_text, reply_markup=markup, parse_mode="Markdown")
        bot.answer_callback_query(call.id)
        return

    if call.data == "admin_add_item" and is_admin(user_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📥 برنامه (فایل)", callback_data="addtype_file", style="success"),
            types.InlineKeyboardButton("🔗 سایت / ربات (لینک)", callback_data="addtype_link", style="primary"),
            types.InlineKeyboardButton("🎥 آموزش (ویدیو / عکس)", callback_data="addtype_tutorial", style="success")
        )
        bot.send_message(user_id, "📁 لطفاً بخش مورد نظر برای افزودن آیتم را انتخاب کنید:", reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("addtype_") and is_admin(user_id):
        itype = call.data.replace("addtype_", "")
        user_temp_data[user_id] = {"type": itype}
        user_state[user_id] = "add_item_get_name"
        bot.send_message(user_id, "✍️ لطفاً نام دکمه را برای این آیتم وارد کنید (مثلا: آموزش جدید 🎥):")
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("admin_") and is_admin(user_id):
        if call.data == "admin_broadcast":
            user_state[user_id] = "waiting_broadcast"
            bot.send_message(user_id, "✍️ لطفاً متن پیام خود را بفرستید:")
            bot.answer_callback_query(call.id)
        elif call.data == "admin_forward":
            user_state[user_id] = "waiting_forward"
            bot.send_message(user_id, "↩️ لطفاً پیام خود را اینجا فوروارد کنید:")
            bot.answer_callback_query(call.id)
        return

    if call.data.startswith("ask_"):
        item_id = call.data.replace("ask_", "")
        if item_id in bot_items:
            item = bot_items[item_id]
            name = item["name"][lang] if isinstance(item["name"], dict) else item["name"]
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("✅ Yes / بله", callback_data=f"buy_{item_id}", style="primary"),
                types.InlineKeyboardButton("❌ No / لغو", callback_data="cancel_buy", style="danger")
            )
            ask_msg = LANG_TEXTS["ask_buy"][lang].format(name, item["points"])
            bot.send_message(user_id, ask_msg, reply_markup=markup, parse_mode="Markdown")
            bot.answer_callback_query(call.id)
        return

    if call.data == "cancel_buy":
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.answer_callback_query(call.id, "Canceled.")
        return

    if call.data.startswith("buy_"):
        item_id = call.data.replace("buy_", "")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        if item_id in bot_items:
            item = bot_items[item_id]
            if user_data["points"] >= item["points"]:
                user_data["points"] -= item["points"]
                save_db()
                bot.answer_callback_query(call.id, "📥 Sending...")
                sent_msg = None
                if item["type"] == "file":
                    caption_text = item.get("caption", "✅ Product") + LANG_TEXTS["security_warn"][lang]
                    try: sent_msg = bot.send_document(user_id, item["file_id"], caption=caption_text)
                    except: bot.send_message(user_id, "Error sending file.")
                elif item["type"] == "tutorial":
                    caption_text = item.get("caption", "🎥 Tutorial") + LANG_TEXTS["security_warn"][lang]
                    if item["media_type"] == "video":
                        try: sent_msg = bot.send_video(user_id, item["file_id"], caption=caption_text)
                        except: bot.send_message(user_id, "Error sending video.")
                    elif item["media_type"] == "photo":
                        try: sent_msg = bot.send_photo(user_id, item["file_id"], caption=caption_text)
                        except: bot.send_message(user_id, "Error sending photo.")
                elif item["type"] == "link":
                    msg_text = f"🔗 {item['username']}" + LANG_TEXTS["security_warn"][lang]
                    sent_msg = bot.send_message(user_id, msg_text)
                if sent_msg:
                    delayed_delete(user_id, sent_msg.message_id, 30)
            else:
                bot.answer_callback_query(call.id, LANG_TEXTS["insufficient_points"][lang], show_alert=True)

@bot.message_handler(content_types=['document', 'photo', 'video', 'audio'], func=lambda message: is_admin(message.from_user.id) and user_state.get(message.from_user.id) != "colorizer_wait_file")
def get_file_id(message):
    file_id = None
    file_type = ""

    if message.document:
        file_id = message.document.file_id
        file_type = "Document / App"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "Photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "Video"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "Audio"

    if file_id:
        text_reply = f"🟢 **فایل با موفقیت دریافت شد!**\n\n" \
                     f"📁 نوع فایل: `{file_type}`\n" \
                     f"🆔 شناسه فایل (`file_id`):\n`{file_id}`"
        bot.reply_to(message, text_reply, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document', 'voice', 'video'])
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text if message.text else ""

    if is_admin(user_id) and message.reply_to_message:
        try:
            first_line = message.reply_to_message.text if message.reply_to_message.text else message.reply_to_message.caption
            target_user_id = int(first_line.split("\n")[0].replace("📥 پیام از کاربر: ", ""))
            bot.send_message(target_user_id, f"📥 **پاسخ پشتیبانی:**\n\n{text}")
            bot.reply_to(message, "✅ ارسال شد.")
            return
        except: pass

    if is_bot_off(user_id): return
    user_data = get_user_data(user_id)
    lang = user_data["lang"]

    if text in ["/lang"]:
        bot.send_message(user_id, LANG_TEXTS["select_lang"], reply_markup=lang_keyboard())
        return

    if not lang:
        bot.send_message(user_id, LANG_TEXTS["select_lang"], reply_markup=lang_keyboard())
        return

    if user_state.get(user_id) == "colorizer_wait_file":
        file_content = ""
        try:
            if message.document:
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_content = downloaded_file.decode('utf-8', errors='ignore')
            elif text:
                file_content = text
        except Exception as e:
            file_content = ""

        if not file_content:
            bot.reply_to(message, "❌ خواندن محتوای فایل با خطا مواجه شد. لطفاً سورس‌کد را به صورت فایل متنی یا متن بفرستید.")
            return

        user_temp_data[user_id]["file_content"] = file_content

        found_buttons = re.findall(r'InlineKeyboardButton\s*\(\s*["\']([^"\']+)["\']', file_content)
        if not found_buttons:
            found_buttons = ["دکمه اول", "دکمه دوم", "دکمه سوم"]

        user_temp_data[user_id]["buttons_list"] = list(set(found_buttons))[:15]

        user_state[user_id] = "colorizer_select_mode"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🔴 کلی سرخ", callback_data="color_mode_all_red", style="danger"),
            types.InlineKeyboardButton("🔵 کلی آبی", callback_data="color_mode_all_blue", style="primary"),
            types.InlineKeyboardButton("🟢 کلی سبز", callback_data="color_mode_all_green", style="primary"),
            types.InlineKeyboardButton("🌈 رنگارنگ ترکیبی (سرخ، سبز، آبی)", callback_data="color_mode_all_rainbow", style="success"),
            types.InlineKeyboardButton("🎨 رنگ کردن دلخواه دکمه‌ها (یکی یکی)", callback_data="color_mode_custom", style="primary")
        )
        bot.reply_to(message, f"🟢 فایل ربات دریافت شد!\n📊 تعداد دکمه‌های شیشه‌ای یافت‌شده: {len(user_temp_data[user_id]['buttons_list'])}\n\nلطفاً حالت رنگ کردن دکمه‌ها را انتخاب کنید:", reply_markup=markup)
        return

    if user_id == ADMIN_ID and user_state.get(user_id) == "waiting_new_admin_id":
        del user_state[user_id]
        if text.isdigit():
            new_admin_id = int(text)
            if new_admin_id not in admins_list:
                admins_list.append(new_admin_id)
                save_admins()
                bot.reply_to(message, f"✅ کاربر با آیدی `{new_admin_id}` با موفقیت به عنوان ادمین اضافه شد.", parse_mode="Markdown")
            else:
                bot.reply_to(message, "⚠️ این کاربر از قبل ادمین است.")
        else:
            bot.reply_to(message, "❌ آیدی نامعتبر است. لطفاً فقط عدد وارد کنید.")
        return

    if is_admin(user_id) and user_state.get(user_id) in ["add_item_get_name", "add_item_get_value", "add_item_get_points"]:
        state = user_state[user_id]
        if state == "add_item_get_name":
            user_temp_data[user_id]["name"] = text
            user_state[user_id] = "add_item_get_value"
            itype = user_temp_data[user_id]["type"]
            if itype == "file":
                bot.send_message(user_id, "📁 لطفاً فایل خود را بفرستید یا `file_id` آن را وارد کنید:")
            elif itype == "tutorial":
                bot.send_message(user_id, "🎥 لطفاً ویدیو، عکس یا `file_id` آموزش خود را ارسال کنید:")
            else:
                bot.send_message(user_id, "🔗 لطفاً آدرس یا یوزرنیم ربات/سایت را بفرستید (مثلا @bot):")
            return
        elif state == "add_item_get_value":
            itype = user_temp_data[user_id]["type"]
            if itype == "file":
                if message.document: val = message.document.file_id
                elif message.photo: val = message.photo[-1].file_id
                elif message.video: val = message.video.file_id
                elif message.audio: val = message.audio.file_id
                else: val = text
                user_temp_data[user_id]["value"] = val
            elif itype == "tutorial":
                if message.video:
                    user_temp_data[user_id]["value"] = message.video.file_id
                    user_temp_data[user_id]["media_type"] = "video"
                elif message.photo:
                    user_temp_data[user_id]["value"] = message.photo[-1].file_id
                    user_temp_data[user_id]["media_type"] = "photo"
                elif message.document:
                    user_temp_data[user_id]["value"] = message.document.file_id
                    user_temp_data[user_id]["media_type"] = "video"
                else:
                    user_temp_data[user_id]["value"] = text.strip()
                    user_temp_data[user_id]["media_type"] = "video"
            else:
                user_temp_data[user_id]["value"] = text

            user_state[user_id] = "add_item_get_points"
            bot.send_message(user_id, "💰 لطفاً تعداد امتیاز مورد نیاز را به عدد وارد کنید:")
            return
        elif state == "add_item_get_points":
            try:
                points = int(text)
                data = user_temp_data[user_id]
                new_id = str(len(bot_items) + 1)
                while new_id in bot_items:
                    new_id = str(int(new_id) + 1)

                if data["type"] == "file":
                    bot_items[new_id] = {
                        "name": {"fa": data["name"], "en": data["name"]},
                        "type": "file",
                        "file_id": data["value"],
                        "points": points,
                        "caption": "👤 ساخته شده با ربات"
                    }
                elif data["type"] == "tutorial":
                    bot_items[new_id] = {
                        "name": {"fa": data["name"], "en": data["name"]},
                        "type": "tutorial",
                        "media_type": data.get("media_type", "video"),
                        "file_id": data["value"],
                        "points": points,
                        "caption": "🎥 آموزش ویدیوئی / تصویری ربات"
                    }
                else:
                    bot_items[new_id] = {
                        "name": {"fa": data["name"], "en": data["name"]},
                        "type": "link",
                        "username": data["value"],
                        "points": points
                    }
                save_items()
                del user_state[user_id]
                del user_temp_data[user_id]
                bot.reply_to(message, f"✅ آیتم جدید با موفقیت اضافه شد و به بخش مربوطه انتقال یافت! (شناسه: {new_id})")
            except:
                bot.reply_to(message, "❌ مقدار امتیاز نامعتبر است. لطفاً فقط عدد وارد کنید:")
            return

    if is_admin(user_id) and user_state.get(user_id) in ["waiting_broadcast", "waiting_forward"]:
        state = user_state.get(user_id)
        del user_state[user_id]
        bot.send_message(user_id, "⏳ در حال ارسال...")
        for uid in list(users_db.keys()):
            try:
                if state == "waiting_broadcast": bot.send_message(int(uid), text)
                else: bot.forward_message(int(uid), message.chat.id, message.message_id)
                time.sleep(0.05)
            except: pass
        bot.send_message(user_id, "📢 پایان ارسال همگانی.")
        return

    if user_state.get(user_id) == "waiting_support":
        del user_state[user_id]
        info_header = f"📥 پیام از کاربر: {user_id}\n👤 نام: {message.from_user.first_name}\n\n💬 متن: {text}"
        for adm in admins_list:
            try: bot.send_message(adm, info_header)
            except: pass
        bot.send_message(user_id, LANG_TEXTS["support_msg"][lang], reply_markup=main_keyboard(lang))
        return

if __name__ == "__main__":
    while True:
        try: bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except KeyboardInterrupt: break
        except: time.sleep(5)