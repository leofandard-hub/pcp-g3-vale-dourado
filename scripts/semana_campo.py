"""Boletins da semana de campo (09 a 13/11/2026) transcritos do dossiê, SÓ PARA ANÁLISE e conferência.

ATENÇÃO: no sistema, estes boletins devem ser lançados pelas TELAS, por pelo menos três integrantes
(enunciado 2.2). Este arquivo serve para o grupo conferir o que digitou e para os cálculos da Parte 3.
"""
import pandas as pd

DIAS = ["2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13"]

# B2–B6 · mão de obra: (atividade, função, previsto, presente, h normais, h extras) por dia
_MO = {
    "2026-11-09": [("A15", "PED", 8, 6, 48, 0), ("A15", "SER", 5, 5, 40, 0), ("A11", "MON", 8, 8, 64, 0), ("A11", "SER", 5, 5, 40, 0),
                   ("A13", "PED", 8, 7, 56, 0), ("A13", "SER", 12, 11, 88, 0), ("A13", "OPE", 3, 3, 24, 0)],
    "2026-11-10": [("A15", "PED", 8, 8, 64, 0), ("A15", "SER", 5, 4, 32, 0), ("A11", "MON", 8, 8, 64, 0), ("A11", "SER", 5, 5, 40, 0),
                   ("A13", "PED", 8, 8, 64, 0), ("A13", "SER", 12, 12, 96, 0), ("A13", "OPE", 3, 3, 24, 0)],
    "2026-11-11": [("A15", "PED", 8, 7, 56, 0), ("A15", "SER", 5, 4, 32, 0), ("A11", "MON", 8, 8, 64, 0), ("A11", "SER", 5, 5, 40, 0),
                   ("A13", "PED", 8, 7, 56, 0), ("A13", "SER", 12, 11, 88, 0), ("A13", "OPE", 3, 2, 16, 0)],
    "2026-11-12": [("A15", "PED", 8, 8, 49.5, 0), ("A15", "SER", 5, 5, 30.9, 0), ("A11", "MON", 8, 7, 56, 0), ("A11", "SER", 5, 5, 40, 0),
                   ("A13", "PED", 8, 8, 64, 0), ("A13", "SER", 12, 12, 96, 0), ("A13", "OPE", 3, 3, 24, 0)],
    "2026-11-13": [("A10", "MON", 13, 12, 96, 0), ("A10", "SER", 7, 6, 48, 0), ("A11", "MON", 8, 7, 56, 0), ("A11", "SER", 5, 5, 40, 0),
                   ("A13", "PED", 8, 6, 48, 0), ("A13", "SER", 12, 12, 96, 0), ("A13", "OPE", 3, 3, 24, 0)],
}
mao_de_obra = pd.DataFrame([(d, *r) for d, rs in _MO.items() for r in rs],
                           columns=["data", "id_atividade", "funcao", "efetivo_previsto", "efetivo_presente", "horas_normais", "horas_extras"])

# produção (sem ocorrências na semana)
_PR = {"2026-11-09": [("A11", 73.8), ("A13", 218.4), ("A15", 63.8)],
       "2026-11-10": [("A11", 87.6), ("A13", 241.9), ("A15", 72.0)],
       "2026-11-11": [("A11", 98.9), ("A13", 201.8), ("A15", 71.9)],
       "2026-11-12": [("A11", 99.5), ("A13", 219.9), ("A15", 64.8)],
       "2026-11-13": [("A10", 209.7), ("A11", 90.8), ("A13", 225.8)]}
producao = pd.DataFrame([(d, a, q) for d, rs in _PR.items() for a, q in rs], columns=["data", "id_atividade", "quantidade_executada"])

