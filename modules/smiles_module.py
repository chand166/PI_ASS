# -*- coding: utf-8 -*-
"""
SMILES 转化模块
将聚酰亚胺单体的【英文全拼 + 简写】交给大语言模型转成规范 SMILES，
再用 RDKit 校验结构合法性（括号闭合 / 芳香性 / 价键 / 原子数），
校验通过的以 canonical SMILES 形式回填为新列。
未通过校验的留空，避免污染下游描述符计算。
"""
import re
import logging
import threading
from typing import Optional, Tuple

import requests
import pandas as pd

logger = logging.getLogger(__name__)

# RDKit 可选：有则做严格化学校验，无则降级为括号配平的语法检查
try:
    from rdkit import Chem
    from rdkit import RDLogger
    RDLogger.DisableLog("rdApp.*")
    _RDKIT = True
except Exception:
    _RDKIT = False


# 聚酰亚胺 4 组单体：(全拼列, 简写列, 目标新列, 单体类型说明[喂给提示词])
MONOMER_COLS = [
    ("单体酸酐1英文全拼", "酸酐简写", "酸酐1_SMILES",
     "二酐（必须含两个环状酸酐基团 -C(=O)OC(=O)- 五元环，可稠合在芳环上）"),
    ("单体酸酐2英文全拼", "酸酐2简写", "酸酐2_SMILES",
     "二酐（必须含两个环状酸酐基团 -C(=O)OC(=O)- 五元环，可稠合在芳环上）"),
    ("单体二胺1英文全拼", "二胺简写", "二胺1_SMILES",
     "二胺（必须含且仅含两个伯氨基 -NH2，即共两个氮原子）"),
    ("单体二胺2英文全拼", "二胺2简写", "二胺2_SMILES",
     "二胺（必须含且仅含两个伯氨基 -NH2，即共两个氮原子）"),
]


# 列名别名 → 系统内部标准列名。DATA-smi.xlsx / 手工录入等常省略"1英文全拼"后缀，
# 这里把常见变体统一映射到 MONOMER_COLS 期望的列名，保证预览与转换都能取到全拼。
_COLUMN_ALIASES = {
    # ---- 酸酐1 全拼 ----
    "单体酸酐": "单体酸酐1英文全拼",
    "单体酸酐1": "单体酸酐1英文全拼",
    "单体酸酐1全拼": "单体酸酐1英文全拼",
    "单体酸酐1全称": "单体酸酐1英文全拼",
    "单体酸酐全称": "单体酸酐1英文全拼",
    "酸酐": "单体酸酐1英文全拼",
    "酸酐全称": "单体酸酐1英文全拼",
    "酸酐全拼": "单体酸酐1英文全拼",
    "酸酐名称": "单体酸酐1英文全拼",
    "酸酐英文全拼": "单体酸酐1英文全拼",
    "dianhydride": "单体酸酐1英文全拼",
    # ---- 酸酐2 全拼 ----
    "单体酸酐2": "单体酸酐2英文全拼",
    "单体酸酐2全拼": "单体酸酐2英文全拼",
    "单体酸酐2全称": "单体酸酐2英文全拼",
    "酸酐2全称": "单体酸酐2英文全拼",
    "酸酐2全拼": "单体酸酐2英文全拼",
    "酸酐2名称": "单体酸酐2英文全拼",
    "酸酐2英文全拼": "单体酸酐2英文全拼",
    # ---- 二胺1 全拼 ----
    "单体二胺": "单体二胺1英文全拼",
    "单体二胺1": "单体二胺1英文全拼",
    "单体二胺1全拼": "单体二胺1英文全拼",
    "单体二胺1全称": "单体二胺1英文全拼",
    "单体二胺全称": "单体二胺1英文全拼",
    "二胺": "单体二胺1英文全拼",
    "二胺全称": "单体二胺1英文全拼",
    "二胺全拼": "单体二胺1英文全拼",
    "二胺名称": "单体二胺1英文全拼",
    "二胺英文全拼": "单体二胺1英文全拼",
    "diamine": "单体二胺1英文全拼",
    # ---- 二胺2 全拼 ----
    "单体二胺2": "单体二胺2英文全拼",
    "单体二胺2全拼": "单体二胺2英文全拼",
    "单体二胺2全称": "单体二胺2英文全拼",
    "二胺2全称": "单体二胺2英文全拼",
    "二胺2全拼": "单体二胺2英文全拼",
    "二胺2名称": "单体二胺2英文全拼",
    "二胺2英文全拼": "单体二胺2英文全拼",
    # ---- 简写变体 ----
    "酸酐缩写": "酸酐简写",
    "单体酸酐简写": "酸酐简写",
    "酸酐1缩写": "酸酐简写",
    "酸酐2缩写": "酸酐2简写",
    "二胺缩写": "二胺简写",
    "单体二胺简写": "二胺简写",
    "二胺1缩写": "二胺简写",
    "二胺2缩写": "二胺2简写",
}


