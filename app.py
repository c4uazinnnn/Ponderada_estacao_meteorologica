from __future__ import annotations

import json

from flask import Flask, Response, jsonify, render_template, request

from database import (
    buscar_leitura,
    deletar_leitura,
    init_db,
    inserir_leitura,
    listar_leituras,
    atualizar_leitura,
)

app = Flask(__name__)


def wants_json() -> bool:
    return request.args.get("formato", "").lower() == "json"


def _to_float(payload: dict, key: str) -> float:
    if key not in payload:
        raise ValueError(f"Campo obrigatorio ausente: {key}")
    try:
        return float(payload[key])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Campo invalido: {key}") from exc


@app.route("/", methods=["GET"])
def index() -> Response | str:
    leituras = listar_leituras(limite=10)
    if wants_json():
        return jsonify({"total": len(leituras), "leituras": leituras})
    leituras_grafico = list(reversed(leituras))
    return render_template(
        "index.html",
        leituras=leituras,
        leituras_json=json.dumps(leituras_grafico, ensure_ascii=False),
    )


@app.route("/leituras", methods=["GET"])
def historico_leituras() -> Response | str:
    leituras = listar_leituras()
    if wants_json():
        return jsonify({"total": len(leituras), "leituras": leituras})
    return render_template("historico.html", leituras=leituras)


@app.route("/leituras", methods=["POST"])
def criar_leitura() -> Response:
    payload = request.get_json(silent=True) or {}
    try:
        temperatura = _to_float(payload, "temperatura")
        umidade = _to_float(payload, "umidade")
        pressao = _to_float(payload, "pressao")
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400

    leitura_id = inserir_leitura(
        temperatura=temperatura,
        umidade=umidade,
        pressao=pressao,
    )
    leitura = buscar_leitura(leitura_id)
    return jsonify({"mensagem": "Leitura criada", "leitura": leitura}), 201


@app.route("/leituras/<int:leitura_id>", methods=["GET"])
def detalhe_leitura(leitura_id: int) -> Response | str:
    leitura = buscar_leitura(leitura_id)
    if not leitura:
        return jsonify({"erro": "Leitura nao encontrada"}), 404

    if wants_json():
        return jsonify(leitura)
    return render_template("editar.html", leitura=leitura)


@app.route("/leituras/<int:leitura_id>", methods=["PUT"])
def editar_leitura(leitura_id: int) -> Response:
    if not buscar_leitura(leitura_id):
        return jsonify({"erro": "Leitura nao encontrada"}), 404

    payload = request.get_json(silent=True) or {}
    try:
        temperatura = _to_float(payload, "temperatura")
        umidade = _to_float(payload, "umidade")
        pressao = _to_float(payload, "pressao")
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400

    atualizado = atualizar_leitura(
        leitura_id=leitura_id,
        temperatura=temperatura,
        umidade=umidade,
        pressao=pressao,
    )
    if not atualizado:
        return jsonify({"erro": "Nao foi possivel atualizar"}), 409

    leitura = buscar_leitura(leitura_id)
    return jsonify({"mensagem": "Leitura atualizada", "leitura": leitura})


@app.route("/leituras/<int:leitura_id>", methods=["DELETE"])
def remover_leitura(leitura_id: int) -> Response:
    removido = deletar_leitura(leitura_id)
    if not removido:
        return jsonify({"erro": "Leitura nao encontrada"}), 404

    if wants_json():
        return jsonify({"mensagem": "Leitura removida", "id": leitura_id})

    html = f"""
    <!doctype html>
    <html lang=\"pt-BR\">
      <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Leitura removida</title>
      </head>
      <body>
        <h1>Leitura removida</h1>
        <p>Leitura {leitura_id} removida com sucesso.</p>
        <p><a href=\"/leituras\">Voltar para historico</a></p>
      </body>
    </html>
    """
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
