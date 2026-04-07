# Estacao Meteorologica IoT - Ponderada

Projeto academico com Arduino (DHT11 + BMP280) e backend Flask para registrar e visualizar leituras de temperatura, umidade e pressao.

## O que o projeto faz

- Recebe JSON do Arduino pela serial (COM8).
- Salva leituras no SQLite.
- Exibe ultimas 10 leituras na tela inicial.
- Exibe historico completo com editar/excluir.
- Mostra grafico temporal na home.

## Estrutura

```text
app.py
database.py
schema.sql
serial_reader.py
templates/
	index.html
	historico.html
	editar.html
static/
	css/style.css
	js/main.js
```

## Como rodar (Windows)

1. Instalar dependencias:

```powershell
py -m pip install flask requests pyserial
```

2. Iniciar API Flask:

```powershell
py app.py
```

3. Iniciar leitor serial (em outro terminal):

```powershell
py serial_reader.py
```

4. Abrir no navegador:

```text
http://127.0.0.1:5000
```

## JSON esperado do Arduino

```json
{"temperatura": 25.5, "umidade": 60.0, "pressao": 1013.25}
```

## Codigo do Arduino

```cpp
#include "DHT.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// -- Configuracoes do DHT11 -----------------------------
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// -- Configuracoes do BME280 (I2C) ----------------------
Adafruit_BME280 bme;

// -- Intervalo de envio (ms) ----------------------------
#define INTERVALO 5000

void setup() {
	Serial.begin(9600);
	dht.begin();

	// Inicializa BME280 - endereco padrao 0x76 ou 0x77
	if (!bme.begin(0x76)) {
		if (!bme.begin(0x77)) {
			Serial.println("{\"erro\":\"BME280 nao encontrado\"}");
		}
	}

	// Configuracoes recomendadas para o BME280
	bme.setSampling(Adafruit_BME280::MODE_NORMAL,
									Adafruit_BME280::SAMPLING_X2,  // temperatura
									Adafruit_BME280::SAMPLING_X16, // pressao
									Adafruit_BME280::SAMPLING_X1,  // umidade
									Adafruit_BME280::FILTER_X16,
									Adafruit_BME280::STANDBY_MS_500);
}

void loop() {
	float temperatura = dht.readTemperature();
	float umidade     = dht.readHumidity();
	float pressao     = bme.readPressure() / 100.0F;

	// Valida leituras antes de enviar
	if (isnan(temperatura) || isnan(umidade)) {
		Serial.println("{\"erro\":\"Falha na leitura do DHT11\"}");
		delay(INTERVALO);
		return;
	}

	// Se o BME falhar, define pressao como 0 para nao quebrar o JSON
	if (isnan(pressao)) {
		pressao = 0.0;
	}

	// Monta e envia o JSON pela serial
	Serial.print("{");
	Serial.print("\"temperatura\":"); Serial.print(temperatura, 1);
	Serial.print(",\"umidade\":");    Serial.print(umidade, 1);
	Serial.print(",\"pressao\":");    Serial.print(pressao, 2);
	Serial.println("}");

	delay(INTERVALO);
}
```

## Endpoints principais

- GET `/`
- GET `/leituras`
- POST `/leituras`
- GET `/leituras/<id>`
- PUT `/leituras/<id>`
- DELETE `/leituras/<id>`

Para retornar JSON nas rotas GET:

```text
?formato=json
```

Exemplo:

```text
http://127.0.0.1:5000/leituras?formato=json
```

## Banco de dados

SQLite com concorrencia configurada em `database.py`:

- `journal_mode = WAL`
- `busy_timeout = 5000`

## Imagens da entrega


1. Tela inicial com grafico e ultimas leituras

![Tela inicial](docs/imagens/Tela%20inicial.png)

2. Tela de historico com botoes de editar/excluir

![Historico](docs/imagens/Tela%20de%20historico.png)

3. Serial monitor/saida do Arduino com JSON

![Serial Arduino](docs/imagens/Serial%20monitor.png)


## Problemas comuns

- COM8 ocupada: feche o Monitor Serial da Arduino IDE.
- Sem dados na tela: confirme se `py app.py` e `py serial_reader.py` estao rodando.
- Erro BMP280: revisar ligacao e inicializacao do sensor no firmware.

