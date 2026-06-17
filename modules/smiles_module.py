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


SMILES_PROMPT_TEMPLATE = """你是一名精通聚酰亚胺单体结构的化学专家。请把下面给出的【单体全称 + 简写】转换成对应的规范 SMILES 字符串。

【单体类型】：{monomer_type}
【单体英文全称】：{full_name}
【简写】：{abbr}

请严格遵守以下规则，任何一条都不得违反：
1. 只输出"一个"SMILES 字符串，不要输出任何解释、说明、Markdown、反引号、代码块、序号、换行或前后缀。
2. SMILES 必须合法且能被 RDKit 成功解析：
   - 所有圆括号 ()、方括号 []、大括号 {{}} 必须严格左右配对、完全闭合，不得出现未闭合或多出、遗漏的括号。
   - 芳香原子一律用小写（如苯环写作 c1ccccc1），脂肪原子用大写（如 C、N、O）。
   - 价键必须饱和，分子整体电中性；不得出现断裂的键、孤立原子、游离的取代基或悬空的占位符。
   - 不得包含聚合重复单元的方括号或聚合度 n；只描述"该单体本身"的一个分子，不要写聚合物链。
3. 结构必须与单体类型严格一致：
   - 二酐：必须含两个环状酸酐基团（两个 -C(=O)OC(=O)- 五元环），可稠合在芳环上（如均苯四甲酸二酐 PMDA、联苯二酐 BPDA、含氟二酐 6FDA）。
   - 二胺：必须含有且仅含有两个伯氨基 -NH2（整个分子恰好两个氮原子），不得含仲/叔胺或酰胺。
4. 若【简写】与【全称】不一致，以【全称】为准来确定结构。
5. 若信息不足以唯一确定结构、该简写对应的单体不存在、或存在歧义无法确定时，请仅输出四个大写字母：FAIL（此时禁止输出任何 SMILES）。

直接输出最终结果（一行纯 SMILES，或 FAIL）："""


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


def extract_smiles(text: str) -> str:
    """从 LLM 返回里抽出纯 SMILES（去 markdown/代码块/空白/首尾引号）。"""
    if not text:
        return ""
    s = text.strip()
    s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
    s = re.sub(r"\n?```$", "", s)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if lines:
        s = lines[0]
    return s.strip("`'\" \t")


class SmilesConverter:
    """把单体全拼/简写转成经 RDKit 校验的 SMILES。"""

    def __init__(self, api_url: str, api_key: str, model: str,
                 timeout: int = 180, max_retries: int = 3):
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

    def _call_api(self, prompt: str) -> Optional[str]:
        for attempt in range(self.max_retries):
            try:
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                    "temperature": 0.0,
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

    def smiles_for_monomer(self, full_name: str, abbr: str, monomer_type: str
                           ) -> Tuple[str, bool]:
        """返回 (canonical_smiles 或 "", 是否校验通过)。空单体直接返回空。"""
        if _is_blank(full_name) and _is_blank(abbr):
            return "", False
        key = (monomer_type, str(full_name).strip(), str(abbr).strip())
        with self._lock:
            if key in self._cache:
                return self._cache[key]
        prompt = SMILES_PROMPT_TEMPLATE.format(
            monomer_type=monomer_type,
            full_name=str(full_name).strip() if not _is_blank(full_name) else "(未提供)",
            abbr=str(abbr).strip() if not _is_blank(abbr) else "(未提供)",
        )
        raw = self._call_api(prompt)
        smiles, valid = "", False
        if raw:
            cand = extract_smiles(raw)
            if cand and cand.upper() != "FAIL":
                ok, canon = validate_smiles(cand)
                smiles = canon if ok else cand  # 记录原值但 valid=False
                valid = ok
        with self._lock:
            self._cache[key] = (smiles, valid)
        return smiles, valid

    def process_dataframe(self, df: pd.DataFrame,
                          progress_callback=None, cancel_event=None) -> pd.DataFrame:
        """
        对每行 4 组单体逐个转 SMILES 并 RDKit 校验，
        新增列：酸酐1_SMILES / 酸酐2_SMILES / 二胺1_SMILES / 二胺2_SMILES。
        未通过校验的留空。返回复制后的新 df。
        """
        out = df.copy()
        for _, _, target, _ in MONOMER_COLS:
            if target not in out.columns:
                out[target] = ""
        total = max(1, len(out) * len(MONOMER_COLS))
        done = 0
        for idx in out.index:
            if cancel_event and cancel_event.is_set():
                break
            for full_col, abbr_col, target, mtype in MONOMER_COLS:
                if cancel_event and cancel_event.is_set():
                    break
                full_val = out.at[idx, full_col] if full_col in out.columns else ""
                abbr_val = out.at[idx, abbr_col] if abbr_col in out.columns else ""
                smiles, valid = self.smiles_for_monomer(full_val, abbr_val, mtype)
                out.at[idx, target] = smiles if valid else ""
                done += 1
                if progress_callback:
                    progress_callback(done, total)
        return out


def rdkit_available() -> bool:
    return _RDKIT