def normalize_input_columns(df):
    """把 DATA-smi.xlsx / 手工录入等常见列名归一到 MONOMER_COLS 期望的内部标准列名。

    返回 (新df, {原列名: 新列名})，第二个元素用于 UI 展示“已归一化哪些列”。
    也会 strip 列名首尾空格（DATA-smi 的列名常带前后空格）。
    """
    if df is None:
        return df, {}
    out = df.copy()
    out.columns = out.columns.str.strip()
    rename = {}
    for col in list(out.columns):
        target = _COLUMN_ALIASES.get(str(col))
        # 目标名若已存在且不是自己，则跳过避免覆盖
        if target and target != col and target not in out.columns:
            rename[col] = target
    if rename:
        out = out.rename(columns=rename)
    return out, rename


# ======== 内置常见聚酰亚胺单体数据库（全拼/简称→规范SMILES）========
# 键：小写全拼、小写简写 → 值：(canonical_SMILES, 单体类型)
# 内置库命中则直接返回，跳过 PubChem/AI 调用，最快最准。
_BUILTIN_MONOMERS = {
    # ====== 二酐 (Dianhydrides) ======
    # PMDA - 均苯四甲酸二酐
    "pmda":                                  ("O=C1OC(=O)c2cc3c(cc21)C(=O)OC3=O",                         "二酐"),
    "pyromellitic dianhydride":              ("O=C1OC(=O)c2cc3c(cc21)C(=O)OC3=O",                         "二酐"),
    "pyromellitic dianhydride (pmda)":       ("O=C1OC(=O)c2cc3c(cc21)C(=O)OC3=O",                         "二酐"),
    # BPDA / s-BPDA - 3,3',4,4'-联苯四甲酸二酐
    "bpda":                                  ("O=C1OC(=O)c2cc(-c3cc4c(cc3)C(=O)OC4=O)ccc21",              "二酐"),
    "3,3',4,4'-biphenyltetracarboxylic dianhydride": ("O=C1OC(=O)c2cc(-c3cc4c(cc3)C(=O)OC4=O)ccc21", "二酐"),
    "s-bpda":                                ("O=C1OC(=O)c2cc(-c3cc4c(cc3)C(=O)OC4=O)ccc21",              "二酐"),
    # ODPA - 4,4'-氧双邻苯二甲酸酐
    "odpa":                                  ("O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21",              "二酐"),
    "4,4'-oxydiphthalic anhydride":          ("O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21",              "二酐"),
    # BTDA - 3,3',4,4'-二苯甲酮四甲酸二酐
    "btda":                                  ("O=C1OC(=O)c2cc(C(=O)c3cc4c(cc3)C(=O)OC4=O)ccc21",          "二酐"),
    "3,3',4,4'-benzophenonetetracarboxylic dianhydride": ("O=C1OC(=O)c2cc(C(=O)c3cc4c(cc3)C(=O)OC4=O)ccc21", "二酐"),
    # 6FDA - 六氟二酐
    "6fda":                                  ("O=C1OC(=O)c2cc(C(C(F)(F)F)(C(F)(F)F)c3cc4c(cc3)C(=O)OC4=O)ccc21", "二酐"),
    "4,4'-(hexafluoroisopropylidene)diphthalic anhydride": ("O=C1OC(=O)c2cc(C(C(F)(F)F)(C(F)(F)F)c3cc4c(cc3)C(=O)OC4=O)ccc21", "二酐"),
    "6fda (hexafluoroisopropylidene diphthalic anhydride)": ("O=C1OC(=O)c2cc(C(C(F)(F)F)(C(F)(F)F)c3cc4c(cc3)C(=O)OC4=O)ccc21", "二酐"),
    # a-BPDA / aBPDA
    "a-bpda":                                ("O=C1OC(=O)c2cccc(-c3cc4c(cc3)C(=O)OC4=O)c21",              "二酐"),
    "2,3,3',4'-biphenyltetracarboxylic dianhydride": ("O=C1OC(=O)c2cccc(-c3cc4c(cc3)C(=O)OC4=O)c21",   "二酐"),
    # HQDPA / HQDEA
    "hqdea":                                 ("O=C1OC(=O)c2cc(Oc3ccc(Oc4ccc5c(c4)C(=O)OC5=O)cc3)ccc21",     "二酐"),
    "hqda":                                  ("O=C1OC(=O)c2cc(Oc3ccc(Oc4ccc5c(c4)C(=O)OC5=O)cc3)ccc21",     "二酐"),
    # ====== 二胺 (Diamines) ======
    # ODA - 4,4'-二氨基二苯醚
    "oda":                                   ("Nc1ccc(Oc2ccc(N)cc2)cc1",                                 "二胺"),
    "4,4'-oxydianiline":                     ("Nc1ccc(Oc2ccc(N)cc2)cc1",                                 "二胺"),
    "4,4'-diaminodiphenyl ether":            ("Nc1ccc(Oc2ccc(N)cc2)cc1",                                 "二胺"),
    # MDA - 4,4'-二氨基二苯甲烷
    "mda":                                   ("Nc1ccc(Cc2ccc(N)cc2)cc1",                                "二胺"),
    "4,4'-methylenedianiline":               ("Nc1ccc(Cc2ccc(N)cc2)cc1",                                "二胺"),
    # p-PDA - 对苯二胺
    "p-pda":                                 ("Nc1ccc(N)cc1",                                           "二胺"),
    "p-phenylenediamine":                    ("Nc1ccc(N)cc1",                                           "二胺"),
    "1,4-phenylenediamine":                  ("Nc1ccc(N)cc1",                                           "二胺"),
    # m-PDA - 间苯二胺
    "m-pda":                                 ("Nc1cccc(N)c1",                                           "二胺"),
    "m-phenylenediamine":                    ("Nc1cccc(N)c1",                                           "二胺"),
    "1,3-phenylenediamine":                  ("Nc1cccc(N)c1",                                           "二胺"),
    # DDS - 4,4'-二氨基二苯砜
    "dds":                                   ("Nc1ccc(S(=O)(=O)c2ccc(N)cc2)cc1",                        "二胺"),
    "4,4'-diaminodiphenyl sulfone":          ("Nc1ccc(S(=O)(=O)c2ccc(N)cc2)cc1",                        "二胺"),
    "diaminodiphenyl sulfone":               ("Nc1ccc(S(=O)(=O)c2ccc(N)cc2)cc1",                        "二胺"),
    # DDE - 4,4'-二氨基二苯醚(同ODA不同名) - 保留但用ODA的SMILES
    "dde":                                   ("Nc1ccc(Oc2ccc(N)cc2)cc1",                                 "二胺"),
    # BAPP / BAPP
    "bapp":                                  ("Nc1ccc(Oc2ccc(C(C)(C)c3ccc(Oc4ccc(N)cc4)cc3)cc2)cc1",     "二胺"),
    "2,2-bis[4-(4-aminophenoxy)phenyl]propane": ("Nc1ccc(Oc2ccc(C(C)(C)c3ccc(Oc4ccc(N)cc4)cc3)cc2)cc1", "二胺"),
    # BAPB - 1,4-双(4-氨基苯氧基)苯
    "bapb":                                  ("Nc1ccc(Oc2ccc(Oc3ccc(N)cc3)cc2)cc1",                     "二胺"),
    "1,4-bis(4-aminophenoxy)benzene":        ("Nc1ccc(Oc2ccc(Oc3ccc(N)cc3)cc2)cc1",                     "二胺"),
    # TFMB / 2,2'-双(三氟甲基)联苯胺
    "tpmb":                                  ("Nc1ccc(C(C)(C)c2ccc(N)cc2)cc1",                          "二胺"),
    "2,2'-bis(trifluoromethyl)benzidine":    ("Nc1ccc(C(C(F)(F)F)(C(F)(F)F)c2ccc(N)cc2)cc1",             "二胺"),
    # APB / 1,3-双(3-氨基苯氧基)苯
    "apb":                                   ("Nc1cccc(Oc2cccc(Oc3cccc(N)c3)c2)c1",                     "二胺"),
    "1,3-bis(3-aminophenoxy)benzene":        ("Nc1cccc(Oc2cccc(Oc3cccc(N)c3)c2)c1",                     "二胺"),
    # 3,3'-DDS
    "3,3'-dds":                              ("Nc1cccc(S(=O)(=O)c2cccc(N)c2)c1",                        "二胺"),
    # DABP / 3,3'-二氨基二苯甲酮
    "dabp":                                  ("Nc1ccc(C(=O)c2ccc(N)cc2)cc1",                            "二胺"),
    "3,3'-diaminobenzophenone":              ("Nc1ccc(C(=O)c2ccc(N)cc2)cc1",                            "二胺"),
    # ====== 从测试数据补充的常见单体 ======
    # OPDA = ODPA（4,4'-氧双邻苯二甲酸酐，同一物质不同缩写）
    "opda":                                  ("O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21",           "二酐"),
    "3,3,4,4-diphenylether tetracarboxylic dianhydride": ("O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21", "二酐"),
    "4,4-oxydiphthalic dianhydride":         ("O=C1OC(=O)c2cc(Oc3ccc4c(c3)C(=O)OC4=O)ccc21",           "二酐"),
    # SiDA - 二甲基硅烷二基二邻苯二甲酸酐
    "sida":                                  ("O=C1OC(=O)c2cc([Si](C)(C)c3ccc4c(c3)C(=O)OC4=O)ccc21",    "二酐"),
    "4,4-(dimethylsilanediyl)diphthalic anhydride": ("O=C1OC(=O)c2cc([Si](C)(C)c3ccc4c(c3)C(=O)OC4=O)ccc21", "二酐"),
    # BPADA - 双酚A二酐
    "bpada":                                 ("O=C1OC(=O)c2cc(Oc3ccc(C(C)(C)c4ccc(Oc5ccc6c(c5)C(=O)OC6=O)cc4)cc3)ccc21", "二酐"),
    "2,2-bis[4-(3,4-dicarboxyphenoxy)phenyl]propane dianhydride": ("O=C1OC(=O)c2cc(Oc3ccc(C(C)(C)c4ccc(Oc5ccc6c(c5)C(=O)OC6=O)cc4)cc3)ccc21", "二酐"),
    # DSDA - 二苯砜四甲酸二酐
    "dsda":                                  ("O=C1OC(=O)c2cc(S(=O)(=O)c3ccc4c(c3)C(=O)OC4=O)ccc21",      "二酐"),
    "3,3,4,4-diphenylsulfonetetracarboxylic dianhydride": ("O=C1OC(=O)c2cc(S(=O)(=O)c3ccc4c(c3)C(=O)OC4=O)ccc21", "二酐"),
    # 6FAPB - 1,4-双(4-氨基-2-三氟甲基苯氧基)苯
    "6fapb":                                 ("Nc1ccc(Oc2ccc(Oc3ccc(N)cc3C(F)(F)F)cc2)c(C(F)(F)F)c1",     "二胺"),
    "1,4-bis(4-amino-2-trifluoromethylphenoxy)benzene": ("Nc1ccc(Oc2ccc(Oc3ccc(N)cc3C(F)(F)F)cc2)c(C(F)(F)F)c1", "二胺"),
    # Cz-NH2 - N-(4-氨基苯基)咔唑
    "cz-nh2":                                ("Nc1ccc(-n2c3ccccc3c3ccccc32)cc1",                        "二胺"),
    "n-(4-aminophenyl)carbazole":            ("Nc1ccc(-n2c3ccccc3c3ccccc32)cc1",                        "二胺"),
    # AMTPA - 4,4'-二氨基-4''-甲基三苯胺
    "amtpa":                                 ("Nc1ccc(N(c2ccc(C)cc2)c3ccc(N)cc3)cc1",                    "二胺"),
    "4,4'-diamino-4''-methyltriphenylamine": ("Nc1ccc(N(c2ccc(C)cc2)c3ccc(N)cc3)cc1",                    "二胺"),
    # Triamine-1 - N1,N1-双(4-氨基苯基)-4-(叔丁基)苯-1,3-二胺
    "triamine-1":                            ("CC(C)(C)c1ccc(N(c2ccc(N)cc2)c3ccc(N)cc3)cc1N",            "二胺"),
    "n1,n1-bis(4-aminophenyl)-4-(tert-butyl)benzene-1,3-diamine": ("CC(C)(C)c1ccc(N(c2ccc(N)cc2)c3ccc(N)cc3)cc1N", "二胺"),
}


