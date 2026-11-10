from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINASC_SOURCE = Path(r"c:\Users\maque\VSCODE\sinasc-estatistica\data\sinasc_nascimentos.csv")
SINASC_OUTPUT = ROOT / "data" / "processed" / "sinasc_sexo_ano.csv"


def normalize_text(value):
    if value is None:
        return ""
    value = unicodedata.normalize("NFKD", str(value))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Z0-9 /]+", " ", value.upper())
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_year_from_month_year(value):
    value = normalize_text(value)
    if not value:
        return None
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if not match:
        return None
    _, year = match.groups()
    return int(year)


def main():
    if not SINASC_SOURCE.exists():
        raise FileNotFoundError(f"Arquivo do SINASC não encontrado: {SINASC_SOURCE}")

    counts = defaultdict(lambda: defaultdict(int))
    with SINASC_SOURCE.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            sexo = normalize_text(row.get("sexo"))
            if sexo not in {"FEMININO", "MASCULINO"}:
                continue
            ano = parse_year_from_month_year(row.get("data_nascimento"))
            if ano is None:
                continue
            counts[ano][sexo] += 1

    SINASC_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with SINASC_OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=';')
        writer.writerow(["ano", "sexo", "nascidos_vivos"])
        for ano in sorted(counts):
            for sexo in ["FEMININO", "MASCULINO"]:
                writer.writerow([ano, sexo, counts[ano].get(sexo, 0)])

    print(f"Arquivo gerado em: {SINASC_OUTPUT}")
    print("Resumo:")
    for ano in sorted(counts):
        print(ano, dict(counts[ano]))


if __name__ == "__main__":
    main()
