#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Asistente simple de estructuras de SQL Server (solo metadatos).

Funcionalidades:
1) Construir un catálogo de columnas recorriendo varias bases de datos.
   El resultado se almacena localmente en SQLite (schema_catalog.db) para evitar JSON masivos.
2) Iniciar un "chat" en consola para buscar tablas/columnas por descripción
   usando coincidencias léxicas y heurísticas (sin depender de IA ni catálogos manuales).

Requisitos:
    pip install pyodbc

Uso:
    # 1. Construir catálogo
    python db_schema_assistant.py --build-catalog

    # 2. Iniciar chat
    python db_schema_assistant.py

IMPORTANTE:
- Se conecta usando Trusted Connection (Windows Authentication).
- Tu usuario de Windows debe tener como mínimo:
    GRANT VIEW DEFINITIONa
  en las bases de datos que quieras catalogar.
"""

import csv
import json
import os
import re
import sqlite3
import sys
import unicodedata
import argparse
import difflib
import pyodbc
from functools import lru_cache
from typing import List, Dict, Any, Tuple, Optional

try:
    from nltk.corpus import wordnet as wn  # type: ignore
    WORDNET_AVAILABLE = True
except (ImportError, LookupError):
    WORDNET_AVAILABLE = False

# ==========================
# CONFIGURACIÓN
# ==========================

# Nombre del servidor SQL Server (puede ser nombre o IP)
# Ejemplos:
#   "MI-SQL-SRV"
#   "MI-SQL-SRV\\INSTANCIA"
#   "10.0.0.5"
#   "localhost\\SQLEXPRESS01"
SQL_SERVER = "localhost\\SQLEXPRESS01"

# Lista de bases de datos a catalogar (usa los nombres reales)
DATABASES = [
    "GAMLO_Empleados"
    # Agrega las que necesites
]

# Archivo local donde se guarda el catálogo (SQLite para evitar JSON masivo)
CATALOG_DB_FILE = "schema_catalog.db"
BATCH_SIZE = 500
CANDIDATE_LIMIT = 400


# ==========================
# CONEXIÓN A SQL SERVER
# ==========================

def get_connection(database: str):
    """
    Crea una conexión a una base de datos específica de SQL Server
    usando Trusted Connection (Windows Authentication).
    """
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def init_catalog_store(reset: bool = False) -> sqlite3.Connection:
    """
    Inicializa la base SQLite que almacena el catálogo.
    """
    conn = sqlite3.connect(CATALOG_DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            database_name TEXT NOT NULL,
            schema_name TEXT NOT NULL,
            table_name TEXT NOT NULL,
            column_name TEXT NOT NULL,
            data_type TEXT,
            max_length INTEGER,
            is_nullable INTEGER,
            description TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_catalog_table ON catalog(table_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_catalog_column ON catalog(column_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_catalog_schema ON catalog(schema_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_catalog_desc ON catalog(description)")
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS catalog_fts 
        USING fts5(
            catalog_id UNINDEXED,
            content,
            tokenize = 'unicode61 remove_diacritics 2'
        )
    """)
    if reset:
        cursor.execute("DELETE FROM catalog")
        cursor.execute("DELETE FROM catalog_fts")
    conn.commit()
    return conn


# ==========================
# UTILIDADES DE NORMALIZACIÓN
# ==========================

WORD_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+")
CAMEL_SPLIT_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def normalize_token(value: str) -> str:
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    without_marks = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return without_marks.lower()


def split_identifier(value: str) -> List[str]:
    if not value:
        return []
    replaced = value.replace("_", " ").replace("-", " ").replace("/", " ")
    camel = CAMEL_SPLIT_PATTERN.sub(" ", replaced)
    tokens = WORD_PATTERN.findall(camel)
    return tokens


def generate_word_variants(token: str) -> List[str]:
    variants = {token}
    if token.endswith("es") and len(token) > 3:
        variants.add(token[:-2])
    if token.endswith("s") and len(token) > 3:
        variants.add(token[:-1])
    else:
        variants.add(f"{token}s")
    if token.startswith("num"):
        variants.add(token.replace("num", "numero"))
    if "numero" in token:
        variants.add(token.replace("numero", "num"))
    if token.endswith("cion"):
        variants.add(token[:-3] + "ción")
    consonants = re.sub(r"[aeiouáéíóúü]", "", token)
    if len(consonants) >= 3:
        variants.add(consonants)
    if len(token) > 4:
        variants.add(token[:4])
    variants = {v for v in variants if v}
    return list(variants)


def build_acronym(text: str) -> str:
    parts = split_identifier(text)
    acronym = "".join(part[0] for part in parts if part)
    acronym = normalize_token(acronym)
    return acronym if len(acronym) >= 2 else ""