# equipamentos: (equip, ativ, operando, corretiva, preventiva, ociosas, falhas, horímetro)
_EQ = {
    "2026-11-09": [("MUN-01", "A10", 0, 0, 0, 8, 0, 3105.4), ("CAM-01", "A13", 7.6, 0, 0, .4, 0, 2566.4), ("CAM-02", "A13", 7.4, 0, 0, .6, 0, 2636.6),
                   ("ROL-01", "A13", 7.2, 0, 0, .8, 0, 6886.2), ("RET-01", "A13", 6.2, 0, 0, 1.8, 0, 8716.3), ("PTA-01", "A10", 0, 0, 0, 8, 0, 2209.4),
                   ("PTA-02", "A10", 0, 0, 0, 8, 0, 5700.7), ("PTA-03", "A11", 7.5, 0, 0, .5, 0, 6383.3), ("PTA-04", "A11", 6.8, 0, 0, 1.2, 0, 4655.8)],
    "2026-11-10": [("MUN-01", "A10", 0, 2.5, 0, 5.5, 1, 3105.4), ("CAM-01", "A13", 5.9, 0, 0, 2.1, 0, 2572.3), ("CAM-02", "A13", 6.2, 0, 0, 1.8, 0, 2642.8),
                   ("ROL-01", "A13", 5.4, 0, 0, 2.6, 0, 6891.6), ("RET-01", "A13", 7.1, 0, 0, .9, 0, 8723.4), ("PTA-01", "A10", 0, 0, 0, 8, 0, 2209.4),
                   ("PTA-02", "A10", 0, 0, 0, 8, 0, 5700.7), ("PTA-03", "A11", 6.0, 0, 0, 2.0, 0, 6389.3), ("PTA-04", "A11", 7.5, 0, 0, .5, 0, 4663.4)],
    "2026-11-11": [("MUN-01", "A10", 0, 0, 0, 8, 0, 3105.4), ("CAM-01", "A13", 7.1, 0, 0, .9, 0, 2579.4), ("CAM-02", "A13", 5.2, 0, 0, 2.8, 0, 2648.1),
                   ("ROL-01", "A13", 7.5, 0, 0, .5, 0, 6899.1), ("RET-01", "A13", 5.6, 0, 0, 2.4, 0, 8729.1), ("PTA-01", "A10", 0, 0, 0, 8, 0, 2209.4),
                   ("PTA-02", "A10", 0, 0, 0, 8, 0, 5700.7), ("PTA-03", "A11", 6.8, 0, 0, 1.2, 0, 6396.1), ("PTA-04", "A11", 7.1, 0, 0, .9, 0, 4670.4)],
    "2026-11-12": [("MUN-01", "A10", 0, 0, 0, 8, 0, 3105.4), ("CAM-01", "A13", 6.4, 0, 0, 1.6, 0, 2585.8), ("CAM-02", "A13", 7.0, 0, 0, 1.0, 0, 2655.1),
                   ("ROL-01", "A13", 6.6, 0, 0, 1.4, 0, 6905.7), ("RET-01", "A13", 6.0, 0, 0, 2.0, 0, 8735.1), ("PTA-01", "A10", 0, 0, 0, 8, 0, 2209.4),
                   ("PTA-02", "A10", 0, 0, 0, 8, 0, 5700.7), ("PTA-03", "A11", 7.2, 0, 0, .8, 0, 6403.3), ("PTA-04", "A11", 7.4, 0, 0, .6, 0, 4677.9)],
    "2026-11-13": [("MUN-01", "A10", 6.9, 0, 0, 1.1, 0, 3112.3), ("CAM-01", "A13", 6.8, 0, 0, 1.2, 0, 2592.6), ("CAM-02", "A13", 6.0, 0, 0, 2.0, 0, 2661.2),
                   ("ROL-01", "A13", 7.1, 0, 0, .9, 0, 6912.8), ("RET-01", "A13", 6.4, 0, 0, 1.6, 0, 8741.5), ("PTA-01", "A10", 6.2, 0, 0, 1.8, 0, 2215.6),
                   ("PTA-02", "A10", 6.9, 0, 0, 1.1, 0, 5707.7), ("PTA-03", "A11", 5.2, 0, 0, 2.8, 0, 6408.5), ("PTA-04", "A11", 5.5, 0, 0, 2.5, 0, 4683.4)],
}
equipamentos = pd.DataFrame([(d, e, a, 8.0, *v) for d, rs in _EQ.items() for e, a, *v in rs],
                            columns=["data", "id_equipamento", "id_atividade", "horas_disponiveis", "horas_operando", "horas_manutencao_corretiva",
                                     "horas_manutencao_preventiva", "horas_ociosas", "numero_falhas", "horimetro"])

