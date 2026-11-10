from __future__ import annotations

import unittest

import pandas as pd

from src.amostragem import sortear_amostra
from src.inferencia import carregar_referencia_sinasc, executar_inferencia


class TestAmostraEInferenciaSIM(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.populacao = pd.read_parquet(
            "data/processed/populacao_infantil.parquet"
        )
        cls.amostra = pd.read_csv(
            "data/processed/amostra_infantil.csv",
            encoding="utf-8-sig",
        )

    def test_amostra_e_uma_aas_reprodutivel_sem_reposicao(self) -> None:
        primeira = sortear_amostra(self.populacao)
        segunda = sortear_amostra(self.populacao)
        self.assertEqual(len(primeira), 316)
        self.assertEqual(primeira["indice_original"].tolist(),
                         segunda["indice_original"].tolist())
        self.assertFalse(primeira["indice_original"].duplicated().any())
        self.assertTrue(
            set(primeira["indice_original"]).issubset(
                set(self.populacao["indice_original"])
            )
        )

    def test_quatro_testes_usam_amostra_e_comparam_com_populacao(self) -> None:
        resultados = executar_inferencia(self.amostra, self.populacao)
        self.assertEqual(
            [resultado["codigo"] for resultado in resultados],
            ["H1", "H2", "H3", "H4"],
        )
        self.assertEqual(
            [resultado["rejeita_h0"] for resultado in resultados],
            [False, False, True, False],
        )
        self.assertTrue(
            all(resultado["contem_parametro"] for resultado in resultados)
        )
        # H1: a proporção populacional supera a dos nascimentos, mas a AAS não
        # detecta a diferença — erro tipo II identificável pela população.
        self.assertEqual(resultados[0]["classificacao"], "Erro tipo II")
        self.assertEqual(resultados[2]["classificacao"], "Rejeição correta de H₀")

    def test_referencia_h1_vem_do_sinasc(self) -> None:
        referencia = carregar_referencia_sinasc()
        self.assertAlmostEqual(referencia["proporcao_masculina"], 0.5115, places=4)
        resultado = executar_inferencia(self.amostra, self.populacao)[0]
        self.assertAlmostEqual(
            resultado["referencia_nula"], referencia["proporcao_masculina"]
        )

    def test_limite_unilateral_e_coerente_com_a_decisao(self) -> None:
        for resultado in executar_inferencia(self.amostra, self.populacao):
            if resultado["cauda"] != "direita":
                continue
            self.assertEqual(
                resultado["limite_inferior_unilateral"] > resultado["referencia_nula"],
                resultado["rejeita_h0"],
                resultado["codigo"],
            )

    def test_proporcao_nula_explicita(self) -> None:
        resultado = executar_inferencia(self.amostra, self.populacao, 0.5)[0]
        self.assertTrue(resultado["rejeita_h0"])
        self.assertAlmostEqual(resultado["estatistica"], 1.986, places=3)

    def test_intervalos_e_valores_p_sao_validos(self) -> None:
        for resultado in executar_inferencia(self.amostra, self.populacao):
            inferior, superior = resultado["intervalo"]
            self.assertLess(inferior, superior, resultado["codigo"])
            self.assertGreaterEqual(resultado["valor_p"], 0)
            self.assertLessEqual(resultado["valor_p"], 1)


if __name__ == "__main__":
    unittest.main()