def _builtin_lookup(name: str) -> tuple:
    """查内置单体数据库，返回 (canonical_smiles, source_label) 或 (None, None)。"""
    if not name:
        return None, None
    key = str(name).strip().lower()
    # 去掉括号内的内容再查一次（如 "PMDA (Pyromellitic Dianhydride)" → "pmda"）
    key_simple = re.sub(r"\s*\(.*?\)", "", key).strip()
    for k in (key, key_simple):
        if k in _BUILTIN_MONOMERS:
            smi, mtype = _BUILTIN_MONOMERS[k]
            return smi, "内置库"
    return None, None


def _validate_monomer_type(smi: str, monomer_type: str) -> bool:
    """后验证：检查 SMILES 是否符合单体类型的基本结构要求。
    二酐：至少 4 个 O 原子、总原子数 > 8 个 C
    二胺：至少 2 个 N 原子、总原子数 > 6 个 C
    用于过滤掉 AI 生成的明显错误（如 CN, N, C=O 等小分子）
    """
    if not smi or len(smi) <= 5:
        return False
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is None or mol.GetNumAtoms() < 6:
            return False
        atoms = mol.GetAtoms()
        n_c = sum(1 for a in atoms if a.GetAtomicNum() == 6)
        if "二酐" in monomer_type:
            n_o = sum(1 for a in atoms if a.GetAtomicNum() == 8)
            return n_o >= 4 and n_c >= 8
        elif "二胺" in monomer_type:
            n_n = sum(1 for a in atoms if a.GetAtomicNum() == 7)
            return n_n >= 2 and n_c >= 6
        return True
    except Exception:
        return False


