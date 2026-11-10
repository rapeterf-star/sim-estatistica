from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "sim_obitos.csv"
OUTPUT_PATH = ROOT / "docs" / "analise_descritiva_sim.md"


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


def load_rows(path: Path):
    with path.open("r", encoding="latin-1", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return list(reader)


def compute_tables(rows):
    total_rows = len(rows)
    sex_known = Counter()
    tipo_por_sexo = Counter()
    fetal_by_sexo = Counter()
    infant_by_sexo = Counter()
    infant_total = 0
    fetal_total = 0
    fetal_total_known = 0
    fetal_missing_sexo = 0

    for row in rows:
        sexo = normalize_text(row.get("sexo"))
        tipo = normalize_text(row.get("tipo_obito"))

        if sexo:
            sex_known[sexo] += 1

        if sexo and tipo:
            tipo_por_sexo[(sexo, tipo)] += 1

        if tipo == "FETAL":
            fetal_total += 1
            if sexo:
                fetal_by_sexo[sexo] += 1
                fetal_total_known += 1
            else:
                fetal_missing_sexo += 1

        if sexo and tipo == "NAO FETAL":
            nascimento = parse_month_year(row.get("nascimento"))
            obito = parse_month_year(row.get("obito"))
            if nascimento is not None and obito is not None and 0 <= obito - nascimento < 12:
                infant_by_sexo[sexo] += 1
                infant_total += 1

    sex_known_sorted = dict(sorted(sex_known.items()))
    total_known = sum(sex_known_sorted.values())
    table_rows = []
    for sex in ["FEMININO", "MASCULINO"]:
        row = {
            "sexo": sex,
            "total_registros": sex_known_sorted.get(sex, 0),
            "percentual_total": round((sex_known_sorted.get(sex, 0) / total_known) * 100, 2) if total_known else 0.0,
            "obitos_fetais": fetal_by_sexo.get(sex, 0),
            "obitos_infantis_aprox": infant_by_sexo.get(sex, 0),
        }
        table_rows.append(row)

    return {
        "total_rows": total_rows,
        "total_sexo_conhecido": total_known,
        "sex_known": sex_known_sorted,
        "table_rows": table_rows,
        "fetal_total": fetal_total,
        "fetal_total_known": fetal_total_known,
        "fetal_missing_sexo": fetal_missing_sexo,
        "infant_total": infant_total,
        "fetal_by_sexo": dict(sorted(fetal_by_sexo.items())),
        "infant_by_sexo": dict(sorted(infant_by_sexo.items())),
    }


def render_markdown(summary):
    lines = []
    lines.append("# Análise descritiva inicial do SIM")
    lines.append("")
    lines.append("Status: resumo provisório, baseado no CSV recebido e sem correção de duplicidades ou exclusões definitivas.")
    lines.append("")
    lines.append("## 1) Panorama geral")
    lines.append("")
    lines.append(f"- Total de registros: {summary['total_rows']}")
    lines.append(f"- Registros com sexo conhecido: {summary['total_sexo_conhecido']}")
    lines.append(f"- Óbitos fetais no arquivo: {summary['fetal_total']}")
    lines.append(f"- Óbitos fetais com sexo conhecido: {summary['fetal_total_known']}")
    lines.append(f"- Óbitos fetais sem sexo informado: {summary['fetal_missing_sexo']}")
    lines.append(f"- Óbitos infantis aproximados (< 12 meses): {summary['infant_total']}")
    lines.append("")
    lines.append("## 2) Distribuição por sexo")
    lines.append("")
    lines.append("| Sexo | Registros | % do total com sexo conhecido |")
    lines.append("| --- | ---: | ---: |")
    for sex in ["FEMININO", "MASCULINO"]:
        total = summary["sex_known"].get(sex, 0)
        percent = round((total / summary['total_sexo_conhecido']) * 100, 2) if summary['total_sexo_conhecido'] else 0.0
        lines.append(f"| {sex} | {total} | {percent:.2f}% |")
    lines.append("")
    lines.append("## 3) Óbitos fetais por sexo")
    lines.append("")
    lines.append("| Sexo | Óbitos fetais com sexo conhecido | % do total de fetais com sexo conhecido |")
    lines.append("| --- | ---: | ---: |")
    for sex in ["FEMININO", "MASCULINO"]:
        count = summary["fetal_by_sexo"].get(sex, 0)
        percent = round((count / summary['fetal_total_known']) * 100, 2) if summary['fetal_total_known'] else 0.0
        lines.append(f"| {sex} | {count} | {percent:.2f}% |")
    lines.append("")
    lines.append("## 4) Óbitos infantis aproximados por sexo")
    lines.append("")
    lines.append("| Sexo | Óbitos infantis aproximados | % do total infantil aproximado |")
    lines.append("| --- | ---: | ---: |")
    for sex in ["FEMININO", "MASCULINO"]:
        count = summary["infant_by_sexo"].get(sex, 0)
        percent = round((count / summary['infant_total']) * 100, 2) if summary['infant_total'] else 0.0
        lines.append(f"| {sex} | {count} | {percent:.2f}% |")
    lines.append("")
    lines.append("## 5) Interpretação metodológica")
    lines.append("")
    lines.append("- Os valores acima são descritivos e dependem da regra operacional de óbito infantil aproximado: diferença menor que 12 meses entre os campos de nascimento e óbito.")
    lines.append("- O arquivo não registra data completa; por isso, a idade é aproximada e deve ser interpretada com cautela.")
    lines.append("- Para inferir risco por sexo, ainda são necessários denominadores agregados compatíveis do SINASC e validação geográfica, temporal e de coorte.")
    lines.append("- Não há comparação de peso ao nascer neste passo, porque a base recebida não contém esse campo e não há base oficial vinculada confirmada.")
    return "\n".join(lines) + "\n"


def main():
    rows = load_rows(CSV_PATH)
    summary = compute_tables(rows)
    markdown = render_markdown(summary)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
