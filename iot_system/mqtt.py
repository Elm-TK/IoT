import json
import paho.mqtt.client as mqtt

from typing import TYPE_CHECKING


class MQTTClient:
    def __init__(self, microclimate_system, config_file="config.json"):
        self.microclimate_system = microclimate_system
        # Загружаем конфигурацию из файла
        with open(config_file) as f:
            config = json.load(f)
        self.server = config["mqtt_server"]
        self.port = config["mqtt_port"]
        self.topic_data = config["topic_data"]
        self.topic_control = config["topic_control"]
        # self.client_id = config["client_id"]
        # Инициализируем MQTT-клиента
        # self.client = mqtt.Client(client_id=self.client_id)
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.server, self.port)

    def on_connect(self, client, userdata, flags, rc):
        print("Подключено к MQTT-серверу с кодом:", rc)
        self.client.subscribe("remote/#")

    def on_message(self, client, userdata, msg):
        # Обработка полученного сообщения
        print("*****",msg.payload)
        try:
            # Попробуйте декодировать только если сообщение не пустое
            if msg.payload:
                command = json.loads(msg.payload.decode())
                print("system Получено сообщение:", msg.topic, command)
                if msg.topic == "remote/mode":
                    self.microclimate_system.mode = command
                elif msg.topic == "remote/cooler":
                    self.microclimate_system.cooler_status = command
                elif msg.topic == "remote/heater":
                    self.microclimate_system.heater_status = command
                elif msg.topic == "remote/light_intensity":
                    self.microclimate_system.light_intensity = command
                elif msg.topic == "remote/pump":
                    self.microclimate_system.pump_status = command
                elif msg.topic == "remote/water":
                    self.microclimate_system.water_level = command
                elif msg.topic == "remote/entries/temp_max":
                    self.microclimate_system.temp_max = command
                elif msg.topic == "remote/entries/temp_min":
                    self.microclimate_system.temp_min = command
                elif msg.topic == "remote/entries/light_max":
                    self.microclimate_system.light_max = command
                elif msg.topic == "remote/entries/light_min":
                    self.microclimate_system.light_min = command
                elif msg.topic == "remote/entries/soil_max":
                    self.microclimate_system.soil_max = command
                elif msg.topic == "remote/entries/soil_min":
                    self.microclimate_system.soil_min = command
                elif msg.topic == "remote/entries/water_min":
                    self.microclimate_system.water_min = command
            else:
                print("Получено пустое сообщение, пропускаем обработку.")
        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")

    def publish_data(self, payload):
        # Публикуем данные с датчиков
        self.client.publish(self.topic_data, payload)

    def publish_topic_data(self, topic, message):
        self.client.publish(topic, message)

    def start(self):
        # Запускаем цикл обработки сообщений
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