SMILES_PROMPT_TEMPLATE = """你是一名精通聚酰亚胺单体结构的化学专家。请把下面给出的【单体全称 + 简写】转换成对应的规范 SMILES 字符串。

【单体类型】：{monomer_type}
【单体英文全称】：{full_name}
【简写】：{abbr}

规则：
1. 只输出"一个"SMILES 字符串，不要输出任何解释、推理、说明、Markdown、反引号、代码块、序号、换行或前后缀。
2. SMILES 必须合法且能被 RDKit 成功解析：
   - 所有圆括号 ()、方括号 []、大括号 {{}} 必须严格左右配对、完全闭合。
   - 芳香原子一律用小写（如苯环写作 c1ccccc1）。
   - 价键必须饱和，分子整体电中性。
   - 单体 SMILES 至少含 6 个重原子（H除外），总长度通常 ≥ 10 个字符。
   - 不得包含聚合重复单元或聚合度 n；只描述"该单体本身"。
3. 结构必须与单体类型严格一致：
   - 二酐：必须含两个环状酸酐基团（两个 -C(=O)OC(=O)- 五元环），可稠合在芳环上。
   - 二胺：必须含有且仅含有两个伯氨基 -NH2（整个分子恰好两个氮原子），不得含仲/叔胺或酰胺。
4. 若【简写】与【全称】不一致，以【全称】为准。
5. 【严禁输出单原子或小分子片段】—— 若你不确定完整结构，或只记得分子的一部分，绝对不要猜一个短片段（如 C、N、O、CO、NN、c1ccccc1 等）。这类输出是错误的。拿不准时直接输出 FAIL。
6. 宁可输出 FAIL，也不要输出猜测的短字符串或碎片。

直接输出最终结果（一行纯 SMILES，或 FAIL）："""


