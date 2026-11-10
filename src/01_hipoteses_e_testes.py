from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "sim_obitos.csv"


def normalize_text(value):
    if value is None:
        return ""
    value = unicodedata.normalize("NFKD", str(value))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Z0-9 /]+", " ", value.upper())
    value = re.sub(r"\s+", " ", value).strip()
    return value


def load_rows(path: Path):
    with path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = list(reader)
    return rows


def exact_duplicates(rows):
    seen = {}
    duplicate_count = 0
    for row in rows:
        key = tuple(row.get(col, "") for col in row.keys())
        if key in seen:
            duplicate_count += 1
        else:
            seen[key] = 1
    return duplicate_count


def parse_month_year(value):
    value = normalize_text(value)
    if not value:
        return None
    found = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if not found:
        return None
    month, year = map(int, found.groups())
    if not (1 <= month <= 12):
        return None
    return year * 12 + month


def summarize(rows):
    if not rows:
        raise ValueError("CSV vazio ou inexistente.")

    columns = list(rows[0].keys())
    total_rows = len(rows)
    missing_sexo = sum(1 for row in rows if not normalize_text(row.get("sexo")))
    sexo_counts = Counter()
    tipo_counts = Counter()
    prematuro_counts = Counter()
    fetal_by_sexo = Counter()
    infantil_aproximado_by_sexo = Counter()
    infant_total = 0

    for row in rows:
        sexo = normalize_text(row.get("sexo"))
        if sexo:
            sexo_counts[sexo] += 1

        tipo = normalize_text(row.get("tipo_obito"))
        if tipo:
            tipo_counts[tipo] += 1

        prematuro = normalize_text(row.get("obito_prematuro"))
        if prematuro:
            prematuro_counts[prematuro] += 1

        if sexo and tipo == "FETAL":
            fetal_by_sexo[sexo] += 1

        if sexo and tipo == "NAO FETAL":
            nascimento = parse_month_year(row.get("nascimento"))
            obito = parse_month_year(row.get("obito"))
            if nascimento is not None and obito is not None and 0 <= obito - nascimento < 12:
                infant_total += 1
                infantil_aproximado_by_sexo[sexo] += 1

    return {
        "columns": columns,
        "total_rows": total_rows,
        "duplicate_rows": exact_duplicates(rows),
        "missing_sexo": missing_sexo,
        "sexo_counts": dict(sorted(sexo_counts.items())),
        "tipo_obito": dict(sorted(tipo_counts.items())),
        "obito_prematuro": dict(sorted(prematuro_counts.items())),
        "fetal_by_sexo": dict(sorted(fetal_by_sexo.items())),
        "infantil_aproximado_by_sexo": dict(sorted(infantil_aproximado_by_sexo.items())),
        "infantil_aproximado_total": infant_total,
    }


def print_summary(summary):
    print("Resumo da base SIM")
    print("-" * 60)
    print(f"Linhas: {summary['total_rows']}")
    print(f"Colunas: {len(summary['columns'])}")
    print(f"Linhas duplicadas exatas: {summary['duplicate_rows']}")
    print(f"Sexo ausente: {summary['missing_sexo']}")
    print()
    print("Colunas:")
    for column in summary["columns"]:
        print(f"- {column}")
    print()
    print("Sexo:")
    for key, value in summary["sexo_counts"].items():
        print(f"- {key}: {value}")
    print()
    print("Tipo de óbito:")
    for key, value in summary["tipo_obito"].items():
        print(f"- {key}: {value}")
    print()
    print("obito_prematuro:")
    for key, value in summary["obito_prematuro"].items():
        print(f"- {key}: {value}")
    print()
    print("Óbitos fetais por sexo:")
    for key, value in summary["fetal_by_sexo"].items():
        print(f"- {key}: {value}")
    print()
    print("Óbitos infantis aproximados (< 12 meses) por sexo:")
    for key, value in summary["infantil_aproximado_by_sexo"].items():
        print(f"- {key}: {value}")
    print(f"Total infantil aproximado: {summary['infantil_aproximado_total']}")


if __name__ == "__main__":
    rows = load_rows(CSV_PATH)
    summary = summarize(rows)
    print_summary(summary)
