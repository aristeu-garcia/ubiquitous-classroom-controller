# 📸 Image Analysis Service - UbiClass

Serviço responsável pela analise das imagens capturadas pela camera, detecção e envio para o Kafka como parte do sistema UbiClass.

## 🚀 Funcionalidades

- **Consumo de mensagens**: Consome as mensagens com os dados das imagens do Kafka
- **Analise de imagen**: Analisa as imagens e realiza a detecção
- **Integração Kafka**: Envio de imagens para tópicos Kafka
- **Configuração Flexível**: Configuração via variáveis de ambiente
- **Monitoramento**: Logs estruturados e tratamento de erros

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8+
- Poetry
- Kafka em execução (use o `docker-compose.kafka.yml` do projeto pai)

### Configuração do Ambiente

1. **Instalar dependências com Poetry:**
```bash
cd services/image-analysis/infra
poetry install
```

2. **Configurar variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Ativar o ambiente virtual:**
```bash
poetry env info
# para conferir o caminho até o .venv
```

## ⚙️ Configuração

As configurações são feitas através de variáveis de ambiente:

### Kafka
- `KAFKA_BOOTSTRAP_SERVERS`: Servidores Kafka (padrão: `localhost:9092`)
- `KAFKA_TOPIC_CAMERA_IMAGES`: Tópico para imagens (padrão: `camera-images`)
- `KAFKA_TOPIC_PROFESSOR_DETECTION`: Tópico para imagens (padrão: `professor-detection`)
- `KAFKA_CONSUMER_GROUP_ID`: Tópico para imagens (padrão: `image-analysis-group`)

### Modelo
- `MODEL_PATH`: Índice da câmera (padrão: `src/models/<modelo>`)
- `CONFIDENCE_THRESHOLD`: Intervalo entre capturas em segundos (padrão: `0.5`)
- `DEVICE`: Qualidade JPEG (1-100, padrão: `cpu`)

## 🏃‍♂️ Execução

### Usando Python diretamente
```bash
poetry shell
python -m src.main
# ou
PYTHONPATH=. python src/main.py
```

## 📦 Estrutura do Projeto

```
camera-service/
├── infra/
│   ├── __init__.py            # Pacote principal
│   ├── config.py              # Configuração
│   └── pyproject.toml         # Configuração do Poetry
├── src/
│   ├── __init__.py            # Pacote principal
│   ├── main.py                # Ponto de entrada do serviço
│   ├── detection_producer.py  # Producer Kafka
│   ├── image_consumer.py      # Consumer Kafka
│   └── professor_detector.py  # Detecção do professor
├── .env                       # Variáveis de ambiente
├── .env.example               # Exemplo de configuração
└── README.md                  # Este arquivo
```

## 📨 Formato das Mensagens

As mensagens enviadas ao Kafka seguem o seguinte formato JSON:

```json
{
  "timestamp": "2025-07-15T10:30:00.123456",
  "service_name": "image-analysis-service",
  "original_message_key": "2025-07-15T10:30:00.123456",
  "professor_detected": true,
  "image_metadata": {...}
}
```