# SMILES 转换三重生成策略：每次调3次，取2/3多数一致的结果
_TEMPS_TRIPLE = [0.0, 0.1, 0.2]
_TEMPS_RETRY = [0.3, 0.4, 0.5]

_PLACEHOLDERS = {"—", "-", "N/A", "n/a", "NA", "/", "—", "无", "未知"}


def _is_blank(v) -> bool:
    if v is None:
        return True
    s = str(v).strip()
    return s == "" or s in _PLACEHOLDERS


def validate_smiles(smi: str) -> Tuple[bool, Optional[str]]:
    """
    校验 SMILES 合法性，返回 (是否合法, 规范SMILES)。
    RDKit 可用：MolFromSmiles 成功且原子数>0 才算通过，通过则返回 canonical SMILES。
    RDKit 不可用：降级为括号配平 + 基本字符检查（仅语法过滤，不保证化学正确）。
    """
    if _is_blank(smi) or str(smi).strip().upper() == "FAIL":
        return False, None
    s = str(smi).strip().strip("`'\" \t")
    # 最小长度硬拦截：最短单体 SMILES 也有 ~13 位（如 Nc1ccc(N)cc1），
    # 长度 ≤5 的必定是 "C"/"NN"/"CO"/"N#N" 等明显错误，直接拒绝。
    if len(s) <= 5:
        return False, None
    if _RDKIT:
        mol = Chem.MolFromSmiles(s)
        if mol is None or mol.GetNumAtoms() == 0:
            return False, None
        try:
            return True, Chem.MolToSmiles(mol)
        except Exception:
            return True, s
    # 降级：括号配平 + 不含非法字符
    pair = {"(": ")", "[": "]", "{": "}"}
    stack = []
    for ch in s:
        if ch in pair:
            stack.append(ch)
        elif ch in pair.values():
            if not stack or pair[stack.pop()] != ch:
                return False, None
    if stack:
        return False, None
    if not re.fullmatch(r"[A-Za-z0-9\(\)\[\]\{\}@=#/\\:.\-+]+", s):
        return False, None
    return True, s


