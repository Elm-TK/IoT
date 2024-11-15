import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters, \
    Updater

from mqtt import MQTTClient
from iot_system.microclimate_system import MicroclimateSystem


class BotHandler:
    def __init__(self, token):
        self.microclimate_system = MicroclimateSystem(is_remote=True)
        self.mqtt_client = MQTTClient(self, self.microclimate_system)
        self.mqtt_client.start()
        self.app = Application.builder().token(token).build()
        self.setup_handlers()

    def setup_handlers(self):
        # Команды и обработчики
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.show_limits, pattern='show_limits'))
        self.app.add_handler(CallbackQueryHandler(self.show_current, pattern='show_current'))
        self.app.add_handler(CallbackQueryHandler(self.show_systems, pattern='show_systems'))
        self.app.add_handler(CallbackQueryHandler(self.toggle_mode, pattern='toggle_mode'))
        self.app.add_handler(CallbackQueryHandler(self.edit_values, pattern='edit_values'))
        self.app.add_handler(CallbackQueryHandler(self.manage_systems, pattern='manage_systems'))
        self.app.add_handler(CallbackQueryHandler(self.set_parameter, pattern='^set_'))
        self.app.add_handler(CallbackQueryHandler(self.toggle_system, pattern='^toggle_'))
        self.app.add_handler(CallbackQueryHandler(self.show_main_menu, pattern='main_menu'))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.receive_new_value))

    async def send_water_alert(self):
        print("Уведомление")
        text = f"⚠️ Внимание! Уровень воды слишком низкий: {self.microclimate_system.water_level}%."
        await self.app.bot.send_message(chat_id="2026620172", text=text)

    async def start(self, update: Update, context: CallbackQueryHandler):
        await update.message.reply_text("Welcome to Microclimate!")
        keyboard = [[InlineKeyboardButton("Меню", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = update.effective_message
        await message.reply_text("Главное меню:", reply_markup=reply_markup)

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, replace=True) -> None:
        keyboard = [
            [InlineKeyboardButton("Показать пограничные значения", callback_data='show_limits')],
            [InlineKeyboardButton("Показать текущие значения", callback_data='show_current')],
            [InlineKeyboardButton("Показать состояние систем", callback_data='show_systems')],
            [InlineKeyboardButton("Редактировать максимальные и минимальные значения", callback_data='edit_values')],
        ]
        if self.microclimate_system.mode == "auto":
            keyboard += [
                [InlineKeyboardButton("Переключить на ручной режим", callback_data='toggle_mode')]
            ]
        else:  # режим "manual"
            keyboard += [
                [InlineKeyboardButton("Управление системами", callback_data='manage_systems')],
                [InlineKeyboardButton("Переключить на автоматический режим", callback_data='toggle_mode')]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if replace:
            await update.callback_query.edit_message_text("Главное меню:", reply_markup=reply_markup)
        else:
            message = update.effective_message
            await message.reply_text("Главное меню:", reply_markup=reply_markup)

    # Показать пограничные значения☻
    async def show_limits(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        limits_text = (
            f"Пограничные значения:\n"
            f"Температура: {self.microclimate_system.temp_min} - {self.microclimate_system.temp_max} °C\n"
            f"Свет: {self.microclimate_system.light_min} - {self.microclimate_system.light_max} лк\n"
            f"Влажность почвы: {self.microclimate_system.soil_min} - {self.microclimate_system.soil_max}%\n"
            f"Уровень воды: {self.microclimate_system.water_min}%"
        )
        await update.callback_query.edit_message_text(limits_text)
        await self.show_main_menu(update, context, replace=False)

    # Показать текущие значения
    async def show_current(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        current_text = (
            f"Текущие значения:\n"
            f"Температура: {self.microclimate_system.temperature} °C\n"
            f"Свет: {self.microclimate_system.light_level} лк\n"
            f"Влажность почвы: {self.microclimate_system.soil_moisture}%\n"
            f"Уровень воды: {self.microclimate_system.water_level}%"
        )
        await update.callback_query.edit_message_text(current_text)
        await self.show_main_menu(update, context, replace=False)

    async def show_systems(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        current_text = (
            f"Состояние систем\n"
            f"Режим работы: {"Автоматический" if self.microclimate_system.mode == "auto" else "Ручной"}\n"
            f"Кулер: {"Включен" if self.microclimate_system.cooler_status else "Выключен"}\n"
            f"Подогрев: {"Включен" if self.microclimate_system.heater_status else "Выключен"}\n"
            f"Освещение: {"Выключено" if self.microclimate_system.light_intensity == 0 else f"Интенсивность {self.microclimate_system.light_intensity}"}\n"
            f"Помпа: {"Включена" if self.microclimate_system.pump_status else "Выключена"}\n"
        )
        await update.callback_query.edit_message_text(current_text)
        await self.show_main_menu(update, context, replace=False)

    # Переключить режим
    async def toggle_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.microclimate_system.mode = "manual" if self.microclimate_system.mode == "auto" else "auto"
        self.mqtt_client.publish_topic_data("remote/mode", json.dumps({"mode": self.microclimate_system.mode}))
        await update.callback_query.edit_message_text(f"Включен режим: {self.microclimate_system.mode}")
        await self.show_main_menu(update, context, replace=False)

    # Подменю редактирования значений
    async def edit_values(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [InlineKeyboardButton("Температура (мин)", callback_data='set_temp_min')],
            [InlineKeyboardButton("Температура (макс)", callback_data='set_temp_max')],
            [InlineKeyboardButton("Свет (мин)", callback_data='set_light_min')],
            [InlineKeyboardButton("Свет (макс)", callback_data='set_light_max')],
            [InlineKeyboardButton("Влажность почвы (мин)", callback_data='set_soil_min')],
            [InlineKeyboardButton("Влажность почвы (макс)", callback_data='set_soil_max')],
            [InlineKeyboardButton("Уровень воды (мин)", callback_data='set_water_min')],
            [InlineKeyboardButton("Назад", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Выберите параметр для редактирования:",
                                                      reply_markup=reply_markup)

    # Подменю управления системами
    async def manage_systems(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [
            [InlineKeyboardButton(f"{'Выключить' if self.microclimate_system.cooler_status else 'Включить'} охлаждение",
                                  callback_data='toggle_cooler')],
            [InlineKeyboardButton(f"{'Выключить' if self.microclimate_system.heater_status else 'Включить'} обогрев",
                                  callback_data='toggle_heater')],
            [InlineKeyboardButton(
                f"Изменить интенсивность освещения на {(self.microclimate_system.light_intensity + 1) % 4}",
                callback_data='toggle_light')],
            [InlineKeyboardButton(f"{'Выключить' if self.microclimate_system.pump_status else 'Включить'} помпу",
                                  callback_data='toggle_pump')],
            [InlineKeyboardButton("Назад", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Управление системами:", reply_markup=reply_markup)

    # Изменение конкретного параметра
    async def set_parameter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        selected_param = update.callback_query.data
        context.user_data['selected_parameter'] = selected_param
        await update.callback_query.edit_message_text(f"Введите новое значение для {selected_param}:")

    # Обработка нового значения параметра
    async def receive_new_value(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        selected_param = context.user_data.get('selected_parameter')
        try:
            new_value = float(update.message.text)
            setattr(self.microclimate_system, selected_param.replace('set_', ''), new_value)
            self.mqtt_client.publish_topic_data("remote/entries",
                                                json.dumps({f"{selected_param.replace('set_', '')}": new_value}))
            await update.message.reply_text(f"{selected_param} установлен на {new_value}.")
            await self.show_main_menu(update, context, replace=False)
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите числовое значение.")

    # Переключение состояния систем
    async def toggle_system(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.callback_query.data == 'toggle_cooler':
            self.microclimate_system.cooler_status = not self.microclimate_system.cooler_status
            self.mqtt_client.publish_topic_data(f"remote/cooler",
                                                json.dumps({"cooler": self.microclimate_system.cooler_status}))
        elif update.callback_query.data == 'toggle_heater':
            self.microclimate_system.heater_status = not self.microclimate_system.heater_status
            self.mqtt_client.publish_topic_data(f"remote/heater",
                                                json.dumps({"heater": self.microclimate_system.heater_status}))
        elif update.callback_query.data == 'toggle_light':
            self.microclimate_system.light_intensity = (self.microclimate_system.light_intensity + 1) % 4
            self.mqtt_client.publish_topic_data(f"remote/light_intensity",
                                                str(self.microclimate_system.light_intensity))
        elif update.callback_query.data == 'toggle_pump':
            self.microclimate_system.pump_status = not self.microclimate_system.pump_status
            self.mqtt_client.publish_topic_data(f"remote/pump",
                                                json.dumps({"pump": self.microclimate_system.pump_status}))
        await self.manage_systems(update, context)

    def run(self):
        self.app.run_polling()


if __name__ == "__main__":
    token = "7069262748:AAGCs7JGzr7D_NxxSifuyYk9BUJl1kP9ktM"
    bot_handler = BotHandler(token)
    bot_handler.run()