def build_search_blob(entry: Dict[str, Any]) -> str:
    texts = []
    for field in ("database", "schema", "table", "column", "data_type", "description"):
        value = entry.get(field) or ""
        if not value:
            continue
        texts.append(value)
        texts.append(value.replace("_", " "))
    tokens = []
    for text in texts:
        for token in split_identifier(text):
            normalized = normalize_token(token)
            if normalized:
                tokens.extend(generate_word_variants(normalized))
    for field in ("table", "column"):
        acronym = build_acronym(entry.get(field, "") or "")
        if acronym:
            tokens.append(acronym)
    unique_tokens = sorted(set(tokens))
    return " ".join(unique_tokens)


def sanitize_for_fts(keyword: str) -> str:
    return re.sub(r"[^0-9a-z_]", "", keyword)


def get_wordnet_variants(token: str) -> List[str]:
    """
    Obtiene sinónimos desde WordNet (si está disponible) para enriquecer la búsqueda.
    Se apoya en los vocabularios en inglés y español. Requiere haber ejecutado:
        >>> import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')
    """
    if not WORDNET_AVAILABLE or not token:
        return []

    synonyms = set()
    try:
        synsets = wn.synsets(token, lang='spa') + wn.synsets(token, lang='eng')
    except LookupError:
        # Datos de wordnet no descargados aún
        return []

    for synset in synsets:
        for lemma in synset.lemmas(lang='eng'):
            synonyms.add(normalize_token(lemma.name()))
        try:
            for lemma in synset.lemmas(lang='spa'):
                synonyms.add(normalize_token(lemma.name()))
        except KeyError:
            # El synset puede no contener lemmas en español
            continue

    return [syn for syn in synonyms if syn and syn != token]


# ==========================
# CONSTRUCCIÓN DEL CATÁLOGO
# ==========================

