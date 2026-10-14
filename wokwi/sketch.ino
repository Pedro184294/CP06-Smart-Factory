
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// ===== SENSOR DHT22 =====
#define DHT_PIN 15
#define DHT_TYPE DHT22

// ===== LEDs =====
#define LED_VERDE 25
#define LED_VERMELHO 26

// ===== WIFI DO WOKWI =====
const char *ssid = "Wokwi-GUEST";
const char *password = "";

// ===== BROKER MQTT =====
const char *mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char *mqtt_topic = "edge/2ano/2CCPG/grupo23/smartfactory/dados";

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long ultimaPublicacao = 0;

void conectarWiFi()
{
    Serial.print("Conectando ao Wi-Fi");

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWi-Fi conectado!");
    Serial.println(WiFi.localIP());
}

void conectarMQTT()
{
    while (!client.connected())
    {
        Serial.print("Conectando ao broker MQTT...");

        String clientId = "ESP32-SmartFactory-";
        clientId += String((uint32_t)ESP.getEfuseMac(), HEX);

        if (client.connect(clientId.c_str()))
        {
            Serial.println(" conectado!");
        }
        else
        {
            Serial.print(" falha, codigo: ");
            Serial.println(client.state());
            delay(2000);
        }
    }
}

void setup()
{
    Serial.begin(115200);

    pinMode(LED_VERDE, OUTPUT);
    pinMode(LED_VERMELHO, OUTPUT);

    dht.begin();

    conectarWiFi();

    client.setServer(mqtt_server, mqtt_port);

    Serial.println("Smart Factory iniciado");
}

void loop()
{
    if (!client.connected())
    {
        conectarMQTT();
    }

    client.loop();

    if (millis() - ultimaPublicacao >= 5000)
    {
        ultimaPublicacao = millis();

        float temperatura = dht.readTemperature();
        float umidade = dht.readHumidity();

        if (isnan(temperatura) || isnan(umidade))
        {
            Serial.println("Erro na leitura do DHT22");
            return;
        }

        // Processamento local (Edge Computing)
        String estado;

        if (temperatura > 35.0)
        {
            estado = "ALERTA";
            digitalWrite(LED_VERMELHO, HIGH);
            digitalWrite(LED_VERDE, LOW);
        }
        else
        {
            estado = "NORMAL";
            digitalWrite(LED_VERMELHO, LOW);
            digitalWrite(LED_VERDE, HIGH);
        }

        // Monta mensagem em formato JSON
        String mensagem = "{";
        mensagem += "\"temperatura\":" + String(temperatura, 2) + ",";
        mensagem += "\"umidade\":" + String(umidade, 2) + ",";
        mensagem += "\"estado\":\"" + estado + "\"";
        mensagem += "}";

        Serial.println(mensagem);

        // Publica os dados no broker MQTT
        if (client.publish(mqtt_topic, mensagem.c_str()))
        {
            Serial.println("Dados enviados via MQTT!");
        }
        else
        {
            Serial.println("Falha ao publicar os dados.");
        }
    }
}
