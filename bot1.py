#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# توکن ربات تلگرام خود را اینجا قرار دهید
BOT_TOKEN = '8374056469:AAEPHX04QMel4FZPULe5A9xWGgsk21YEr1I'


# ID ادمین اصلی - این رو با user ID خودت عوض کن
SUPER_ADMIN_ID = 6479704151

# اطلاعات مدیر (قابل تغییر)
MANAGER_NAME = "مهدی"
MANAGER_USERNAME = "@Mahdi9193a"

# ذخیره اطلاعات کاربران
user_sessions = {}

# ذخیره تاریخچه قرعه‌کشی‌ها
lottery_history = {}

# فایل ذخیره لیست ادمین‌ها
admins_file = 'admins.json'

def load_admins():
    """بارگذاری لیست ادمین‌ها از فایل"""
    if os.path.exists(admins_file):
        try:
            with open(admins_file, 'r') as f:
                admins = json.load(f)
                if SUPER_ADMIN_ID not in admins:
                    admins.append(SUPER_ADMIN_ID)
                return admins
        except:
            pass
    return [SUPER_ADMIN_ID]

def save_admins(admins):
    """ذخیره لیست ادمین‌ها در فایل"""
    try:
        with open(admins_file, 'w') as f:
            json.dump(admins, f)
        return True
    except:
        return False

admin_list = load_admins()

def is_admin(user_id):
    return user_id in admin_list

def is_super_admin(user_id):
    return user_id == SUPER_ADMIN_ID

def format_number(num):
    """فرمت کردن اعداد با کامای فارسی"""
    return f"{num:,}".replace(',', '،')

# کیبوردهای مختلف