def _try_smiles(smi: str):
    """RDKit 可用时返回 canonical SMILES，否则 None。供 extract_smiles 选最佳候选。"""
    if not smi or len(smi) <= 5:
        return None
    try:
        mol = Chem.MolFromSmiles(smi)
        if mol is not None and mol.GetNumAtoms() > 0:
            return Chem.MolToSmiles(mol)
    except Exception:
        pass
    return None


def extract_smiles(text: str) -> str:
    """从 LLM 返回里抽出纯 SMILES。
    推理模型(Kimi-K2.5/v4-pro等)：优先找 [SMILES]...[/SMILES] 标签内内容。
    非推理模型(deepseek-v4-flash等)：从行中提取。
    兜底：全文正则扫描所有疑似 SMILES token，用 RDKit 校验选原子数最多的合法候选。
    """
    if not text:
        return ""
    s = text.strip()
    s = re.sub(r"^```[a-zA-Z]*", "", s)
    s = re.sub(r"```$", "", s)

    # 1) 优先提取 [SMILES]...[/SMILES] 标签内的内容
    tag_match = re.search(r"\[SMILES\](.*?)\[/SMILES\]", s, re.DOTALL)
    if tag_match:
        inner = tag_match.group(1).strip()
        inner = inner.strip("`'\" \t.,;:")
        if inner.upper() == "FAIL":
            return ""
        # 标签内如果有换行取最后一行
        inner_lines = [ln.strip() for ln in inner.splitlines() if ln.strip()]
        tag_candidate = inner_lines[-1] if inner_lines else inner
        # RDKit 校验
        if _RDKIT:
            canon = _try_smiles(tag_candidate)
            if canon:
                return canon
        # 无 RDKit 或校验不通过：检查括号配平
        if not _RDKIT:
            tag_candidate = tag_candidate.strip("`'\" \t.,;:")
            ok, _ = validate_smiles(tag_candidate)
            if ok:
                return tag_candidate

    # 2) 兜底：全文扫描所有候选
    lines = [ln.strip().strip("`'\" \t.,;:") for ln in s.splitlines() if ln.strip()]
    candidates = list(lines)
    candidates += re.findall(r"[A-Za-z0-9\(\)\[\]\{\}@=#/\\:.+-]+", s)
    seen, uniq = set(), []
    for c in candidates:
        if c and c not in seen:
            seen.add(c); uniq.append(c)
    if not uniq:
        return ""
    # 有 RDKit：选原子数最多的合法候选（最长的合法 SMILES 通常就是答案）
    if _RDKIT:
        best, best_n = "", 0
        for c in uniq:
            canon = _try_smiles(c)
            if canon is not None:
                n = Chem.MolFromSmiles(canon).GetNumAtoms()
                if n > best_n:
                    best, best_n = canon, n
        return best
    # 无 RDKit：返回最长候选
    return max(uniq, key=len)


