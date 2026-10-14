
from flask import Flask, render_template_string
import requests

app = Flask(__name__)

API_URL = "http://api:5000/dados"

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <title>Smart Factory - Monitoramento</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
            margin: 0;
            padding: 40px 20px;
        }
        main {
            max-width: 850px;
            margin: auto;
        }
        h1 { text-align: center; }
        .subtitulo {
            text-align: center;
            color: #64748b;
            margin-bottom: 30px;
        }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 18px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 14px;
            box-shadow: 0 3px 12px #00000010;
        }
        .card h2 {
            font-size: 16px;
            color: #64748b;
        }
        .valor {
            font-size: 32px;
            font-weight: bold;
        }
        .estado {
            display: inline-block;
            padding: 8px 14px;
            border-radius: 20px;
            background: #dcfce7;
            color: #166534;
            font-weight: bold;
        }
        .alerta {
            background: #fee2e2;
            color: #991b1b;
        }
        footer {
            text-align: center;
            margin-top: 30px;
            color: #64748b;
            font-size: 13px;
        }
    </style>
</head>
<body>
<main>
    <h1>Smart Factory</h1>
    <p class="subtitulo">Monitoramento IoT com ESP32, MQTT e Flask</p>

    <section class="cards">
        <div class="card">
            <h2>Temperatura</h2>
            <div class="valor">{{ temperatura }}</div>
            <p>Graus Celsius (°C)</p>
        </div>

        <div class="card">
            <h2>Umidade</h2>
            <div class="valor">{{ umidade }}</div>
            <p>Umidade relativa (%)</p>
        </div>

        <div class="card">
            <h2>Estado do sistema</h2>
            <p>
                <span class="estado {{ 'alerta' if estado == 'ALERTA' else '' }}">
                    {{ estado }}
                </span>
            </p>
        </div>
    </section>

    <footer>
        Atualização automática a cada 5 segundos
    </footer>
</main>
</body>
</html>
"""


@app.route("/")
def dashboard():
    try:
        resposta = requests.get(API_URL, timeout=3)
        resposta.raise_for_status()
        dados = resposta.json()

        temperatura = dados.get("temperatura")
        umidade = dados.get("umidade")
        estado = dados.get("estado", "SEM DADOS")

        temperatura = (
            f"{temperatura:.1f}" if temperatura is not None else "--"
        )
        umidade = f"{umidade:.1f}" if umidade is not None else "--"

    except requests.RequestException:
        temperatura = "--"
        umidade = "--"
        estado = "API INDISPONÍVEL"

    return render_template_string(
        HTML,
        temperatura=temperatura,
        umidade=umidade,
        estado=estado
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)