from telebot import TeleBot, types
import json
import os

TOKEN = "8776201901:AAEs8BZLoGjtSAGhG-e_SKIPD59sMsWTfOw"
ADMIN_ID = 6696199952

bot = TeleBot(TOKEN)

FILE = "queue.json"

# ---------------- SERVICES ----------------
SERVICES = [
    "🦷 Tish davolash",
    "🪥 Plomba qilish",
    "😁 Oqartirish",
    "🦷 Tish olish",
    "💬 Bepul maslahat"
]

# ---------------- LOAD/SAVE ----------------
def load():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------------- KEYBOARDS ----------------
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➕ Navbatga yozilish")
    kb.row("📊 Navbatni ko‘rish")
    kb.row("👨‍⚕️ Admin panel")
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("➡ Keyingi bemor")
    kb.row("❌ O‘chirish")
    kb.row("🔙 Orqaga")
    return kb

def service_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in SERVICES:
        kb.row(s)
    return kb

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "🦷 *Stomatolog Clinic Bot*\n\n"
        "Xizmatlar:\n"
        "• Tish davolash\n"
        "• Plomba\n"
        "• Oqartirish\n"
        "• Tish olish\n"
        "• Bepul maslahat\n\n"
        "👇 Tanlang:",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ---------------- JOIN QUEUE ----------------
@bot.message_handler(func=lambda m: m.text == "➕ Navbatga yozilish")
def choose_service(msg):
    sent = bot.send_message(msg.chat.id, "🧾 Xizmatni tanlang:", reply_markup=service_menu())
    bot.register_next_step_handler(sent, ask_name)

def ask_name(msg):
    service = msg.text

    if service not in SERVICES:
        return bot.send_message(msg.chat.id, "❌ Xizmat noto‘g‘ri", reply_markup=main_menu())

    sent = bot.send_message(msg.chat.id, "👤 Ismingizni kiriting:")
    bot.register_next_step_handler(sent, save_user, service)

def save_user(msg, service):
    data = load()

    user = {
        "id": msg.from_user.id,
        "chat_id": msg.chat.id,
        "name": msg.text,
        "service": service
    }

    data.append(user)
    save(data)

    bot.send_message(
        msg.chat.id,
        f"✅ Navbatga qo‘shildingiz!\n🧾 Xizmat: {service}",
        reply_markup=main_menu()
    )

# ---------------- SHOW QUEUE ----------------
@bot.message_handler(func=lambda m: m.text == "📊 Navbatni ko‘rish")
def show_queue(msg):
    data = load()

    if not data:
        return bot.send_message(msg.chat.id, "📭 Navbat bo‘sh")

    text = "📊 NAVBAT:\n\n"

    for i, u in enumerate(data, 1):
        text += f"{i}. {u['name']} — {u['service']}\n"

    text += f"\n👨‍⚕️ Hozir: {data[0]['name']}"
    bot.send_message(msg.chat.id, text)

# ---------------- ADMIN PANEL ----------------
@bot.message_handler(func=lambda m: m.text == "👨‍⚕️ Admin panel")
def admin_panel(msg):
    if msg.from_user.id != ADMIN_ID:
        return bot.send_message(msg.chat.id, "❌ Ruxsat yo‘q")

    bot.send_message(msg.chat.id, "👨‍⚕️ Admin panel", reply_markup=admin_menu())

# ---------------- BACK ----------------
@bot.message_handler(func=lambda m: m.text == "🔙 Orqaga")
def back(msg):
    bot.send_message(msg.chat.id, "🏠 Menu", reply_markup=main_menu())

# ---------------- NEXT PATIENT ----------------
@bot.message_handler(func=lambda m: m.text == "➡ Keyingi bemor")
def next_patient(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    data = load()

    if not data:
        return bot.send_message(msg.chat.id, "📭 Navbat yo‘q")

    user = data.pop(0)
    save(data)

    bot.send_message(
        user["chat_id"],
        "🔔 Sizning navbatingiz keldi!\n👨‍⚕️ Klinikaga kirishingiz mumkin."
    )

    bot.send_message(msg.chat.id, f"➡ Chaqirildi: {user['name']}")# ---------------- DELETE ----------------
@bot.message_handler(func=lambda m: m.text == "❌ O‘chirish")
def delete_menu(msg):
    if msg.from_user.id != ADMIN_ID:
        return

    data = load()

    if not data:
        return bot.send_message(msg.chat.id, "📭 Bo‘sh")

    text = "❌ O‘chirish uchun raqamni yozing:\n\n"

    for i, u in enumerate(data, 1):
        text += f"{i}. {u['name']} — {u['service']}\n"

    sent = bot.send_message(msg.chat.id, text)
    bot.register_next_step_handler(sent, delete_user)

def delete_user(msg):
    try:
        idx = int(msg.text) - 1
        data = load()

        removed = data.pop(idx)
        save(data)

        bot.send_message(msg.chat.id, f"❌ O‘chirildi: {removed['name']}")

    except:
        bot.send_message(msg.chat.id, "❌ Noto‘g‘ri raqam")

# ---------------- RUN ----------------
bot.polling(none_stop=True)