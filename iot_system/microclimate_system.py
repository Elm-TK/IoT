import json
import random
import threading
import time
from tkinter import *

from mqtt import MQTTClient


class MicroclimateSystem:
    def __init__(self, is_remote=False):

        # Инициализационные переменные (Максимальные, минимальные, начальные значения)
        self.temp_min = 15.0
        self.temp_max = 30.0
        self.light_min = 40.0
        self.light_max = 80.0
        self.soil_min = 40.0
        self.soil_max = 70.0
        self.water_min = 20.0
        self.water_max = 100.0

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

        if not is_remote:
            # Инициализация MQTT
            self.mqtt_client = MQTTClient(self)
            self.mqtt_client.start()
            # Таймер для обновления данных
            self.interval = 5
            self.running = True
            self.sensor_update_thread = threading.Thread(target=self.update_sensor_values)
            self.sensor_update_thread.start()

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

            # Обновление уровня освещенности
            self.light_level += round(random.uniform(-3.0, 2.0), 2)  # Случайные колебания
            if self.light_intensity == 1:
                self.light_level += 1
            elif self.light_intensity == 2:
                self.light_level += 2
            elif self.light_intensity == 3:
                self.light_level += 3

            # Логика влажности почвы
            if self.pump_status:
                moisture_gain = round(random.uniform(2.0, 5.0), 2)
                self.soil_moisture += moisture_gain
                self.water_level -= 1.0  # Уменьшение уровня воды при включенной помпе
            else:
                moisture_loss = round(random.uniform(0.5, 1.5), 2)
                self.soil_moisture -= moisture_loss

            self.soil_moisture = max(0, min(100, self.soil_moisture))

            # Автоматический режим
            if self.mode == 'auto':
                self.automatic_control()

            sensor_data = {
                "temperature": round(self.temperature, 2),
                "light_level": round(self.light_level, 2),
                "soil_moisture": round(self.soil_moisture, 2),
                "water_level": round(self.water_level, 2),
            }

            # Публикуем данные по разным топикам для каждого сенсора
            for sensor, value in sensor_data.items():
                self.mqtt_client.publish_topic_data(f"current/{sensor}", value)

            systems_status = {
                "pump_status": self.pump_status,
                "cooler_status": self.cooler_status,
                "heater_status": self.heater_status,
                "light_intensity": self.light_intensity,
                "mode": self.mode,
            }
            for system, status in systems_status.items():
                self.mqtt_client.publish_topic_data(f"system/{system}", json.dumps(status))

                threshold_values = {
                    "temp_max": self.temp_max,
                    "temp_min": self.temp_min,
                    "light_max": self.light_max,
                    "light_min": self.light_min,
                    "soil_max": self.soil_max,
                    "soil_min": self.soil_min,
                    "water_max": self.water_max,
                    "water_min": self.water_min,
                }

                for threshold, value in threshold_values.items():
                    self.mqtt_client.publish_topic_data(f"threshold/{threshold}", value)

    def automatic_control(self):
        temp_mid = (self.temp_min + self.temp_max) / 2

        # Управление системой охлаждения
        if self.temperature > self.temp_max:
            self.cooler_status = True
        elif self.temperature <= temp_mid:
            self.cooler_status = False

        # Управление системой подогрева
        if self.temperature < self.temp_min:
            self.heater_status = True
        elif self.temperature >= temp_mid:
            self.heater_status = False

        # Управление освещением
        if self.light_level < self.light_min:
            if self.light_intensity != 3:
                self.light_intensity += 1
        elif self.light_level > self.light_max:
            if self.light_intensity != 0:
                self.light_intensity -= 1

        # Управление помпой
        if self.soil_moisture < self.soil_min and self.water_level > 10.0:
            self.pump_status = True
        elif self.soil_moisture > self.soil_max:
            self.pump_status = False


if __name__ == "__main__":
    MicroclimateSystem()
