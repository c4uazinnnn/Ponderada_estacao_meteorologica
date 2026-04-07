from __future__ import annotations

import json
import time
from typing import Any

import requests
import serial

SERIAL_PORT = "COM8"
BAUD_RATE = 9600
API_URL = "http://127.0.0.1:5000/leituras"
TIMEOUT_SECONDS = 2


def parse_linha_serial(linha: str) -> dict[str, float] | None:
    try:
        payload: dict[str, Any] = json.loads(linha)
    except json.JSONDecodeError:
        return None

    if "erro" in payload:
        print(f"[ARDUINO] {payload['erro']}")
        return None

    required = ("temperatura", "umidade", "pressao")
    if not all(key in payload for key in required):
        print(f"[WARN] JSON recebido sem campos esperados: {payload}")
        return None

    try:
        return {
            "temperatura": float(payload["temperatura"]),
            "umidade": float(payload["umidade"]),
            "pressao": float(payload["pressao"]),
        }
    except (TypeError, ValueError):
        return None


def enviar_para_api(leitura: dict[str, float]) -> None:
    try:
        response = requests.post(API_URL, json=leitura, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        print(f"[OK] Leitura enviada: {leitura}")
    except requests.RequestException as exc:
        print(f"[ERRO] Falha ao enviar leitura para API: {exc}")


def iniciar_leitura_serial() -> None:
    print(f"Conectando na porta {SERIAL_PORT} ({BAUD_RATE} baud)...")
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print("Leitor serial iniciado. Aguardando dados do Arduino...")
        while True:
            try:
                linha = ser.readline().decode("utf-8", errors="ignore").strip()
                if not linha:
                    continue

                leitura = parse_linha_serial(linha)
                if leitura is None:
                    print(f"[WARN] Linha ignorada (nao e JSON valido esperado): {linha}")
                    continue

                enviar_para_api(leitura)
            except serial.SerialException as exc:
                print(f"[ERRO] Falha na comunicacao serial: {exc}")
                time.sleep(2)
            except KeyboardInterrupt:
                print("Encerrando leitor serial...")
                break


if __name__ == "__main__":
    iniciar_leitura_serial()
