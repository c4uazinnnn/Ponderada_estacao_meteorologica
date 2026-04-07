#include "DHT.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

// ── Configurações do DHT11 ──────────────────────────────
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ── Configurações do BME280 (I2C) ──────────────────────
Adafruit_BME280 bme; 

// ── Intervalo de envio (ms) ─────────────────────────────
#define INTERVALO 5000

void setup() {
  Serial.begin(9600);
  dht.begin();

  // Inicializa BME280 — endereço padrão 0x76 ou 0x77
  if (!bme.begin(0x76)) {
    if (!bme.begin(0x77)) {
      Serial.println("{\"erro\":\"BME280 nao encontrado\"}");
    }
  }

  // Configurações recomendadas para o BME280
  bme.setSampling(Adafruit_BME280::MODE_NORMAL,
                  Adafruit_BME280::SAMPLING_X2,  // temperatura
                  Adafruit_BME280::SAMPLING_X16, // pressão
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

  // Se o BME falhar, define pressão como 0 para não quebrar o JSON
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