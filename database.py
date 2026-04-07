import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "estacao.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_db_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    return conn


def init_db(
    db_path: str | Path = DB_PATH,
    schema_path: str | Path = SCHEMA_PATH,
) -> None:
    schema_sql = Path(schema_path).read_text(encoding="utf-8")
    with get_db_connection(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()


def inserir_leitura(
    temperatura: float,
    umidade: float,
    pressao: float,
    data_hora: str | None = None,
    db_path: str | Path = DB_PATH,
) -> int:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if data_hora is None:
            cursor.execute(
                """
                INSERT INTO leituras (temperatura, umidade, pressao)
                VALUES (?, ?, ?)
                """,
                (temperatura, umidade, pressao),
            )
        else:
            cursor.execute(
                """
                INSERT INTO leituras (temperatura, umidade, pressao, data_hora)
                VALUES (?, ?, ?, ?)
                """,
                (temperatura, umidade, pressao, data_hora),
            )
        conn.commit()
        return int(cursor.lastrowid)


def listar_leituras(
    limite: int | None = None,
    db_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, temperatura, umidade, pressao, data_hora
        FROM leituras
        ORDER BY data_hora DESC, id DESC
    """
    params: tuple[Any, ...] = ()

    if limite is not None:
        query += " LIMIT ?"
        params = (limite,)

    with get_db_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def buscar_leitura(
    leitura_id: int,
    db_path: str | Path = DB_PATH,
) -> dict[str, Any] | None:
    with get_db_connection(db_path) as conn:
        row = conn.execute(
            """
            SELECT id, temperatura, umidade, pressao, data_hora
            FROM leituras
            WHERE id = ?
            """,
            (leitura_id,),
        ).fetchone()
        return dict(row) if row else None


def atualizar_leitura(
    leitura_id: int,
    temperatura: float,
    umidade: float,
    pressao: float,
    data_hora: str | None = None,
    db_path: str | Path = DB_PATH,
) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if data_hora is None:
            cursor.execute(
                """
                UPDATE leituras
                SET temperatura = ?, umidade = ?, pressao = ?
                WHERE id = ?
                """,
                (temperatura, umidade, pressao, leitura_id),
            )
        else:
            cursor.execute(
                """
                UPDATE leituras
                SET temperatura = ?, umidade = ?, pressao = ?, data_hora = ?
                WHERE id = ?
                """,
                (temperatura, umidade, pressao, data_hora, leitura_id),
            )
        conn.commit()
        return cursor.rowcount > 0


def deletar_leitura(
    leitura_id: int,
    db_path: str | Path = DB_PATH,
) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM leituras WHERE id = ?", (leitura_id,))
        conn.commit()
        return cursor.rowcount > 0
