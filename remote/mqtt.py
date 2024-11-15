import json
import paho.mqtt.client as mqtt


class MQTTClient:
    def __init__(self, interface, microclimate_system, config_file="config.json"):
        self.interface = interface
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

        self.client.subscribe("current/#")
        self.client.subscribe("system/#")
        self.client.subscribe("threshold/#")

    def on_message(self, client, userdata, msg):
        # Обработка полученного сообщения
        command = json.loads(msg.payload.decode())
        print("remote Получено сообщение:", msg.topic, command)
        if msg.topic == "current/temperature":
            self.microclimate_system.temperature = command["temperature"]
        elif msg.topic == "current/light_level":
            self.microclimate_system.light_level = command["light_level"]
        elif msg.topic == "current/soil_moisture":
            self.microclimate_system.soil_moisture = command["soil_moisture"]
        elif msg.topic == "current/water_level":
            self.microclimate_system.water_level = command["water_level"]
        elif msg.topic == "system/pump_status":
            self.microclimate_system.pump_status = command["pump_status"]
        elif msg.topic == "system/cooler_status":
            self.microclimate_system.cooler_status = command["cooler_status"]
        elif msg.topic == "system/heater_status":
            self.microclimate_system.heater_status = command["heater_status"]
        elif msg.topic == "system/light_intensity":
            self.microclimate_system.light_intensity = command["light_intensity"]
        elif msg.topic == "system/mode":
            self.microclimate_system.mode = command["mode"]
        elif msg.topic == "threshold/temp_max":
            self.microclimate_system.temp_max = command["temp_max"]
        elif msg.topic == "threshold/temp_min":
            self.microclimate_system.temp_min = command["temp_min"]
        elif msg.topic == "threshold/light_max":
            self.microclimate_system.light_max = command["light_max"]
        elif msg.topic == "threshold/light_min":
            self.microclimate_system.light_min = command["light_min"]
        elif msg.topic == "threshold/soil_max":
            self.microclimate_system.soil_max = command["soil_max"]
        elif msg.topic == "threshold/soil_min":
            self.microclimate_system.soil_min = command["soil_min"]
        elif msg.topic == "threshold/water_max":
            self.microclimate_system.water_max = command["water_max"]
        elif msg.topic == "threshold/water_min":
            self.microclimate_system.water_min = command["water_min"]

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
