import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from mqtt import MQTTClient
from iot_system.microclimate_system import MicroclimateSystem

microclimate_system = MicroclimateSystem(is_remote=True)
mqtt_client = MQTTClient(None, microclimate_system)
mqtt_client.start()


async def start(update: Update, context: CallbackQueryHandler):
    await update.message.reply_text("Welcome to Microclimate!")
    keyboard = [[InlineKeyboardButton("Меню", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = update.effective_message
    await message.reply_text("Главное меню:", reply_markup=reply_markup)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, replace=True) -> None:
    keyboard = [
        [InlineKeyboardButton("Показать пограничные значения", callback_data='show_limits')],
        [InlineKeyboardButton("Показать текущие значения", callback_data='show_current')],
        [InlineKeyboardButton("Показать состояние систем", callback_data='show_systems')],
        [InlineKeyboardButton("Редактировать максимальные и минимальные значения", callback_data='edit_values')],
    ]
    if microclimate_system.mode == "auto":
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
async def show_limits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    limits_text = (
        f"Пограничные значения:\n"
        f"Температура: {microclimate_system.temp_min} - {microclimate_system.temp_max} °C\n"
        f"Свет: {microclimate_system.light_min} - {microclimate_system.light_max} лк\n"
        f"Влажность почвы: {microclimate_system.soil_min} - {microclimate_system.soil_max}%\n"
        f"Уровень воды: {microclimate_system.water_min}%"
    )
    await update.callback_query.edit_message_text(limits_text)
    await show_main_menu(update, context, replace=False)


# Показать текущие значения
async def show_current(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_text = (
        f"Текущие значения:\n"
        f"Температура: {microclimate_system.temperature} °C\n"
        f"Свет: {microclimate_system.light_level} лк\n"
        f"Влажность почвы: {microclimate_system.soil_moisture}%\n"
        f"Уровень воды: {microclimate_system.water_level}%"
    )
    await update.callback_query.edit_message_text(current_text)
    await show_main_menu(update, context, replace=False)


async def show_systems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_text = (
        f"Состояние систем\n"
        f"Режим работы: {"Автоматический" if microclimate_system.mode == "auto" else "Ручной"}\n"
        f"Кулер: {"Включен" if microclimate_system.cooler_status else "Выключен"}\n"
        f"Подогрев: {"Включен" if microclimate_system.heater_status else "Выключен"}\n"
        f"Освещение: {"Выключено" if microclimate_system.light_intensity == 0 else f"Интенсивность {microclimate_system.light_intensity}"}\n"
        f"Помпа: {"Включена" if microclimate_system.pump_status else "Выключена"}\n"
    )
    await update.callback_query.edit_message_text(current_text)
    await show_main_menu(update, context, replace=False)


# Переключить режим
async def toggle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    microclimate_system.mode = "manual" if microclimate_system.mode == "auto" else "auto"
    mqtt_client.publish_topic_data("remote/mode", json.dumps({"mode": microclimate_system.mode}))
    await update.callback_query.edit_message_text(f"Включен режим: {microclimate_system.mode}")
    await show_main_menu(update, context, replace=False)


# Подменю редактирования значений
async def edit_values(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.callback_query.edit_message_text("Выберите параметр для редактирования:", reply_markup=reply_markup)


# Подменю управления системами
async def manage_systems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton(f"{'Выключить' if microclimate_system.cooler_status else 'Включить'} охлаждение",
                              callback_data='toggle_cooler')],
        [InlineKeyboardButton(f"{'Выключить' if microclimate_system.heater_status else 'Включить'} обогрев",
                              callback_data='toggle_heater')],
        [InlineKeyboardButton("Изменить интенсивность освещения",
                              callback_data='toggle_light')],
        [InlineKeyboardButton(f"{'Выключить' if microclimate_system.pump_status else 'Включить'} помпу",
                              callback_data='toggle_pump')],
        [InlineKeyboardButton("Назад", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Управление системами:", reply_markup=reply_markup)


# Изменение конкретного параметра
async def set_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_param = update.callback_query.data
    context.user_data['selected_parameter'] = selected_param
    await update.callback_query.edit_message_text(f"Введите новое значение для {selected_param}:")


# Обработка нового значения параметра
async def receive_new_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selected_param = context.user_data.get('selected_parameter')
    try:
        new_value = float(update.message.text)
        setattr(microclimate_system, selected_param.replace('set_', ''), new_value)
        mqtt_client.publish_topic_data("remote/entries",
                                       json.dumps({f"{selected_param.replace('set_', '')}": new_value}))
        await update.message.reply_text(f"{selected_param} установлен на {new_value}.")
        await show_main_menu(update, context, replace=False)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите числовое значение.")


# Переключение состояния систем
async def toggle_system(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query.data == 'toggle_cooler':
        microclimate_system.cooler_status = not microclimate_system.cooler_status
        mqtt_client.publish_topic_data(f"remote/cooler", json.dumps({"cooler": microclimate_system.cooler_status}))
    elif update.callback_query.data == 'toggle_heater':
        microclimate_system.heater_status = not microclimate_system.heater_status
        mqtt_client.publish_topic_data(f"remote/heater", json.dumps({"heater": microclimate_system.heater_status}))
    elif update.callback_query.data == 'toggle_light':
        microclimate_system.light_status += 1
        mqtt_client.publish_topic_data(f"remote/light_intensity", str(microclimate_system.light_intensity))
    elif update.callback_query.data == 'toggle_pump':
        microclimate_system.pump_status = not microclimate_system.pump_status
        mqtt_client.publish_topic_data(f"remote/pump", json.dumps({"pump": microclimate_system.pump_status}))
    await manage_systems(update, context)


def main():
    app = Application.builder().token("7069262748:AAGCs7JGzr7D_NxxSifuyYk9BUJl1kP9ktM").build()

    # Команды и обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_limits, pattern='show_limits'))
    app.add_handler(CallbackQueryHandler(show_current, pattern='show_current'))
    app.add_handler(CallbackQueryHandler(show_systems, pattern='show_systems'))
    app.add_handler(CallbackQueryHandler(toggle_mode, pattern='toggle_mode'))
    app.add_handler(CallbackQueryHandler(edit_values, pattern='edit_values'))
    app.add_handler(CallbackQueryHandler(manage_systems, pattern='manage_systems'))
    app.add_handler(CallbackQueryHandler(set_parameter, pattern='^set_'))
    app.add_handler(CallbackQueryHandler(toggle_system, pattern='^toggle_'))
    app.add_handler(CallbackQueryHandler(show_main_menu, pattern='main_menu'))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_new_value))

    app.run_polling()


if __name__ == "__main__":
    main()
