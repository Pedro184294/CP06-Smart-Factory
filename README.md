# CP06 — Smart Factory: Monitoramento com Edge Computing

## 1. Sobre o projeto

O projeto **Smart Factory** tem como objetivo desenvolver uma solução de monitoramento ambiental utilizando Internet das Coisas (IoT), Edge Computing e comunicação MQTT.

A solução utiliza um ESP32 conectado a um sensor DHT22 para realizar leituras de temperatura e umidade. O processamento local identifica situações normais e condições de alerta com base na temperatura, enquanto LEDs indicam visualmente o estado do ambiente.

Os dados são enviados por MQTT para uma API desenvolvida em Python com Flask. A API disponibiliza as leituras por meio de um endpoint HTTP, que é consumido por um dashboard web. A API e o dashboard são executados em contêineres Docker separados.

## 2. Integrantes do grupo

- **Turma:** 2CCPG
- **Grupo:** 23

**Integrantes:**

1. Pedro Luis Tofoli
2. Fabricio Cardoso de Oliveira
3. Vinicius Barbosa Gomes
4. Leonardo Luster Gomes
5. Nelson Troccoli Santos Neto
6. Raphael Talarico Nascimento Silva

## 3. Tecnologias utilizadas

- **ESP32:** microcontrolador responsável pelas leituras e pelo processamento local.
- **DHT22:** sensor de temperatura e umidade.
- **LEDs:** indicadores visuais para os estados normal e alerta.
- **Wokwi:** plataforma de simulação do circuito eletrônico e do firmware.
- **MQTT:** protocolo de comunicação entre o ESP32 e a API.
- **HiveMQ:** broker MQTT público.
- **Python:** linguagem utilizada no desenvolvimento do backend.
- **Flask:** framework utilizado para desenvolver a API e o dashboard.
- **Docker:** tecnologia utilizada para executar os serviços em contêineres.
- **Docker Compose:** ferramenta utilizada para configurar e iniciar os serviços.
- **HTML e CSS:** tecnologias utilizadas na interface web.

## 4. Arquitetura da solução

O fluxo de funcionamento do projeto é:

```text
Sensor DHT22
     |
     v
ESP32 — Edge Computing
     |
     | Processamento local
     | Temperatura > 35 °C: ALERTA
     | Temperatura <= 35 °C: NORMAL
     |
     | Publicação MQTT a cada 5 segundos
     v
Broker HiveMQ
     |
     | Tópico MQTT do grupo
     v
API Flask — Docker
     |
     | Endpoint HTTP GET /dados
     v
Dashboard Flask — Docker
     |
     v
Visualização de temperatura,
umidade e estado do ambiente
```

### 4.1. Processamento na borda (Edge Computing)

O processamento local ocorre no ESP32. O dispositivo recebe os dados do sensor DHT22 e compara a temperatura medida com o limite definido de 35 °C.

A classificação é realizada da seguinte forma:

| Condição | Estado | LED verde | LED vermelho |
|---|---|---|---|
| Temperatura menor ou igual a 35 °C | NORMAL | Ligado | Desligado |
| Temperatura maior que 35 °C | ALERTA | Desligado | Ligado |

A umidade é coletada e enviada junto com a temperatura, mas não interfere na classificação do estado.

O processamento local permite identificar a condição do ambiente diretamente no microcontrolador, sem depender de um servidor remoto para realizar essa comparação.

## 5. Comunicação MQTT

A comunicação entre o ESP32 e a API utiliza o broker público HiveMQ.

- **Broker:** `broker.hivemq.com`
- **Porta:** `1883`
- **Protocolo:** MQTT
- **Intervalo de publicação:** 5 segundos
- **Tópico MQTT:** `edge/2ano/2CCPG/grupo23/smartfactory/dados`

O ESP32 publica mensagens em formato JSON. Um exemplo de mensagem é:

```json
{
  "temperatura": 31.0,
  "umidade": 45.0,
  "estado": "NORMAL"
}
```

Quando a temperatura ultrapassa 35 °C, o campo `estado` passa a ser `"ALERTA"`.

A API se inscreve no mesmo tópico para receber as mensagens publicadas pelo ESP32 e disponibilizar os dados ao dashboard.

**Importante:** o tópico configurado no firmware do ESP32 deve ser exatamente igual ao tópico utilizado pela API.

## 6. Estrutura do projeto

```text
CP06-Smart-Factory/
├── api.py
├── dashboard.py
├── requirements.txt
├── Dockerfile.api
├── Dockerfile.dashboard
├── docker-compose.yml
├── .gitignore
├── README.md
└── wokwi/
    ├── diagram.json
    └── sketch.ino
```

### Descrição dos arquivos