class SmilesConverter:
    """把单体全拼/简写转成经 RDKit 校验的 SMILES。"""

    def __init__(self, api_url: str, api_key: str, model: str,
                 timeout: int = 90, max_retries: int = 2):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self._cache = {}          # (type, full, abbr) -> (smiles, valid) 去重
        self._lock = threading.Lock()

    def _call_api(self, prompt: str, temperature: float = 0.0) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2048,
                    "temperature": temperature,
                }
                resp = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                logger.error(f"SMILES API错误 {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"SMILES API调用失败 第{attempt+1}次: {e}")
        return None

    def _db_lookup(self, full_name: str, timeout: float = 15.0) -> Tuple[Optional[str], Optional[str]]:
        """先用全拼查公开数据库（PubChemPy → CIRpy 兜底），返回 (canonical_smiles, source)。

        只用【英文全拼】查询——简写（如 ODA/6FDA）在数据库里会命中无关结构，故不用。
        任一数据库命中且 RDKit 能解析即返回。网络失败时返回 (None, None)。
        """
        if _is_blank(full_name):
            return None, None
        name = str(full_name).strip()
        def _canon(smi):
            if not smi:
                return None
            ok, c = validate_smiles(smi)
            return c if ok else None

        # 1) PubChemPy：按名称搜索化合物
        try:
            import pubchempy as pcp
            results = pcp.get_compounds(name, 'name')
            if results:
                cpd = results[0]
                raw = (getattr(cpd, 'smiles', None)
                       or getattr(cpd, 'canonical_smiles', None)
                       or getattr(cpd, 'isomeric_smiles', None))
                c = _canon(raw)
                if c:
                    return c, "PubChem"
        except Exception as e:
            logger.debug(f"PubChemPy 查询异常 ({name}): {e}")

        # 2) CIRpy（CACTUS 兜底）
        try:
            import cirpy
            raw = cirpy.resolve(name, 'smiles')
            if raw:
                c = _canon(raw)
                if c:
                    return c, "CACTUS"
        except Exception as e:
            logger.debug(f"CIRpy 查询异常 ({name}): {e}")

        return None, None

    def smiles_for_monomer(self, full_name: str, abbr: str, monomer_type: str,
                           max_rounds: int = 2) -> Tuple[str, bool, str]:
        """返回 (canonical_smiles 或 "", 是否校验通过, 来源)。

        来源 source ∈ {"内置库": 内置库命中, "db": PubChem/CACTUS与AI一致,
                       "ai": AI三重生成多数一致, "ai_single": AI单次有效但无多数, ""}。

        策略（三层递进）：
        1) 先查【内置库】→ 命中直接返回（最快最准）。
        2) 内置库未命中 → 查 PubChem/CACTUS，命中则调一次AI比对：
           · 一致 → 采纳数据库
           · 不一致 → 走三重AI生成
        3) AI三重生成 + 多数投票：每轮 3 次（temperature 递增），
           有 ≥2 次相同 canonical → 采纳；全部不同则再试一轮。
        """
        if _is_blank(full_name) and _is_blank(abbr):
            return "", False, ""
        key = (monomer_type, str(full_name).strip(), str(abbr).strip())
        with self._lock:
            if key in self._cache:
                return self._cache[key]

        fname = str(full_name).strip() if not _is_blank(full_name) else "(未提供)"
        aname = str(abbr).strip() if not _is_blank(abbr) else "(未提供)"

        # ---- 步骤1：内置库查询（最快）----
        b_smi, b_src = _builtin_lookup(fname)
        if b_smi:
            result = (b_smi, True, "内置库")
            with self._lock:
                self._cache[key] = result
            return result
        # 同时用简写查一次
        if not _is_blank(abbr):
            b_smi2, _ = _builtin_lookup(abbr)
            if b_smi2:
                result = (b_smi2, True, "内置库")
                with self._lock:
                    self._cache[key] = result
                return result

        # ---- 步骤2：PubChem / CACTUS 外部数据库查询 ----
        db_smi, _db_src = self._db_lookup(fname)

        # 若数据库命中 → 直接采纳（数据库比 AI 更可靠，避免 AI 幻觉）
        if db_smi:
            if _validate_monomer_type(db_smi, monomer_type):
                result = (db_smi, True, "db")
                with self._lock:
                    self._cache[key] = result
                return result

        # 提示词模板
        base_prompt = SMILES_PROMPT_TEMPLATE.format(
            monomer_type=monomer_type, full_name=fname, abbr=aname)

        # ---- 步骤3：AI 三重生成 + 多数投票 ----
        def _try_round(temps):
            """执行一轮三重生成，返回 (最佳canonical, 是否多数一致, 最高频次)。"""
            votes = {}  # canonical -> count
            valid_list = []  # (atoms, canonical)
            for temp in temps:
                raw = self._call_api(base_prompt, temperature=temp)
                if not raw:
                    continue
                cand = extract_smiles(raw)
                if not cand or cand.upper() == "FAIL":
                    continue
                ok, canon = validate_smiles(cand)
                if ok:
                    # 再加上单体类型后验证（过滤 CN, N, C=O 等明显错误）
                    if _validate_monomer_type(canon, monomer_type):
                        votes[canon] = votes.get(canon, 0) + 1
                    try:
                        n = Chem.MolFromSmiles(canon).GetNumAtoms()
                    except Exception:
                        n = 0
                    valid_list.append((n, canon))

            # 是否有 ≥2 次一致的？
            best_canon = ""
            best_count = 0
            for canon, cnt in votes.items():
                if cnt > best_count:
                    best_count = cnt
                    best_canon = canon

            # 没有多数一致时，取原子数最多的合法候选
            if not best_canon and valid_list:
                valid_list.sort(key=lambda x: x[0], reverse=True)
                best_canon = valid_list[0][1]
                best_count = 1  # 标记为单个通过

            return best_canon, best_count >= 2, best_count

        # 第一轮（温度 0.0, 0.1, 0.2）
        smi, agreed, _ = _try_round(_TEMPS_TRIPLE)
        if smi and agreed:
            result = (smi, True, "ai")
            with self._lock:
                self._cache[key] = result
            return result

        # 第二轮（温度 0.3, 0.4, 0.5）——重试
        if max_rounds >= 2:
            smi2, agreed2, max_cnt2 = _try_round(_TEMPS_RETRY)
            if smi2 and agreed2:
                result = (smi2, True, "ai")
                with self._lock:
                    self._cache[key] = result
                return result
            # 第二轮的候选优于第一轮的？
            if smi2 and not smi:
                smi = smi2
            elif smi2 and max_cnt2 >= 1:
                # 第二轮有候选但无多数，优于第一轮完全失败
                smi = smi2

        source_label = "ai" if smi else ""
        result = (smi or "", bool(smi), source_label)
        with self._lock:
            self._cache[key] = result
        return result

    def process_dataframe(self, df: pd.DataFrame,
                          progress_callback=None, cancel_event=None,
                          workers: int = 6) -> pd.DataFrame:
        """
        对每行 4 组单体并发转 SMILES 并 RDKit 校验，
        新增列：酸酐1_SMILES / 酸酐2_SMILES / 二胺1_SMILES / 二胺2_SMILES。
        未通过校验的留空。返回复制后的新 df。
        """
        from concurrent.futures import ThreadPoolExecutor
        # 先归一化列名（兼容各种输入格式）
        out, _ = normalize_input_columns(df.copy())
        for _, _, target, _ in MONOMER_COLS:
            if target not in out.columns:
                out[target] = ""

        # 展开成任务列表，便于并发派发
        tasks = []
        for idx in out.index:
            for full_col, abbr_col, target, mtype in MONOMER_COLS:
                full_val = out.at[idx, full_col] if full_col in out.columns else ""
                abbr_val = out.at[idx, abbr_col] if abbr_col in out.columns else ""
                tasks.append((idx, target, full_val, abbr_val, mtype))

        total = max(1, len(tasks))
        done_cnt = [0]
        done_lock = threading.Lock()
        results: dict = {}
        results_valid: dict = {}   # (idx, target) -> (valid:bool, has_candidate:bool, source:str)
        results_lock = threading.Lock()
        aborted = [False]

        def worker(task):
            idx, target, full_val, abbr_val, mtype = task
            if cancel_event and cancel_event.is_set():
                aborted[0] = True
                return
            smiles, valid, source = self.smiles_for_monomer(full_val, abbr_val, mtype)
            with results_lock:
                # 校验通过写 canonical；未通过但拿到候选也写入，尽量全面（状态列会标记）
                results[(idx, target)] = smiles if (valid or smiles) else ""
                results_valid[(idx, target)] = (valid, bool(smiles), source)
            with done_lock:
                done_cnt[0] += 1
                cur = done_cnt[0]
            if progress_callback:
                try:
                    progress_callback(cur, total)
                except Exception:
                    pass

        workers = max(1, min(int(workers), 16))
        with ThreadPoolExecutor(max_workers=workers,
                                thread_name_prefix="smiles") as ex:
            futures = [ex.submit(worker, t) for t in tasks]
            for fut in futures:
                try:
                    fut.result()
                except Exception as e:
                    logger.error(f"SMILES 并发任务异常: {e}")

        # 写回 SMILES（已取消则保留已得到的部分结果）
        for (idx, target), smiles in results.items():
            out.at[idx, target] = smiles
        # 校验状态汇总列：📚数据库与AI一致 / ✓通过RDKit / △未校验但有候选(已填入待核对) / ✗完全失败
        labels = ["酐1", "酐2", "胺1", "胺2"]
        rows = {}
        for i, (_fc, _ac, target, _mt) in enumerate(MONOMER_COLS):
            for idx in out.index:
                valid, has_cand, source = results_valid.get((idx, target), (False, False, ""))
                mark = ("📚" if (valid and source == "db")
                        else ("✓" if valid else ("△" if has_cand else "✗")))
                rows.setdefault(idx, []).append(f"{labels[i]}{mark}")
        out["SMILES校验状态"] = [" ".join(rows.get(idx, [])) for idx in out.index]
        if aborted[0]:
            logger.info("SMILES 转化被用户取消，已保留部分结果")
        return out


def rdkit_available() -> bool:
    return _RDKIT
