# 📸 Camera Service - UbiClass

Serviço responsável pela captura de imagens da câmera e envio para o Kafka como parte do sistema UbiClass.

## 🚀 Funcionalidades

- **Captura Contínua**: Coleta imagens da câmera em intervalos configuráveis
- **Processamento de Imagem**: Codificação em base64 e otimização de qualidade
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
cd services/camera-service/infra
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

### Câmera
- `CAMERA_INDEX`: Índice da câmera (padrão: `0`)
- `CAPTURE_INTERVAL`: Intervalo entre capturas em segundos (padrão: `5`)
- `IMAGE_QUALITY`: Qualidade JPEG (1-100, padrão: `80`)
- `IMAGE_WIDTH`: Largura da imagem (padrão: `640`)
- `IMAGE_HEIGHT`: Altura da imagem (padrão: `480`)

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
│   ├── __init__.py          # Pacote principal
│   ├── config.py            # Configuração
│   └── pyproject.toml       # Configuração do Poetry
├── src/
│   ├── __init__.py          # Pacote principal
│   ├── main.py              # Ponto de entrada do serviço
│   ├── camera.py            # Módulo de captura de câmera
│   └── kafka_producer.py    # Producer Kafka
├── .env                     # Variáveis de ambiente
├── .env.example             # Exemplo de configuração
└── README.md                # Este arquivo
```

## 📨 Formato das Mensagens

As mensagens enviadas ao Kafka seguem o seguinte formato JSON:

```json
{
  "timestamp": "2025-07-15T10:30:00.123456",
  "service_name": "camera-service",
  "camera_index": 0,
  "image_data": "base64_encoded_image_data...",
  "image_format": "JPEG",
  "image_quality": 80,
  "image_width": 640,
  "image_height": 480,
  "encoding": "base64"
}
```
