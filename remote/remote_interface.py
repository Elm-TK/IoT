import json
import tkinter as tk
from tkinter import END
from tkinter import messagebox, Checkbutton

from iot_system import microclimate_system
from remote.mqtt import MQTTClient


class RemoteInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Simulator")

        self.microclimate_system = microclimate_system.MicroclimateSystem(is_remote=True)

        # Инициализация MQTT
        self.mqtt_client = MQTTClient(self, self.microclimate_system)
        self.mqtt_client.start()

        # Настройка интерфейса
        self.setup_ui()
        self.is_entries_on = True
        # Начинаем обновлять интерфейс
        self.update_ui()

    def setup_ui(self):
        # Блок датчиков
        sensor_frame = tk.Frame(self.root)
        sensor_frame.pack(pady=10)

        # Блок температуры
        temp_frame = tk.LabelFrame(sensor_frame, text="Температура", padx=10, pady=10)
        temp_frame.grid(row=0, column=0, padx=10, pady=5)
        self.temp_label = tk.Label(temp_frame, text=f"Температура: {self.microclimate_system.temperature:.2f}°C")
        self.temp_label.pack(pady=5)
        self.temp_indicator = tk.Label(temp_frame, text="Нормально", bg="green", width=10)
        self.temp_indicator.pack(pady=5)
        tk.Label(temp_frame, text="Мин:").pack()
        self.temp_min_entry = tk.Entry(temp_frame)
        self.temp_min_entry.insert(0, str(self.microclimate_system.temp_min))
        self.temp_min_entry.config(state=tk.DISABLED)
        self.temp_min_entry.pack()
        tk.Label(temp_frame, text="Макс:").pack()
        self.temp_max_entry = tk.Entry(temp_frame)
        self.temp_max_entry.insert(0, str(self.microclimate_system.temp_max))
        self.temp_max_entry.config(state=tk.DISABLED)
        self.temp_max_entry.pack()
        self.cooler_button = tk.Button(temp_frame, text="Включить систему охлаждения", command=self.toggle_cooler)
        self.cooler_button.pack(pady=5)
        self.heater_button = tk.Button(temp_frame, text="Включить систему подогрева", command=self.toggle_heater)
        self.heater_button.pack(pady=5)

        # Блок освещенности
        light_frame = tk.LabelFrame(sensor_frame, text="Освещенность", padx=10, pady=10)
        light_frame.grid(row=0, column=1, padx=10, pady=5)
        self.light_label = tk.Label(light_frame,
                                    text=f"Уровень освещенности: {self.microclimate_system.light_level:.2f}%")
        self.light_label.pack(pady=5)
        self.light_indicator = tk.Label(light_frame, text="Нормально", bg="green", width=10)
        self.light_indicator.pack(pady=5)
        tk.Label(light_frame, text="Мин:").pack()
        self.light_min_entry = tk.Entry(light_frame)
        self.light_min_entry.insert(0, str(self.microclimate_system.light_min))
        self.light_min_entry.config(state=tk.DISABLED)
        self.light_min_entry.pack()
        tk.Label(light_frame, text="Макс:").pack()
        self.light_max_entry = tk.Entry(light_frame)
        self.light_max_entry.insert(0, str(self.microclimate_system.light_max))
        self.light_max_entry.config(state=tk.DISABLED)
        self.light_max_entry.pack()
        self.light_button = tk.Button(light_frame, text="Интенсивность: Выкл",
                                      command=self.toggle_light_intensity)
        self.light_button.pack(pady=5)

        # Блок влажности почвы
        soil_frame = tk.LabelFrame(sensor_frame, text="Влажность почвы", padx=10, pady=10)
        soil_frame.grid(row=1, column=0, padx=10, pady=5)
        self.soil_label = tk.Label(soil_frame, text=f"Влажность почвы: {self.microclimate_system.soil_moisture:.2f}%")
        self.soil_label.pack(pady=5)
        self.soil_indicator = tk.Label(soil_frame, text="Нормально", bg="green", width=10)
        self.soil_indicator.pack(pady=5)
        tk.Label(soil_frame, text="Мин:").pack()
        self.soil_min_entry = tk.Entry(soil_frame)
        self.soil_min_entry.insert(0, str(self.microclimate_system.soil_min))
        self.soil_min_entry.config(state=tk.DISABLED)
        self.soil_min_entry.pack()
        tk.Label(soil_frame, text="Макс:").pack()
        self.soil_max_entry = tk.Entry(soil_frame)
        self.soil_max_entry.insert(0, str(self.microclimate_system.soil_max))
        self.soil_max_entry.config(state=tk.DISABLED)
        self.soil_max_entry.pack()
        self.pump_button = tk.Button(soil_frame, text="Включить помпу", command=self.toggle_pump)
        self.pump_button.pack(pady=5)

        # Блок уровня воды
        water_frame = tk.LabelFrame(sensor_frame, text="Уровень воды", padx=10, pady=10)
        water_frame.grid(row=1, column=1, padx=10, pady=5)
        self.water_label = tk.Label(water_frame, text=f"Уровень воды: {self.microclimate_system.water_level:.2f}%")
        self.water_label.pack(pady=5)
        self.water_indicator = tk.Label(water_frame, text="Нормально", bg="green", width=10)
        self.water_indicator.pack(pady=5)
        tk.Label(water_frame, text="Уведомление при ...% уровня воды").pack()
        self.water_min_entry = tk.Entry(water_frame)
        self.water_min_entry.insert(0, str(self.microclimate_system.water_min))
        self.water_min_entry.config(state=tk.DISABLED)
        self.water_min_entry.pack()
        self.add_water_button = tk.Button(water_frame, text="Добавить воду", command=self.add_water)
        self.add_water_button.pack(pady=5)

        # Режим редактирования пограничных значений
        self.entry_edit_checkbutton = Checkbutton(self.root, text="Режим редактирования пограничных значений",
                                                  command=self.toggle_entries, onvalue=True, offvalue=False)
        self.entry_edit_checkbutton.pack(pady=5)

        # Отправка пограничных значений
        self.send_entries_button = tk.Button(self.root, text="Отправить все максимальные и максимальные значения",
                                             command=self.send_entries)
        self.send_entries_button.pack(pady=5)

        # Переключение режимов
        self.mode_button = tk.Button(self.root, text="Переключить на Автоматический режим", command=self.toggle_mode)
        self.mode_button.pack(pady=5)

    def toggle_entries(self):
        print(self.is_entries_on)
        if self.is_entries_on:
            self.unlock_entries()
        else:
            self.lock_entries()
        self.is_entries_on = not self.is_entries_on

    def lock_entries(self):
        self.temp_min_entry.config(state=tk.DISABLED)
        self.temp_max_entry.config(state=tk.DISABLED)
        self.light_min_entry.config(state=tk.DISABLED)
        self.light_max_entry.config(state=tk.DISABLED)
        self.soil_min_entry.config(state=tk.DISABLED)
        self.soil_max_entry.config(state=tk.DISABLED)
        self.water_min_entry.config(state=tk.DISABLED)

    def unlock_entries(self):
        self.temp_min_entry.config(state=tk.NORMAL)
        self.temp_max_entry.config(state=tk.NORMAL)
        self.light_min_entry.config(state=tk.NORMAL)
        self.light_max_entry.config(state=tk.NORMAL)
        self.soil_min_entry.config(state=tk.NORMAL)
        self.soil_max_entry.config(state=tk.NORMAL)
        self.water_min_entry.config(state=tk.NORMAL)

    def toggle_mode(self):
        # Переключаем режим между "Автоматический" и "Ручной"
        self.microclimate_system.mode = 'manual' if self.microclimate_system.mode == 'auto' else 'auto'
        self.mqtt_client.publish_topic_data("remote/mode", json.dumps(self.microclimate_system.mode))
        print(self.microclimate_system.mode)
        # Обновляем текст кнопки в зависимости от режима
        self.mode_button.config(text="Автоматический" if self.microclimate_system.mode == 'auto' else "Ручной")

    def toggle_cooler(self):
        if self.microclimate_system.mode == 'manual':
            self.microclimate_system.cooler_status = not self.microclimate_system.cooler_status
            self.update_cooler_status()
            self.mqtt_client.publish_topic_data(f"remote/cooler", json.dumps(self.microclimate_system.cooler_status))

    def toggle_heater(self):
        if self.microclimate_system.mode == 'manual':
            self.microclimate_system.heater_status = not self.microclimate_system.heater_status
            self.update_heater_status()
            self.mqtt_client.publish_topic_data(f"remote/heater", json.dumps(self.microclimate_system.heater_status))

    def toggle_light_intensity(self):
        if self.microclimate_system.mode == 'manual':
            self.microclimate_system.light_intensity = (self.microclimate_system.light_intensity + 1) % 4
            self.update_light_status()
            self.mqtt_client.publish_topic_data(f"remote/light_intensity", self.microclimate_system.light_intensity)

    def toggle_pump(self):
        if self.microclimate_system.mode == 'manual':
            self.microclimate_system.pump_status = not self.microclimate_system.pump_status
            self.update_pump_status()
            self.mqtt_client.publish_topic_data(f"remote/pump", json.dumps(self.microclimate_system.pump_status))

    def add_water(self):
        self.microclimate_system.water_level = 100.0
        self.water_label.config(text=f"Уровень воды: {self.microclimate_system.water_level:.2f}%")
        messagebox.showinfo("Добавление воды", "Вода добавлена в резервуар")
        self.mqtt_client.publish_topic_data(f"remote/water", json.dumps(self.microclimate_system.water_level))

    def update_cooler_status(self):
        self.cooler_button.config(
            text=f"{'Выключить' if self.microclimate_system.cooler_status else 'Включить'} систему охлаждения")

    def update_heater_status(self):
        self.heater_button.config(
            text=f"{'Выключить' if self.microclimate_system.heater_status else 'Включить'} систему подогрева")

    def update_light_status(self):
        intensity_texts = ['Выкл', 'Низкий', 'Средний', 'Высокий']
        self.light_button.config(text=f"Интенсивность: {intensity_texts[self.microclimate_system.light_intensity]}")

    def update_pump_status(self):
        self.pump_button.config(text=f"{'Выключить' if self.microclimate_system.pump_status else 'Включить'} помпу")

    def update_water_status(self):
        self.water_label.config(text=f"Уровень воды: {self.microclimate_system.water_level:.2f}%")

    def update_ui(self):
        self.mode_button.config(text="Автоматический" if self.microclimate_system.mode == 'auto' else "Ручной")
        # Обновляем текст с показаниями датчиков
        self.temp_label.config(text=self.microclimate_system.temperature)
        self.light_label.config(text=self.microclimate_system.light_level)
        self.soil_label.config(text=self.microclimate_system.soil_moisture)
        self.water_label.config(text=self.microclimate_system.water_level)

        self.update_water_status()
        self.update_cooler_status()
        self.update_heater_status()
        self.update_light_status()
        self.update_pump_status()

        if self.is_entries_on:
            self.unlock_entries()
            self.temp_min_entry.delete(0, END)
            self.temp_min_entry.insert(0, str(self.microclimate_system.temp_min))
            self.temp_max_entry.delete(0, END)
            self.temp_max_entry.insert(0, str(self.microclimate_system.temp_max))
            self.light_min_entry.delete(0, END)
            self.light_min_entry.insert(0, str(self.microclimate_system.light_min))
            self.light_max_entry.delete(0, END)
            self.light_max_entry.insert(0, str(self.microclimate_system.light_max))
            self.soil_min_entry.delete(0, END)
            self.soil_min_entry.insert(0, str(self.microclimate_system.soil_min))
            self.soil_max_entry.delete(0, END)
            self.soil_max_entry.insert(0, str(self.microclimate_system.soil_max))
            self.water_min_entry.delete(0, END)
            self.water_min_entry.insert(0, str(self.microclimate_system.water_min))
            self.lock_entries()

        # Повторно вызываем этот метод через 5000 миллисекунд (5 секунд)
        self.root.after(5000, self.update_ui)

    def send_entries(self):
        entries_data = {
            "temp_max": self.temp_max_entry.get(),
            "temp_min": self.temp_min_entry.get(),
            "light_max": self.light_max_entry.get(),
            "light_min": self.light_min_entry.get(),
            "soil_max": self.soil_max_entry.get(),
            "soil_min": self.soil_min_entry.get(),
            "water_min": self.water_min_entry.get(),
        }
        for entry, value in entries_data.items():
            self.mqtt_client.publish_topic_data(f"remote/entries/{entry}", value)


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteInterface(root)
    root.mainloop()
