from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import json
from threading import Lock

app = Flask(__name__)

# Configurações do broker MQTT
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "fiap/cp06/smartfactory/temperatura"

# Dados recebidos do ESP32
dados = {
    "temperatura": None,
    "umidade": None,
    "estado": "AGUARDANDO DADOS"
}

trava = Lock()


# Executado quando o cliente conecta ao broker MQTT
def ao_conectar(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Conectado ao broker MQTT com sucesso!", flush=True)

        resultado, _ = client.subscribe(TOPIC)

        if resultado == mqtt.MQTT_ERR_SUCCESS:
            print(f"Inscrito no tópico: {TOPIC}", flush=True)
        else:
            print("Erro ao solicitar inscrição no tópico MQTT.", flush=True)
    else:
        print(f"Falha na conexão MQTT. Código: {reason_code}", flush=True)


# Executado quando uma mensagem MQTT é recebida
def ao_receber(client, userdata, msg):
    global dados

    try:
        mensagem = json.loads(msg.payload.decode("utf-8"))

        with trava:
            dados.update(mensagem)

        print(
            f"Dados recebidos no tópico {msg.topic}: {mensagem}",
            flush=True
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        print("Mensagem recebida não está em formato JSON válido.", flush=True)


# Executado quando o cliente desconecta do broker
def ao_desconectar(
    client, userdata, disconnect_flags, reason_code, properties
):
    print(
        f"Desconectado do broker MQTT. Motivo: {reason_code}",
        flush=True
    )


# Criação do cliente MQTT usando a API Paho 2.x
cliente = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2
)

cliente.on_connect = ao_conectar
cliente.on_message = ao_receber
cliente.on_disconnect = ao_desconectar


# Rota inicial da API
@app.route("/")
def inicio():
    return jsonify({
        "aplicacao": "API Smart Factory",
        "status": "online",
        "endpoint_dados": "/dados"
    })


# Endpoint com os dados atuais do sensor
@app.route("/dados")
def obter_dados():
    with trava:
        return jsonify(dados)


# Inicialização da aplicação
if __name__ == "__main__":
    try:
        print("Conectando ao broker MQTT...", flush=True)

        cliente.connect(BROKER, PORT, 60)

        print("Iniciando loop MQTT...", flush=True)
        cliente.loop_start()

        print("Iniciando API Flask na porta 5000...", flush=True)

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False
        )

    except KeyboardInterrupt:
        print("Encerrando aplicação...", flush=True)

    except Exception as erro:
        print(f"Erro ao iniciar a aplicação: {erro}", flush=True)

    finally:
        cliente.loop_stop()
        cliente.disconnect()