def get_admin_keyboard():
    keyboard = [
        [KeyboardButton("🎲 اجرای قرعه کشی")],
        [KeyboardButton("📋 قرعه‌کشی‌های گذشته")],
        [KeyboardButton("👥 مدیریت ادمین‌ها")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_user_keyboard():
    keyboard = [
        [KeyboardButton("📋 مشاهده نتایج قرعه‌کشی‌ها")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def get_admin_management_keyboard():
    keyboard = [
        [KeyboardButton("➕ اضافه کردن ادمین")],
        [KeyboardButton("➖ حذف ادمین")],
        [KeyboardButton("📄 لیست ادمین‌ها")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_finish_list_keyboard():
    keyboard = [
        [KeyboardButton("✅ اتمام لیست")],
        [KeyboardButton("✏️ ویرایش لیست")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ready_keyboard():
    keyboard = [
        [KeyboardButton("🎲 اجرای قرعه کشی")],
        [KeyboardButton("🔙 بازگشت به منوی اصلی")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_history_keyboard():
    all_lotteries = []
    for admin_id in lottery_history:
        for lottery in lottery_history[admin_id]:
            all_lotteries.append(lottery)
    
    if not all_lotteries:
        return get_back_keyboard()
    
    all_lotteries.sort(key=lambda x: x['date'], reverse=True)
    
    keyboard = []
    for lottery in all_lotteries[:20]:
        keyboard.append([KeyboardButton(f"📋 {lottery['name']}")])
    
    keyboard.append([KeyboardButton("🔙 بازگشت به منوی اصلی")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_history_detail_keyboard(user_id):
    if is_admin(user_id):
        keyboard = [
            [KeyboardButton("📋 قرعه‌کشی‌های گذشته")],
            [KeyboardButton("🔙 بازگشت به منوی اصلی")]
        ]
    else:
        keyboard = [
            [KeyboardButton("📋 مشاهده نتایج قرعه‌کشی‌ها")],
            [KeyboardButton("🔙 بازگشت به منوی اصلی")]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def init_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'state': 'main',
            'names': [],
            'count': 0,
            'lottery_name': '',
            'total_prize': 0,
            'prize_per_person': 0,
            'temp_admin_id': None
        }
    
    if is_admin(user_id) and user_id not in lottery_history:
        lottery_history[user_id] = []

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "کاربر"
    init_user_session(user_id)
    
    if is_admin(user_id):
        if is_super_admin(user_id):
            welcome_text = f"🎯 سلام {user_name}!\n\n" \
                          "شما ادمین اصلی این ربات هستید 👑\n" \
                          "می‌توانید قرعه‌کشی بسازید و ادمین‌ها را مدیریت کنید."
        else:
            welcome_text = f"🎯 سلام {user_name}!\n\n" \
                          "شما ادمین این ربات هستید ✅\n" \
                          "می‌توانید قرعه‌کشی بسازید و نتایج را مشاهده کنید."
        keyboard = get_admin_keyboard()
    else:
        welcome_text = f"🎯 سلام {user_name}!\n\n" \
                      "شما می‌توانید نتایج قرعه‌کشی‌ها را مشاهده کنید 👀"
        keyboard = get_user_keyboard()
    
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

async def get_user_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "کاربر"
    
    status = "👑 ادمین اصلی" if is_super_admin(user_id) else "✅ ادمین" if is_admin(user_id) else "👤 کاربر عادی"
    
    await update.message.reply_text(
        f"🆔 اطلاعات شما:\n\n"
        f"• نام: {user_name}\n"
        f"• User ID: `{user_id}`\n"
        f"• وضعیت: {status}\n\n"
        f"💡 این ID را برای اضافه شدن به ادمین‌ها استفاده کنید.",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    init_user_session(user_id)
    
    session = user_sessions[user_id]

    admin_only_actions = [
        "🎲 اجرای قرعه کشی", 
        "👥 مدیریت ادمین‌ها", 
        "➕ اضافه کردن ادمین", 
        "➖ حذف ادمین", 
        "📄 لیست ادمین‌ها"
    ]
    
    if text in admin_only_actions and not is_admin(user_id):
        await update.message.reply_text(
            "❌ شما مجوز انجام این عمل را ندارید!\n"
            "فقط ادمین‌ها می‌توانند این کار را انجام دهند.",
            reply_markup=get_user_keyboard()
        )
        return

    super_admin_only_actions = ["👥 مدیریت ادمین‌ها", "➕ اضافه کردن ادمین", "➖ حذف ادمین", "📄 لیست ادمین‌ها"]
    
    if text in super_admin_only_actions and not is_super_admin(user_id):
        await update.message.reply_text(
            "❌ فقط ادمین اصلی می‌تواند ادمین‌ها را مدیریت کند!",
            reply_markup=get_admin_keyboard()
        )
        return

    # مدیریت دکمه‌ها
    if text == "🎲 اجرای قرعه کشی":
        await handle_start_lottery(update, user_id, session)
    elif text in ["📋 قرعه‌کشی‌های گذشته", "📋 مشاهده نتایج قرعه‌کشی‌ها"]:
        await handle_view_history(update, user_id)
    elif text == "👥 مدیریت ادمین‌ها":
        await handle_admin_management(update, user_id)
    elif text == "➕ اضافه کردن ادمین":
        await handle_add_admin_request(update, user_id, session)
    elif text == "➖ حذف ادمین":
        await handle_remove_admin_request(update, user_id)
    elif text == "📄 لیست ادمین‌ها":
        await handle_list_admins(update, user_id)
    elif text == "🔙 بازگشت به منوی اصلی":
        await handle_back_to_main(update, user_id, session)
    elif text == "✅ اتمام لیست":
        await handle_finish_list(update, user_id, session)
    elif text == "✏️ ویرایش لیست":
        await handle_edit_list(update, user_id, session)
    else:
        # مدیریت state ها
        if session['state'] == 'getting_lottery_name':
            await handle_lottery_name(update, user_id, session, text)
        elif session['state'] == 'getting_total_prize':
            await handle_total_prize(update, user_id, session, text)
        elif session['state'] == 'collecting_names':
            await handle_collecting_names(update, user_id, session, text)
        elif session['state'] == 'getting_count':
            await handle_getting_count(update, user_id, session, text)
        elif session['state'] == 'getting_prize_per_person':
            await handle_prize_per_person(update, user_id, session, text)
        elif session['state'] == 'ready_to_draw' and text == "🎲 اجرای قرعه کشی":
            await execute_lottery(update, user_id, session)
        elif session['state'] == 'adding_admin':
            await handle_add_admin(update, user_id, session, text)
        elif session['state'] == 'removing_admin':
            await handle_remove_admin(update, user_id, text)
        else:
            await handle_lottery_selection(update, user_id, text)

async def handle_start_lottery(update: Update, user_id: int, session: dict):
    if session['state'] == 'ready_to_draw':
        await execute_lottery(update, user_id, session)
    else:
        session['state'] = 'getting_lottery_name'
        session['names'] = []
        session['lottery_name'] = ''
        session['total_prize'] = 0
        session['prize_per_person'] = 0
        
        await update.message.reply_text(
            "🏷️ ابتدا یک نام برای این قرعه‌کشی وارد کنید:\n\n"
            "مثال: قرعه‌کشی جایزه، انتخاب تیم، قرعه هدیه و...\n\n"
            "👇 نام قرعه‌کشی را بنویسید:",
            reply_markup=get_back_keyboard()
        )

async def handle_lottery_name(update: Update, user_id: int, session: dict, text: str):
    if not text.strip():
        await update.message.reply_text(
            "❌ نام نامعتبر!\n"
            "لطفاً یک نام معتبر برای قرعه‌کشی وارد کنید."
        )
        return

    session['lottery_name'] = text.strip()
    session['state'] = 'getting_total_prize'
    
    await update.message.reply_text(
        f"✅ نام قرعه‌کشی: \"{session['lottery_name']}\"\n\n"
        "💰 حالا مبلغ کل اسپانسری (جایزه) را وارد کنید:\n\n"
        "مثال: 500000 (برای ۵۰۰،۰۰۰ تومان)\n\n"
        "👇 مبلغ کل را بنویسید:",
        reply_markup=get_back_keyboard()
    )

async def handle_total_prize(update: Update, user_id: int, session: dict, text: str):
    try:
        total_prize = int(text.strip())
        if total_prize <= 0:
            raise ValueError()
            
        session['total_prize'] = total_prize
        session['state'] = 'collecting_names'
        
        await update.message.reply_text(
            f"✅ نام قرعه‌کشی: \"{session['lottery_name']}\"\n"
            f"💰 مبلغ کل اسپانسری: {format_number(total_prize)} تومان\n\n"
            "📝 حالا لطفاً لیست اسامی را وارد کنید:\n\n"
            "• هر اسم را در یک خط جداگانه بنویسید\n"
            "• می‌توانید تا هزاران اسم وارد کنید\n"
            "• پس از تمام شدن، روی \"اتمام لیست\" کلیک کنید\n"
            "• برای ویرایش اسامی از \"ویرایش لیست\" استفاده کنید\n\n"
            "👇 شروع کنید:",
            reply_markup=get_finish_list_keyboard()
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ مبلغ نامعتبر!\n"
            "لطفاً یک عدد معتبر وارد کنید.\n\n"
            "مثال: 500000"
        )

async def handle_collecting_names(update: Update, user_id: int, session: dict, text: str):
    new_names = [name.strip() for name in text.split('\n') if name.strip()]
    
    if new_names:
        session['names'].extend(new_names)
        
        recent_names = '\n'.join(f"• {name}" for name in new_names[-5:])
        
        await update.message.reply_text(
            f"✅ {len(new_names)} اسم اضافه شد\n"
            f"📊 مجموع: {len(session['names'])} اسم\n\n"
            f"آخرین اسامی اضافه شده:\n{recent_names}\n\n"
            "ادامه دهید، \"اتمام لیست\" یا \"ویرایش لیست\" را انتخاب کنید..."
        )
    else:
        await update.message.reply_text(
            "❌ اسم معتبری وارد نشد. لطفاً دوباره تلاش کنید."
        )

async def handle_edit_list(update: Update, user_id: int, session: dict):
    if session['state'] == 'collecting_names' and session['names']:
        # نمایش لیست فعلی برای ویرایش
        if len(session['names']) > 20:
            names_text = '\n'.join(f"{i+1}. {name}" for i, name in enumerate(session['names'][:20]))
            names_text += f"\n... و {len(session['names']) - 20} اسم دیگر"
        else:
            names_text = '\n'.join(f"{i+1}. {name}" for i, name in enumerate(session['names']))
        
        await update.message.reply_text(
            f"✏️ ویرایش لیست اسامی:\n\n"
            f"📋 لیست فعلی ({len(session['names'])} اسم):\n{names_text}\n\n"
            f"برای ویرایش:\n"
            f"• برای پاک کردن همه: \"پاک کردن همه\" بنویسید\n"
            f"• برای حذف اسم خاص: \"حذف نام_فرد\" بنویسید\n"
            f"• یا اسامی جدید اضافه کنید\n\n"
            f"👇 دستور خود را وارد کنید:",
            reply_markup=get_finish_list_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ لیستی برای ویرایش وجود ندارد!\n"
            "ابتدا اسامی را وارد کنید."
        )

async def handle_finish_list(update: Update, user_id: int, session: dict):
    if session['state'] == 'collecting_names':
        if not session['names']:
            await update.message.reply_text(
                "❌ هیچ اسمی وارد نشده است!\n"
                "لطفاً ابتدا اسامی را وارد کنید."
            )
            return

        session['state'] = 'getting_count'
        
        names_preview = session['names'][:10]
        preview_text = '\n'.join(f"{i+1}. {name}" for i, name in enumerate(names_preview))
        if len(session['names']) > 10:
            preview_text += f"\n... و {len(session['names']) - 10} اسم دیگر"
        
        await update.message.reply_text(
            f"✅ تعداد {len(session['names'])} اسم دریافت شد!\n\n"
            f"📊 اسامی دریافت شده:\n{preview_text}\n\n"
            f"🔢 تعدادچرخ گرونه را مشخص کنید:\n"
            f"(عدد بین 1 تا {len(session['names'])})",
            reply_markup=get_back_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ ابتدا روی \"اجرای قرعه کشی\" کلیک کنید."
        )

async def handle_getting_count(update: Update, user_id: int, session: dict, text: str):
    try:
        count = int(text)
    except ValueError:
        await update.message.reply_text(
            f"❌ عدد نامعتبر!\n"
            f"لطفاً عددی بین 1 تا {len(session['names'])} وارد کنید."
        )
        return

    if count < 1 or count > len(session['names']):
        await update.message.reply_text(
            f"❌ عدد نامعتبر!\n"
            f"لطفاً عددی بین 1 تا {len(session['names'])} وارد کنید."
        )
        return

    session['count'] = count
    session['state'] = 'getting_prize_per_person'

    await update.message.reply_text(
        f"🎯 آماده تنظیم جایزه!\n\n"
        f"📋 تعداد کل اسامی: {len(session['names'])}\n"
        f"🎲 تعداد برندگان: {count}\n"
        f"💰 مبلغ کل: {format_number(session['total_prize'])} تومان\n\n"
        f"💵 حالا مبلغ جایزه هر نفر را وارد کنید:\n"
        f"(مثال: {format_number(session['total_prize'] // count)} تومان)\n\n"
        f"👇 مبلغ جایزه هر نفر:",
        reply_markup=get_back_keyboard()
    )

async def handle_prize_per_person(update: Update, user_id: int, session: dict, text: str):
    try:
        prize_per_person = int(text.strip())
        if prize_per_person <= 0:
            raise ValueError()
            
        session['prize_per_person'] = prize_per_person
        session['state'] = 'ready_to_draw'
        
        total_distributed = prize_per_person * session['count']
        
        await update.message.reply_text(
            f"🎯 همه چیز آماده قرعه‌کشی!\n\n"
            f"📋 خلاصه اطلاعات:\n"
            f"• نام: {session['lottery_name']}\n"
            f"• مبلغ کل اسپانسری: {format_number(session['total_prize'])} تومان\n"
            f"• تعداد شرکت‌کنندگان: {len(session['names'])} نفر\n"
            f"• تعداد برندگان: {session['count']} نفر\n"
            f"• جایزه هر نفر: {format_number(prize_per_person)} تومان\n"
            f"• مجموع توزیع شده: {format_number(total_distributed)} تومان\n\n"
            "برای اجرای قرعه‌کشی روی دکمه زیر کلیک کنید:",
            reply_markup=get_ready_keyboard()
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ مبلغ نامعتبر!\n"
            "لطفاً یک عدد معتبر وارد کنید."
        )

async def execute_lottery(update: Update, user_id: int, session: dict):
    shuffled_names = session['names'].copy()
    random.shuffle(shuffled_names)
    winners = shuffled_names[:session['count']]
    
    current_time = datetime.now().strftime('%Y/%m/%d - %H:%M:%S')
    lottery_data = {
        'name': session['lottery_name'],
        'all_names': session['names'].copy(),
        'winners': winners.copy(),
        'date': current_time,
        'total_count': len(session['names']),
        'selected_count': session['count'],
        'total_prize': session['total_prize'],
        'prize_per_person': session['prize_per_person'],
        'admin_id': user_id
    }
    
    lottery_history[user_id].append(lottery_data)
    
    winners_text = '\n'.join(f"{i+1}. {name}" for i, name in enumerate(winners))
    
    result_message = (
        f"🎉 نتایج قرعه‌کشی: \"{session['lottery_name']}\"\n\n"
        f"💰 مبلغ کل اسپانسری: {format_number(session['total_prize'])} تومان\n\n"
        f"🏆 اسامی اعلام شده برندگان خوش‌شانس مبلغ {format_number(session['prize_per_person'])} تومان شده‌اند:\n\n"
        f"{winners_text}\n\n"
        f"📊 از مجموع {len(session['names'])} شرکت‌کننده\n"
        f"⏰ زمان قرعه‌کشی: {current_time}\n\n"
        f"📢 تمامی کاربران از اعلام قرعه‌کشی موظف هستند به مدت 12 ساعت به مالک محترم گپ از نام قرعه‌کشی و مبلغ جایزه برای دریافت اطلاع دهند.\n\n"
        f"👤 مدیریت: {MANAGER_NAME} {MANAGER_USERNAME}\n\n"
        f"💾 این قرعه‌کشی در تاریخچه ذخیره شد."
    )

    await update.message.reply_text(result_message, reply_markup=get_admin_keyboard())

    # ریست جلسه
    session['state'] = 'main'
    session['names'] = []
    session['count'] = 0
    session['lottery_name'] = ''
    session['total_prize'] = 0
    session['prize_per_person'] = 0

async def show_lottery_details(update: Update, user_id: int, lottery_data: dict):
    winners_text = '\n'.join(f"{i+1}. {name}" for i, name in enumerate(lottery_data['winners']))
    
    if is_admin(user_id):
        if len(lottery_data['all_names']) > 50:
            all_names_text = '\n'.join(
                f"{i+1}. {name}" for i, name in enumerate(lottery_data['all_names'][:50])
            )
            all_names_text += f"\n... و {len(lottery_data['all_names']) - 50} اسم دیگر"
        else:
            all_names_text = '\n'.join(
                f"{i+1}. {name}" for i, name in enumerate(lottery_data['all_names'])
            )

        history_message = (
            f"📋 جزئیات قرعه‌کشی: \"{lottery_data['name']}\"\n\n"
            f"📅 تاریخ: {lottery_data['date']}\n"
            f"💰 مبلغ کل اسپانسری: {format_number(lottery_data.get('total_prize', 0))} تومان\n"
            f"👥 تعداد کل شرکت‌کنندگان: {lottery_data['total_count']}\n"
            f"🏆 تعداد برندگان: {lottery_data['selected_count']}\n"
            f"💵 جایزه هر نفر: {format_number(lottery_data.get('prize_per_person', 0))} تومان\n"
            f"👤 ادمین ایجادکننده: {lottery_data.get('admin_id', 'نامشخص')}\n\n"
            f"🏆 اسامی اعلام شده برندگان خوش‌شانس مبلغ {format_number(lottery_data.get('prize_per_person', 0))} تومان شده‌اند:\n{winners_text}\n\n"
            f"📢 تمامی کاربران از اعلام قرعه‌کشی موظف هستند به مدت 12 ساعت به مالک محترم گپ از نام قرعه‌کشی و مبلغ جایزه برای دریافت اطلاع دهند.\n\n"
            f"👤 مدیریت: {MANAGER_NAME} {MANAGER_USERNAME}\n\n"
            f"👥 تمام شرکت‌کنندگان:\n{all_names_text}"
        )
    else:
        # کاربران عادی فقط برندگان را می‌بینند
        history_message = (
            f"📋 نتایج قرعه‌کشی: \"{lottery_data['name']}\"\n\n"
            f"📅 تاریخ: {lottery_data['date']}\n"
            f"💰 مبلغ کل اسپانسری: {format_number(lottery_data.get('total_prize', 0))} تومان\n"
            f"👥 تعداد کل شرکت‌کنندگان: {lottery_data['total_count']}\n"
            f"🏆 تعداد برندگان: {lottery_data['selected_count']}\n\n"
            f"🏆 اسامی اعلام شده برندگان خوش‌شانس مبلغ {format_number(lottery_data.get('prize_per_person', 0))} تومان شده‌اند:\n{winners_text}\n\n"
            f"📢 تمامی کاربران از اعلام قرعه‌کشی موظف هستند به مدت 12 ساعت به مالک محترم گپ از نام قرعه‌کشی و مبلغ جایزه برای دریافت اطلاع دهند.\n\n"
            f"👤 مدیریت: {MANAGER_NAME} {MANAGER_USERNAME}\n\n"
            f"ℹ️ برای مشاهده لیست کامل شرکت‌کنندگان با ادمین تماس بگیرید."
        )

    await update.message.reply_text(history_message, reply_markup=get_history_detail_keyboard(user_id))

# بقیه توابع (مدیریت ادمین و...)

async def handle_view_history(update: Update, user_id: int):
    total_lotteries = 0
    for admin_id in lottery_history:
        total_lotteries += len(lottery_history[admin_id])
    
    if total_lotteries == 0:
        if is_admin(user_id):
            text = "📋 هیچ قرعه‌کشی قبلی یافت نشد!\nابتدا یک قرعه‌کشی انجام دهید."
            keyboard = get_admin_keyboard()
        else:
            text = "📋 هیچ قرعه‌کشی قبلی یافت نشد!"
            keyboard = get_user_keyboard()
    else:
        text = f"📋 قرعه‌کشی‌های موجود:\n\n" \
               f"🗂️ تعداد کل: {total_lotteries} قرعه‌کشی\n\n" \
               "برای مشاهده جزئیات هر قرعه‌کشی، روی نام آن کلیک کنید:"
        keyboard = get_history_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard)

async def handle_admin_management(update: Update, user_id: int):
    await update.message.reply_text(
        "👥 مدیریت ادمین‌ها:\n\n"
        "• ➕ اضافه کردن ادمین جدید\n"
        "• ➖ حذف ادمین موجود\n"
        "• 📄 مشاهده لیست ادمین‌ها\n\n"
        "⚠️ فقط ادمین اصلی می‌تواند ادمین‌ها را مدیریت کند.\n\n"
        "گزینه مورد نظر را انتخاب کنید:",
        reply_markup=get_admin_management_keyboard()
    )

async def handle_add_admin_request(update: Update, user_id: int, session: dict):
    session['state'] = 'adding_admin'
    await update.message.reply_text(
        "➕ اضافه کردن ادمین جدید:\n\n"
        "لطفاً User ID فرد مورد نظر را ارسال کنید.\n\n"
        "💡 نکته: کاربر می‌تواند با ارسال دستور /myid در ربات، User ID خود را دریافت کند.\n\n"
        "👇 User ID را وارد کنید:",
        reply_markup=get_back_keyboard()
    )

async def handle_add_admin(update: Update, user_id: int, session: dict, text: str):
    try:
        new_admin_id = int(text.strip())
        
        if new_admin_id in admin_list:
            await update.message.reply_text(
                f"⚠️ کاربر {new_admin_id} قبلاً ادمین است!",
                reply_markup=get_admin_management_keyboard()
            )
        else:
            admin_list.append(new_admin_id)
            if save_admins(admin_list):
                lottery_history[new_admin_id] = []
                
                await update.message.reply_text(
                    f"✅ کاربر {new_admin_id} با موفقیت به عنوان ادمین اضافه شد!\n\n"
                    f"🔢 تعداد کل ادمین‌ها: {len(admin_list)}",
                    reply_markup=get_admin_management_keyboard()
                )
            else:
                await update.message.reply_text(
                    "❌ خطا در ذخیره اطلاعات! دوباره تلاش کنید.",
                    reply_markup=get_admin_management_keyboard()
                )
        
        session['state'] = 'main'
        
    except ValueError:
        await update.message.reply_text(
            "❌ User ID نامعتبر!\n"
            "لطفاً یک عدد معتبر وارد کنید.\n\n"
            "مثال: 123456789"
        )

async def handle_remove_admin_request(update: Update, user_id: int):
    removable_admins = [admin for admin in admin_list if admin != SUPER_ADMIN_ID]
    
    if not removable_admins:
        await update.message.reply_text(
            "⚠️ هیچ ادمین قابل حذفی وجود ندارد!\n"
            "ادمین اصلی قابل حذف نیست.",
            reply_markup=get_admin_management_keyboard()
        )
        return
    
    text = "➖ حذف ادمین:\n\nUser ID ادمینی که می‌خواهید حذف کنید را وارد کنید:\n\n"
    text += "📋 ادمین‌های قابل حذف:\n"
    for admin_id in removable_admins:
        text += f"• {admin_id}\n"
    
    user_sessions[user_id]['state'] = 'removing_admin'
    
    await update.message.reply_text(text, reply_markup=get_back_keyboard())

async def handle_remove_admin(update: Update, user_id: int, text: str):
    try:
        admin_to_remove = int(text.strip())
        
        if admin_to_remove == SUPER_ADMIN_ID:
            await update.message.reply_text(
                "❌ نمی‌توان ادمین اصلی را حذف کرد!",
                reply_markup=get_admin_management_keyboard()
            )
        elif admin_to_remove not in admin_list:
            await update.message.reply_text(
                f"❌ کاربر {admin_to_remove} در لیست ادمین‌ها وجود ندارد!",
                reply_markup=get_admin_management_keyboard()
            )
        else:
            admin_list.remove(admin_to_remove)
            if save_admins(admin_list):
                await update.message.reply_text(
                    f"✅ کاربر {admin_to_remove} با موفقیت از لیست ادمین‌ها حذف شد!\n\n"
                    f"🔢 تعداد کل ادمین‌ها: {len(admin_list)}",
                    reply_markup=get_admin_management_keyboard()
                )
            else:
                await update.message.reply_text(
                    "❌ خطا در ذخیره اطلاعات! دوباره تلاش کنید.",
                    reply_markup=get_admin_management_keyboard()
                )
        
        user_sessions[user_id]['state'] = 'main'
        
    except ValueError:
        await update.message.reply_text(
            "❌ User ID نامعتبر!\n"
            "لطفاً یک عدد معتبر وارد کنید."
        )

async def handle_list_admins(update: Update, user_id: int):
    text = f"📄 لیست ادمین‌ها:\n\n🔢 تعداد کل: {len(admin_list)}\n\n"
    
    for i, admin_id in enumerate(admin_list, 1):
        if admin_id == SUPER_ADMIN_ID:
            text += f"{i}. {admin_id} (ادمین اصلی) 👑\n"
        else:
            text += f"{i}. {admin_id} (ادمین) ✅\n"
    
    await update.message.reply_text(text, reply_markup=get_admin_management_keyboard())

async def handle_back_to_main(update: Update, user_id: int, session: dict):
    session['state'] = 'main'
    session['names'] = []
    session['count'] = 0
    session['lottery_name'] = ''
    session['total_prize'] = 0
    session['prize_per_person'] = 0
    session['temp_admin_id'] = None
    
    if is_admin(user_id):
        text = "🏠 به منوی اصلی بازگشتید"
        keyboard = get_admin_keyboard()
    else:
        text = "🏠 به منوی اصلی بازگشتید"
        keyboard = get_user_keyboard()
    
    await update.message.reply_text(text, reply_markup=keyboard)

async def handle_lottery_selection(update: Update, user_id: int, text: str):
    # بررسی دستورات ویرایش لیست
    if user_sessions[user_id]['state'] == 'collecting_names':
        if text == "پاک کردن همه":
            user_sessions[user_id]['names'] = []
            await update.message.reply_text(
                "🗑️ همه اسامی پاک شدند!\n"
                "حالا می‌توانید اسامی جدید وارد کنید."
            )
            return
        elif text.startswith("حذف "):
            name_to_remove = text[4:].strip()
            if name_to_remove in user_sessions[user_id]['names']:
                user_sessions[user_id]['names'].remove(name_to_remove)
                await update.message.reply_text(
                    f"✅ نام \"{name_to_remove}\" از لیست حذف شد!\n"
                    f"📊 تعداد باقی‌مانده: {len(user_sessions[user_id]['names'])} اسم"
                )
            else:
                await update.message.reply_text(
                    f"❌ نام \"{name_to_remove}\" در لیست یافت نشد!"
                )
            return
    
    # جستجو در قرعه‌کشی‌ها
    lottery_name = text.replace("📋 ", "").strip()
    
    selected_lottery = None
    for admin_id in lottery_history:
        for lottery in lottery_history[admin_id]:
            if lottery['name'] == lottery_name:
                selected_lottery = lottery
                break
        if selected_lottery:
            break
    
    if selected_lottery:
        await show_lottery_details(update, user_id, selected_lottery)
    else:
        if is_admin(user_id):
            keyboard = get_admin_keyboard()
        else:
            keyboard = get_user_keyboard()
        
        await update.message.reply_text(
            "❓ دستور نامعتبر!\n"
            "لطفاً از دکمه‌های موجود استفاده کنید.",
            reply_markup=keyboard
        )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("myid", get_user_id_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 ربات قرعه‌کشی با سیستم ادمین و مبلغ جایزه آماده است!")
    print("📱 برای استفاده:")
    print("1. توکن ربات را در کد قرار دهید")
    print(f"2. SUPER_ADMIN_ID را با User ID خود عوض کنید (فعلی: {SUPER_ADMIN_ID})")
    print(f"3. اطلاعات مدیر را تغییر دهید (فعلی: {MANAGER_NAME} {MANAGER_USERNAME})")
    print("4. از دستور /myid برای دریافت User ID استفاده کنید")
    print("\n📦 برای نصب کتابخانه مورد نیاز:")
    print("pip install python-telegram-bot")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()