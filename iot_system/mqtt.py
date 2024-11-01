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
        # Инициализируем MQTT-клиента
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.server, self.port)

    def on_connect(self, client, userdata, flags, rc):
        print("Подключено к MQTT-серверу с кодом:", rc)

        self.client.subscribe("remote/mode")
        self.client.subscribe("remote/cooler")
        self.client.subscribe("remote/heater")

    def on_message(self, client, userdata, msg):
        # Обработка полученного сообщения
        command = json.loads(msg.payload.decode())
        print("system Получено сообщение:", msg.topic, command)
        if msg.topic == "remote/mode" and 'mode' in command:
            self.microclimate_system.mode = command['mode']
        elif msg.topic == "remote/cooler" and 'cooler' in command:
            self.microclimate_system.cooler_status = command['cooler']
        elif msg.topic == "remote/heater" and 'heater' in command:
            self.microclimate_system.heater_status = command['heater']

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
