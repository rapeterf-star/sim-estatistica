from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "data" / "raw" / "sim_obitos.csv"
SINASC_PATH = ROOT / "data" / "processed" / "sinasc_sexo_ano.csv"


def normalize_text(value):
    if value is None:
        return ""
    value = unicodedata.normalize("NFKD", str(value))
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Z0-9 /]+", " ", value.upper())
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_month_year(value):
    value = normalize_text(value)
    if not value:
        return None
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if not match:
        return None
    month, year = map(int, match.groups())
    if not (1 <= month <= 12):
        return None
    return year * 12 + month


def parse_year(value):
    value = normalize_text(value)
    if not value:
        return None
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if not match:
        return None
    _, year = match.groups()
    return int(year)


def sim_infant_deaths_by_sex_year(path: Path):
    counts = defaultdict(lambda: defaultdict(int))
    with path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            sexo = normalize_text(row.get("sexo"))
            tipo = normalize_text(row.get("tipo_obito"))
            if not sexo or tipo != "NAO FETAL":
                continue
            nascimento = parse_month_year(row.get("nascimento"))
            obito = parse_month_year(row.get("obito"))
            if nascimento is None or obito is None:
                continue
            if not (0 <= obito - nascimento < 12):
                continue
            year = parse_year(row.get("nascimento"))
            if year is None:
                continue
            counts[str(year)][sexo] += 1
    return counts


def load_sinasc_counts(path: Path):
    if not path.exists():
        return None
    counts = defaultdict(lambda: defaultdict(int))
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=';')
        for row in reader:
            ano = normalize_text(row.get("ano") or row.get("year") or row.get("ano_nascimento"))
            sexo = normalize_text(row.get("sexo") or row.get("sex"))
            nascidos = row.get("nascidos_vivos") or row.get("nascidos") or row.get("total")
            if not ano or not sexo or nascidos is None:
                continue
            try:
                value = int(float(str(nascidos).replace(".", "").replace(",", "")))
            except ValueError:
                continue
            counts[ano][sexo] += value
    return counts


def rate_per_1000(obitos, nascimentos):
    if not nascimentos:
        return None
    return (obitos / nascimentos) * 1000.0


def main():
    if not SIM_PATH.exists():
        raise FileNotFoundError(f"Arquivo SIM não encontrado: {SIM_PATH}")

    sim_counts = sim_infant_deaths_by_sex_year(SIM_PATH)
    sinasc_counts = load_sinasc_counts(SINASC_PATH)

    if sinasc_counts is None:
        print("Arquivo de denominadores do SINASC não encontrado.")
        print(f"Esperado em: {SINASC_PATH}")
        print("")
        print("Colunas esperadas no CSV agregado: ano, sexo, nascidos_vivos")
        print("Exemplo:")
        print("ano;sexo;nascidos_vivos")
        print("2011;FEMININO;20000")
        print("2011;MASCULINO;21000")
        print("")
        print("Enquanto o arquivo não for fornecido, a comparação de taxa por sexo fica bloqueada.")
        return

    years = sorted(set(sim_counts) & set(sinasc_counts), key=lambda x: int(x))
    print("Taxa de óbito infantil aproximada por sexo (SIM vs SINASC)")
    print("=" * 72)
    print("Ano | Sexo | Óbitos infantis SIM | Nascidos vivos SINASC | Taxa por 1.000")
    print("-" * 72)

    for year in years:
        for sexo in ["FEMININO", "MASCULINO"]:
            obitos = sim_counts.get(year, {}).get(sexo, 0)
            nascimentos = sinasc_counts.get(year, {}).get(sexo, 0)
            if not obitos and not nascimentos:
                continue
            taxa = rate_per_1000(obitos, nascimentos)
            if taxa is None:
                print(f"{year} | {sexo} | {obitos} | {nascimentos} | sem denominador")
            else:
                print(f"{year} | {sexo} | {obitos} | {nascimentos} | {taxa:.2f}")

    print("")
    print("Observação: a regra de óbito infantil aproximada é a diferença em meses entre nascimento e óbito, com limite inferior a 12 meses.")
    print("Essa comparação deve ser interpretada como análise preliminar e exige validação geográfica, temporal e de coorte antes de inferir risco por sexo.")


if __name__ == "__main__":
    main()