# B9 · custos (competência 13/11)
_C = [("L00431", "1.3.2", "A10", "SUBCONTRATO", 3776.64), ("L00432", "1.3.3", "A11", "SUBCONTRATO", 12669.78),
      ("L00433", "1.3.5", "A13", "MAO_DE_OBRA", 19832.00), ("L00434", "1.3.7", "A15", "MAO_DE_OBRA", 8368.15),
      ("L00435", "1.3.7", "A15", "MATERIAL", 1646.10), ("L00436", "1.3.7", "A15", "MATERIAL", 7612.53),
      ("L00437", "1.3.3", "A11", "MATERIAL", 55594.72), ("L00438", "1.3.5", "A13", "MATERIAL", 73570.39),
      ("L00439", "1.3.5", "A13", "MATERIAL", 26528.25), ("L00440", "1.3.2", "A10", "MATERIAL", 32194.58),
      ("L00441", "1.3.2", "A10", "EQUIPAMENTO", 4993.00), ("L00442", "1.3.5", "A13", "EQUIPAMENTO", 3621.15),
      ("L00443", "1.3.5", "A13", "EQUIPAMENTO", 3609.80), ("L00444", "1.3.5", "A13", "EQUIPAMENTO", 3515.85),
      ("L00445", "1.3.5", "A13", "EQUIPAMENTO", 4038.70), ("L00446", "1.3.2", "A10", "EQUIPAMENTO", 2015.50),
      ("L00447", "1.3.2", "A10", "EQUIPAMENTO", 2069.10), ("L00448", "1.3.3", "A11", "EQUIPAMENTO", 1987.55),
      ("L00449", "1.3.3", "A11", "EQUIPAMENTO", 2099.40), ("L00450", "1.9", None, "INDIRETO", 36662.43)]
custos = pd.DataFrame([(i, "2026-11-13", e, a, c, v) for i, e, a, c, v in _C],
                      columns=["id_lancamento", "data", "codigo_eap", "id_atividade", "categoria", "valor_rs"])

# B1/B10 · plano semanal S46
plano = pd.DataFrame([("PK0124", "A10", "Lúcia Farias", 435.9, 209.7, "MATERIAL"), ("PK0125", "A11", "Lúcia Farias", 401.8, 450.7, None),
                      ("PK0126", "A13", "Jair Bispo", 1030, 1108, None), ("PK0127", "A15", "Osvaldo Lins", 272.4, 272.4, None),
                      ("PK0128", "A25", "Hélio Prado", 1.86, 0.0, "SERVICO_ANTERIOR")],
                     columns=["id_pacote", "id_atividade", "encarregado", "meta_quantidade", "quantidade_realizada", "causa_nao_cumprimento"])
plano.insert(1, "semana", "2026-S46"); plano.insert(2, "data_inicio_semana", "2026-11-09")
plano["concluido"] = (plano.quantidade_realizada / plano.meta_quantidade >= 0.97).astype(int)

# B7 · pedidos emitidos e recebimento
pedidos_novos = pd.DataFrame([("PC0118", "TFR", "A26", "F10", "2026-11-09", "2026-12-29", "2026-12-15"),
                              ("PC0120", "EVP", "A27", "F10", "2026-11-09", "2026-11-05", "2026-12-11"),
                              ("PC0079", "TIN", "A16", "F12", "2026-11-11", "2026-11-27", "2026-11-23")],
                             columns=["id_pedido", "id_material", "id_atividade", "id_fornecedor", "data_pedido", "data_necessidade_obra", "data_prometida"])

if __name__ == "__main__":
    print("Hh semana:", (mao_de_obra.horas_normais + mao_de_obra.horas_extras).sum())
    print("Custo direto semana:", custos[custos.categoria != "INDIRETO"].valor_rs.sum())
    print("PPC S46:", plano.concluido.mean())