def build_catalog() -> int:
    """
    Recorre las bases de datos configuradas y almacena un catálogo de columnas
    en SQLite (evita generar un JSON gigante).
    """
    catalog_conn = init_catalog_store(reset=True)
    insert_cursor = catalog_conn.cursor()
    total = 0

    for db_name in DATABASES:
        print(f"[INFO] Catalogando base de datos: {db_name} ...")
        sql_conn = get_connection(db_name)
        sql_cursor = sql_conn.cursor()

        sql_cursor.execute("""
            SELECT
                DB_NAME() AS database_name,
                s.name AS schema_name,
                t.name AS table_name,
                c.name AS column_name,
                ty.name AS data_type,
                c.max_length,
                c.is_nullable,
                ep.value AS column_description
            FROM sys.tables t
            INNER JOIN sys.schemas s ON s.schema_id = t.schema_id
            INNER JOIN sys.columns c ON c.object_id = t.object_id
            INNER JOIN sys.types ty ON ty.user_type_id = c.user_type_id
            LEFT JOIN sys.extended_properties ep 
                ON ep.major_id = c.object_id
               AND ep.minor_id = c.column_id
               AND ep.name = 'MS_Description'
            ORDER BY s.name, t.name, c.column_id;
        """)

        while True:
            rows = sql_cursor.fetchmany(BATCH_SIZE)
            if not rows:
                break

            for row in rows:
                entry = {
                    "database": row.database_name,
                    "schema": row.schema_name,
                    "table": row.table_name,
                    "column": row.column_name,
                    "data_type": row.data_type,
                    "max_length": int(row.max_length) if row.max_length is not None else None,
                    "is_nullable": int(bool(row.is_nullable)),
                    "description": str(row.column_description) if row.column_description is not None else ""
                }

                insert_cursor.execute("""
                    INSERT INTO catalog (
                        database_name, schema_name, table_name, column_name,
                        data_type, max_length, is_nullable, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry["database"],
                    entry["schema"],
                    entry["table"],
                    entry["column"],
                    entry["data_type"],
                    entry["max_length"],
                    entry["is_nullable"],
                    entry["description"]
                ))

                catalog_id = insert_cursor.lastrowid
                content_blob = build_search_blob(entry) or entry["column"]
                insert_cursor.execute("""
                    INSERT INTO catalog_fts (catalog_id, content)
                    VALUES (?, ?)
                """, (catalog_id, content_blob))

                total += 1

            catalog_conn.commit()

        sql_conn.close()

    catalog_conn.close()
    print(f"[INFO] Se catalogaron {total} columnas en total.")
    return total


# ==========================
# BÚSQUEDA "INTELIGENTE"
# ==========================

STOPWORDS = {
    # Español
    "donde", "dónde", "esta", "está", "el", "la", "los", "las",
    "de", "del", "en", "que", "qué", "cual", "cuál", "para",
    "es", "se", "guarda", "almacena", "información", "info",
    # Inglés
    "where", "is", "the", "of", "in", "on", "store", "stored", "information", "data"
}


def expand_keywords(words: List[str], debug: bool = False) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Expande las palabras clave usando normalización, heurísticas básicas y sinónimos (WordNet).
    Retorna la lista de términos y, si debug es True, las variantes generadas por cada palabra.
    """
    expanded = set()
    debug_map: Dict[str, List[str]] = {}

    for w in words:
        normalized = normalize_token(w)
        if not normalized:
            continue

        variants = set([normalized])
        heuristic = generate_word_variants(normalized)
        variants.update(heuristic)
        wordnet_variants = get_wordnet_variants(normalized)
        variants.update(wordnet_variants)
        expanded.update(variants)

        if debug:
            debug_map[normalized] = sorted(variants)

    return list(expanded), debug_map


def _collect_candidates(
    conn: sqlite3.Connection,
    keywords: List[str],
    db_filter: Optional[str] = None,
    schema_filter: Optional[str] = None,
    table_filter: Optional[str] = None,
    column_filter: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Recupera candidatos desde SQLite usando coincidencias por LIKE para cada palabra clave.
    """
    candidates: Dict[str, Dict[str, Any]] = {}
    cursor = conn.cursor()
    db_filter_norm = db_filter.upper().strip() if db_filter else None
    schema_filter_norm = schema_filter.upper().strip() if schema_filter else None
    table_filter_norm = table_filter.upper().strip() if table_filter else None
    column_filter_norm = column_filter.upper().strip() if column_filter else None

    for kw in keywords if keywords else ['*']:
        like_kw = '%' if kw == '*' else f"%{kw}%"
        query = """
            SELECT 
                database_name, schema_name, table_name, column_name,
                data_type, max_length, is_nullable, description
            FROM catalog
            WHERE (
                column_name LIKE ?
                OR table_name LIKE ?
                OR description LIKE ?
                OR schema_name LIKE ?
                OR database_name LIKE ?
            )
        """
        params: List[Any] = [like_kw, like_kw, like_kw, like_kw, like_kw]

        if db_filter_norm:
            query += " AND UPPER(database_name) = ?"
            params.append(db_filter_norm)
        if schema_filter_norm:
            query += " AND UPPER(schema_name) = ?"
            params.append(schema_filter_norm)
        if table_filter_norm:
            query += " AND UPPER(table_name) LIKE ?"
            params.append(f"%{table_filter_norm}%")
        if column_filter_norm:
            query += " AND UPPER(column_name) LIKE ?"
            params.append(f"%{column_filter_norm}%")

        query += " LIMIT ?"
        params.append(CANDIDATE_LIMIT)

        cursor.execute(query, tuple(params))

        for row in cursor.fetchall():
            key = f"{row['database_name']}|{row['schema_name']}|{row['table_name']}|{row['column_name']}"
            if key not in candidates:
                candidates[key] = {
                    "database": row["database_name"],
                    "schema": row["schema_name"],
                    "table": row["table_name"],
                    "column": row["column_name"],
                    "data_type": row["data_type"],
                    "max_length": row["max_length"],
                    "is_nullable": bool(row["is_nullable"]),
                    "description": row["description"] or ""
                }
    return list(candidates.values())


@lru_cache(maxsize=256)
def _cached_search(signature_json: str) -> List[Dict[str, Any]]:
    """
    Ejecuta la búsqueda usando una firma cacheable (keywords + filtros).
    La conexión SQLite se abre aquí para evitar serializar objetos no cacheables.
    """
    signature = json.loads(signature_json)
    keywords = signature["keywords"]
    db_filter = signature.get("db_filter")
    schema_filter = signature.get("schema_filter")
    table_filter = signature.get("table_filter")
    column_filter = signature.get("column_filter")
    limit = signature.get("limit", 10)

    conn = sqlite3.connect(CATALOG_DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        candidates = _collect_candidates(
            conn,
            keywords,
            db_filter=db_filter,
            schema_filter=schema_filter,
            table_filter=table_filter,
            column_filter=column_filter,
        )
    finally:
        conn.close()

    if not candidates:
        return []

    scored = []

    for item in candidates:
        text = f"{item['database']} {item['schema']} {item['table']} {item['column']} {item['description']}".lower()
        score = 0

        for kw in keywords:
            if kw == '*':
                continue
            if kw in item['column'].lower():
                score += 6
            elif kw in item['table'].lower():
                score += 5
            elif kw in text:
                score += 4
            else:
                s = difflib.SequenceMatcher(None, kw, text).ratio()
                if s > 0.6:
                    score += int(s * 3)

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:limit]]


def search_catalog(question: str,
                   conn: sqlite3.Connection,
                   max_results: int = 10,
                   db_filter: Optional[str] = None,
                   schema_filter: Optional[str] = None,
                   table_filter: Optional[str] = None,
                   column_filter: Optional[str] = None,
                   debug: bool = False) -> Tuple[List[Dict[str, Any]], Dict[str, List[str]]]:
    """
    Busca en el catálogo las columnas más relacionadas con la pregunta.
    Admite filtros in-line como @db=NombreBD y @schema=NombreSchema.
    """
    raw_tokens = [w.strip("¿?!.:,;()").lower() for w in question.split()]

    keywords: List[str] = []

    for token in raw_tokens:
        if token.startswith("@db="):
            db_filter = token.split("=", 1)[1]
        elif token.startswith("@schema="):
            schema_filter = token.split("=", 1)[1]
        elif token.startswith("@table="):
            table_filter = token.split("=", 1)[1]
        elif token.startswith("@column="):
            column_filter = token.split("=", 1)[1]
        elif token and token not in STOPWORDS:
            keywords.append(token)

    keywords, debug_map = expand_keywords(keywords, debug=debug)

    if not keywords:
        # Permitir consultas solo con filtros usando comodín
        keywords = ['*']

    signature_json = json.dumps({
        "keywords": keywords,
        "db_filter": db_filter,
        "schema_filter": schema_filter,
        "table_filter": table_filter,
        "column_filter": column_filter,
        "limit": max_results,
    }, sort_keys=True)

    results = _cached_search(signature_json)
    return results, debug_map


# ==========================
# LOOP DE CHAT EN CONSOLA
# ==========================

def format_result(item: Dict[str, Any]) -> str:
    """
    Devuelve una línea de texto legible para un resultado.
    """
    desc = item.get("description") or ""
    if len(desc) > 60:
        desc = desc[:57] + "..."
    return (
        f"DB: {item['database']} | {item['schema']}.{item['table']} -> "
        f"{item['column']} ({item['data_type']})"
        + (f" | desc: {desc}" if desc else "")
    )


def run_chat(output_format: str = "text", limit: int = 10, debug: bool = False):
    """
    Inicia un chat simple por consola.
    """
    if not os.path.exists(CATALOG_DB_FILE):
        print(f"[ERROR] No se encontró {CATALOG_DB_FILE}. Ejecuta primero el script con --build-catalog.")
        return

    conn = sqlite3.connect(CATALOG_DB_FILE)
    conn.row_factory = sqlite3.Row

    print("==============================================")
    print(" Asistente de estructura de BD (solo metadatos)")
    print(" Escribe 'salir' para terminar.")
    print(" Ejemplos de preguntas:")
    print("   - ¿Dónde está el número de cuenta del cliente?")
    print("   - columnas donde se guarda la cédula del cliente")
    print("   - Usa filtros como @db=NombreBD, @schema=Schema, @table=Tabla, @column=Columna")
    print("==============================================")

    while True:
        try:
            q = input("\nTú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Saliendo...")
            break

        if not q:
            continue

        if q.lower() in ("salir", "exit", "quit"):
            print("[INFO] Saliendo...")
            break

        results, debug_map = search_catalog(
            q,
            conn,
            max_results=limit,
            debug=debug,
        )

        if debug and debug_map:
            print("DEBUG: Variantes generadas por palabra:")
            for token, variants in debug_map.items():
                print(f"  {token}: {', '.join(variants)}")

        if not results:
            print("Bot: No encontré columnas relacionadas con esa descripción.")
            continue

        if output_format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif output_format == "csv":
            writer = csv.DictWriter(
                sys.stdout,
                fieldnames=["database", "schema", "table", "column", "data_type", "description"]
            )
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "database": r["database"],
                    "schema": r["schema"],
                    "table": r["table"],
                    "column": r["column"],
                    "data_type": r["data_type"],
                    "description": r["description"],
                })
        else:
            print("Bot: Podría estar en alguno de estos campos:")
            for r in results:
                print("  - " + format_result(r))

    conn.close()


# ==========================
# MAIN
# ==========================

def main():
    parser = argparse.ArgumentParser(description="Asistente de metadatos SQL Server.")
    parser.add_argument(
        "--build-catalog",
        action="store_true",
        help="Reconstruye el catálogo de columnas a partir de las bases de datos configuradas."
    )
    parser.add_argument(
        "--output",
        choices=["text", "json", "csv"],
        default="text",
        help="Formato de salida para los resultados del chat."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Número máximo de resultados por consulta."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Muestra las variantes/sinónimos generados para cada término."
    )
    args = parser.parse_args()

    if args.build_catalog:
        total = build_catalog()
        print(f"[INFO] Catálogo guardado en {CATALOG_DB_FILE} ({total} columnas).")
    else:
        run_chat(output_format=args.output, limit=args.limit, debug=args.debug)


if __name__ == "__main__":
    main()