- `api.py`: recebe as mensagens MQTT e disponibiliza os dados por meio de uma API Flask.
- `dashboard.py`: implementa o dashboard web e consulta a API para exibir as informações.
- `requirements.txt`: lista as dependências Python necessárias para a aplicação.
- `Dockerfile.api`: define a imagem Docker utilizada para executar a API.
- `Dockerfile.dashboard`: define a imagem Docker utilizada para executar o dashboard.
- `docker-compose.yml`: configura os serviços, as portas e a comunicação entre os contêineres.
- `.gitignore`: define arquivos e pastas que não devem ser versionados.
- `wokwi/diagram.json`: descreve o circuito eletrônico simulado.
- `wokwi/sketch.ino`: contém o firmware do ESP32.

## 7. Como executar o projeto

### 7.1. Pré-requisitos

Para executar a aplicação localmente, são necessários:

- Docker Desktop instalado e em execução.
- Navegador web.
- Acesso à internet para a comunicação com o broker MQTT público.

### 7.2. Passo 1 — Clonar o repositório

No terminal, execute:

```bash
git clone https://github.com/Pedro184294/CP06-Smart-Factory.git
```

Entre na pasta do projeto:

```bash
cd CP06-Smart-Factory
```

### 7.3. Passo 2 — Iniciar os contêineres

Execute o comando:

```bash
docker compose up --build
```

O Docker Compose construirá as imagens e iniciará os serviços da API e do dashboard.

### 7.4. Passo 3 — Acessar a API

Abra no navegador:

[http://localhost:5000/](http://localhost:5000/)

Para consultar os dados recebidos via MQTT, acesse:

[http://localhost:5000/dados](http://localhost:5000/dados)

O endpoint `/dados` disponibiliza os dados de temperatura, umidade e estado recebidos pela API.

### 7.5. Passo 4 — Acessar o dashboard

Abra no navegador:

[http://localhost:5001/](http://localhost:5001/)

O dashboard apresenta as informações recebidas pela API e permite atualizar os dados exibidos por meio do botão **Atualizar**.

### 7.6. Passo 5 — Encerrar a aplicação

No terminal em que o Docker Compose está sendo executado, pressione `Ctrl + C`.

Para interromper e remover os contêineres criados pelo Compose, execute:

```bash
docker compose down
```

## 8. Testes realizados

Os testes do projeto verificam a integração entre o sensor simulado, o ESP32, o broker MQTT, a API e o dashboard.

| Temperatura configurada | Estado esperado | LED verde | LED vermelho |
|---|---|---|---|
| 30 °C | NORMAL | Ligado | Desligado |
| 35 °C | NORMAL | Ligado | Desligado |
| 36 °C | ALERTA | Desligado | Ligado |
| 30 °C | NORMAL | Ligado | Desligado |

Para verificar o funcionamento integrado:

1. Iniciar a simulação do ESP32 no Wokwi.
2. Confirmar a conexão com o broker HiveMQ.
3. Verificar a publicação das mensagens MQTT.
4. Consultar o endpoint `http://localhost:5000/dados`.
5. Abrir o dashboard em `http://localhost:5001/`.
6. Alterar a temperatura no sensor simulado e aguardar a próxima publicação MQTT.
7. Atualizar o dashboard e verificar a mudança de estado.

Os testes devem confirmar que o estado é calculado localmente pelo ESP32 e que as informações chegam corretamente à API e ao dashboard.

## 9. Dificuldades encontradas e soluções

Uma das dificuldades encontradas durante o desenvolvimento foi configurar a comunicação MQTT entre o ESP32 simulado no Wokwi e a API executada em um contêiner Docker.

Para resolver essa questão, foi necessário configurar o broker HiveMQ, definir um tópico MQTT para o grupo e garantir que o firmware e a API utilizassem exatamente o mesmo tópico.

Outra configuração importante foi permitir que o dashboard acessasse a API pela rede interna do Docker Compose, utilizando o endereço `http://api:5000/dados`.

Essas configurações possibilitaram a integração entre os componentes e a exibição dos dados de monitoramento no dashboard.

## 10. Links do projeto

- **Repositório GitHub:** [https://github.com/Pedro184294/CP06-Smart-Factory](https://github.com/Pedro184294/CP06-Smart-Factory)
- **Simulação Wokwi:** [https://wokwi.com/projects/477853369056797697](https://wokwi.com/projects/477853369056797697)
- **Vídeo de demonstração:** https://youtu.be/CXNnKAGKVB8

## 11. Vídeo de demonstração

A demonstração apresentará o funcionamento integrado da solução, incluindo:

1. O circuito e o firmware do ESP32 no Wokwi.
2. As leituras de temperatura e umidade pelo DHT22.
3. O processamento local e a indicação dos LEDs.
4. A publicação de mensagens no broker MQTT.
5. A execução dos contêineres Docker.
6. A consulta dos dados pelo endpoint `/dados`.
7. A atualização do dashboard e a mudança entre os estados NORMAL e ALERTA.

O link do vídeo será compartilhado para permitir a avaliação do projeto.

---

**Checkpoint 6 — Smart Factory | Edge Computing, IoT e Docker**
