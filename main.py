import tkinter as tk
import random
import threading
import time
from tkinter import messagebox


class IoTDevice:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced IoT Device Simulator")

        # Инициализационные переменные (Максимальные, минимальные, начальные значения)
        self.initial_values = {
            "temp_min": 15.0,
            "temp_max": 30.0,
            "light_min": 40.0,
            "light_max": 80.0,
            "soil_min": 40.0,
            "soil_max": 70.0,
            "water_min": 20.0,
            "water_max": 100.0,
        }

        # Инициализация значений датчиков и актуаторов
        self.temperature = 20.00
        self.light_level = 70.00
        self.soil_moisture = 50.00
        self.water_level = 100.00
        self.pump_status = False
        self.cooler_status = False
        self.heater_status = False
        self.light_status = False
        self.light_intensity = 0  # 0: выкл, 1: низкий, 2: средний, 3: высокий
        self.mode = 'manual'

        # Пороговые значения
        self.interval = 1

        # Интерфейс
        self.create_interface()

        # Таймер для обновления данных
        self.running = True
        self.sensor_update_thread = threading.Thread(target=self.update_sensor_values)
        self.sensor_update_thread.start()

    def create_interface(self):
        # Блок датчиков
        sensor_frame = tk.Frame(self.root)
        sensor_frame.pack(pady=10)

        # Блок температуры
        temp_frame = tk.LabelFrame(sensor_frame, text="Температура", padx=10, pady=10)
        temp_frame.grid(row=0, column=0, padx=10, pady=5)
        self.temp_label = tk.Label(temp_frame, text=f"Температура: {self.temperature:.2f}°C")
        self.temp_label.pack(pady=5)
        self.temp_indicator = tk.Label(temp_frame, text="Нормально", bg="green", width=10)
        self.temp_indicator.pack(pady=5)
        tk.Label(temp_frame, text="Мин:").pack()
        self.temp_min_entry = tk.Entry(temp_frame)
        self.temp_min_entry.insert(0, str(self.initial_values["temp_min"]))
        self.temp_min_entry.pack()
        tk.Label(temp_frame, text="Макс:").pack()
        self.temp_max_entry = tk.Entry(temp_frame)
        self.temp_max_entry.insert(0, str(self.initial_values["temp_max"]))
        self.temp_max_entry.pack()
        self.cooler_button = tk.Button(temp_frame, text="Включить систему охлаждения", command=self.toggle_cooler)
        self.cooler_button.pack(pady=5)
        self.heater_button = tk.Button(temp_frame, text="Включить систему подогрева", command=self.toggle_heater)
        self.heater_button.pack(pady=5)

        # Блок освещенности
        light_frame = tk.LabelFrame(sensor_frame, text="Освещенность", padx=10, pady=10)
        light_frame.grid(row=0, column=1, padx=10, pady=5)
        self.light_label = tk.Label(light_frame, text=f"Уровень освещенности: {self.light_level:.2f}%")
        self.light_label.pack(pady=5)
        self.light_indicator = tk.Label(light_frame, text="Нормально", bg="green", width=10)
        self.light_indicator.pack(pady=5)
        tk.Label(light_frame, text="Мин:").pack()
        self.light_min_entry = tk.Entry(light_frame)
        self.light_min_entry.insert(0, str(self.initial_values["light_min"]))
        self.light_min_entry.pack()
        tk.Label(light_frame, text="Макс:").pack()
        self.light_max_entry = tk.Entry(light_frame)
        self.light_max_entry.insert(0, str(self.initial_values["light_max"]))
        self.light_max_entry.pack()
        self.light_button = tk.Button(light_frame, text="Интенсивность: Выкл", command=self.toggle_light_intensity)
        self.light_button.pack(pady=5)

        # Блок влажности почвы
        soil_frame = tk.LabelFrame(sensor_frame, text="Влажность почвы", padx=10, pady=10)
        soil_frame.grid(row=1, column=0, padx=10, pady=5)
        self.soil_label = tk.Label(soil_frame, text=f"Влажность почвы: {self.soil_moisture:.2f}%")
        self.soil_label.pack(pady=5)
        self.soil_indicator = tk.Label(soil_frame, text="Нормально", bg="green", width=10)
        self.soil_indicator.pack(pady=5)
        tk.Label(soil_frame, text="Мин:").pack()
        self.soil_min_entry = tk.Entry(soil_frame)
        self.soil_min_entry.insert(0, str(self.initial_values["soil_min"]))
        self.soil_min_entry.pack()
        tk.Label(soil_frame, text="Макс:").pack()
        self.soil_max_entry = tk.Entry(soil_frame)
        self.soil_max_entry.insert(0, str(self.initial_values["soil_max"]))
        self.soil_max_entry.pack()
        self.pump_button = tk.Button(soil_frame, text="Включить помпу", command=self.toggle_pump)
        self.pump_button.pack(pady=5)

        # Блок уровня воды
        water_frame = tk.LabelFrame(sensor_frame, text="Уровень воды", padx=10, pady=10)
        water_frame.grid(row=1, column=1, padx=10, pady=5)
        self.water_label = tk.Label(water_frame, text=f"Уровень воды: {self.water_level:.2f}%")
        self.water_label.pack(pady=5)
        self.water_indicator = tk.Label(water_frame, text="Нормально", bg="green", width=10)
        self.water_indicator.pack(pady=5)
        tk.Label(water_frame, text="Уведомление при ...% уровня воды").pack()
        self.water_min_entry = tk.Entry(water_frame)
        self.water_min_entry.insert(0, str(self.initial_values["water_min"]))
        self.water_min_entry.pack()
        self.water_max_entry = self.initial_values["water_max"]
        self.add_water_button = tk.Button(water_frame, text="Добавить воду", command=self.add_water)
        self.add_water_button.pack(pady=5)

        # Переключение режимов
        self.mode_label = tk.Label(self.root, text="Режим: Ручной")
        self.mode_label.pack(pady=5)
        self.mode_button = tk.Button(self.root, text="Переключить на Автоматический режим", command=self.toggle_mode)
        self.mode_button.pack(pady=5)

    def toggle_pump(self):
        if self.mode == 'manual':
            self.pump_status = not self.pump_status
            self.update_pump_status()

    def toggle_cooler(self):
        if self.mode == 'manual':
            self.cooler_status = not self.cooler_status
            self.update_cooler_status()

    def toggle_heater(self):
        if self.mode == 'manual':
            self.heater_status = not self.heater_status
            self.update_heater_status()

    def toggle_light_intensity(self):
        if self.mode == 'manual':
            self.light_intensity = (self.light_intensity + 1) % 4
            self.update_light_status()

    def toggle_mode(self):
        if self.mode == 'manual':
            self.mode = 'auto'
            self.mode_label.config(text="Режим: Автоматический")
            self.mode_button.config(text="Переключить на Ручной режим")
        else:
            self.mode = 'manual'
            self.mode_label.config(text="Режим: Ручной")
            self.mode_button.config(text="Переключить на Автоматический режим")

    def update_pump_status(self):
        self.pump_button.config(text=f"{'Выключить' if self.pump_status else 'Включить'} помпу")

    def update_cooler_status(self):
        self.cooler_button.config(text=f"{'Выключить' if self.cooler_status else 'Включить'} систему охлаждения")

    def update_heater_status(self):
        self.heater_button.config(text=f"{'Выключить' if self.heater_status else 'Включить'} систему подогрева")

    def update_light_status(self):
        intensity_texts = ['Выкл', 'Низкий', 'Средний', 'Высокий']
        self.light_button.config(text=f"Интенсивность: {intensity_texts[self.light_intensity]}")

    def add_water(self):
        self.water_level = 100.0
        self.water_label.config(text=f"Уровень воды: {self.water_level:.2f}%")
        messagebox.showinfo("Добавление воды", "Вода добавлена в резервуар")

    def update_sensor_values(self):
        while self.running:
            time.sleep(self.interval)

            # Обновление температуры
            if self.cooler_status:
                self.temperature -= round(random.uniform(1.0, 2.0), 2)  # Охлаждение
            elif self.heater_status:
                self.temperature += round(random.uniform(1.0, 2.0), 2)  # Подогрев
            else:
                self.temperature += round(random.uniform(-0.5, 0.5), 2)  # Естественные колебания

            self.temp_label.config(text=f"Температура: {self.temperature:.2f}°C")
            self.check_temperature_range()

            # Обновление уровня освещенности
            self.light_level += round(random.uniform(-3.0, 2.0), 2)  # Случайные колебания
            if self.light_intensity == 1:
                self.light_level += 1
            elif self.light_intensity == 2:
                self.light_level += 2
            elif self.light_intensity == 3:
                self.light_level += 3
            self.light_label.config(text=f"Уровень освещенности: {self.light_level:.2f}%")
            self.check_light_range()

            # Логика влажности почвы
            if self.pump_status:
                moisture_gain = round(random.uniform(2.0, 5.0), 2)
                self.soil_moisture += moisture_gain
                self.water_level -= 1.0  # Уменьшение уровня воды при включенной помпе
            else:
                moisture_loss = round(random.uniform(0.5, 1.5), 2)
                self.soil_moisture -= moisture_loss

            if self.water_level <= 10.0:
                messagebox.showwarning("Уровень воды", "Пора долить воду в резервуар!")

            self.soil_moisture = max(0, min(100, self.soil_moisture))
            self.soil_label.config(text=f"Влажность почвы: {self.soil_moisture:.2f}%")
            self.check_soil_range()

            # Обновление уровня воды
            self.water_label.config(text=f"Уровень воды: {self.water_level:.2f}%")
            self.check_water_range()

            # Автоматический режим
            if self.mode == 'auto':
                self.automatic_control()

    def check_temperature_range(self):
        temp_min = float(self.temp_min_entry.get())
        temp_max = float(self.temp_max_entry.get())
        if self.temperature < temp_min:
            self.temp_indicator.config(text="Низко", bg="blue")
        elif self.temperature > temp_max:
            self.temp_indicator.config(text="Высоко", bg="red")
        else:
            self.temp_indicator.config(text="Нормально", bg="green")

    def check_light_range(self):
        light_min = float(self.light_min_entry.get())
        light_max = float(self.light_max_entry.get())
        if self.light_level < light_min:
            self.light_indicator.config(text="Низко", bg="blue")
        elif self.light_level > light_max:
            self.light_indicator.config(text="Высоко", bg="red")
        else:
            self.light_indicator.config(text="Нормально", bg="green")

    def check_soil_range(self):
        soil_min = float(self.soil_min_entry.get())
        soil_max = float(self.soil_max_entry.get())
        if self.soil_moisture < soil_min:
            self.soil_indicator.config(text="Низко", bg="red")
        elif self.soil_moisture > soil_max:
            self.soil_indicator.config(text="Высоко", bg="red")
        else:
            self.soil_indicator.config(text="Нормально", bg="green")

    def check_water_range(self):
        water_min = float(self.water_min_entry.get())
        if self.water_level < water_min:
            self.water_indicator.config(text="Низко", bg="red")
            messagebox.showwarning("Уровень воды", f"Уровень воды ниже {water_min}%!")
        else:
            self.water_indicator.config(text="Нормально", bg="green")

    def automatic_control(self):
        temp_min = float(self.temp_min_entry.get())
        temp_max = float(self.temp_max_entry.get())
        temp_mid = (temp_min + temp_max) / 2

        # Управление системой охлаждения
        if self.temperature > temp_max:
            self.cooler_status = True
        elif self.temperature <= temp_mid:
            self.cooler_status = False
        self.update_cooler_status()

        # Управление системой подогрева
        if self.temperature < temp_min:
            self.heater_status = True
        elif self.temperature >= temp_mid:
            self.heater_status = False
        self.update_heater_status()

        # Управление освещением
        light_min = float(self.light_min_entry.get())
        light_max = float(self.light_max_entry.get())
        if self.light_level < light_min:
            if self.light_intensity != 3:
                self.light_intensity += 1
        elif self.light_level > light_max:
            if self.light_intensity != 0:
                self.light_intensity -= 1
        self.update_light_status()

        # Управление помпой
        soil_min = float(self.soil_min_entry.get())
        soil_max = float(self.soil_max_entry.get())
        if self.soil_moisture < soil_min and self.water_level > 10.0:
            self.pump_status = True
        elif self.soil_moisture > soil_max:
            self.pump_status = False
        self.update_pump_status()


root = tk.Tk()
iot_device = IoTDevice(root)
root.mainloop()
