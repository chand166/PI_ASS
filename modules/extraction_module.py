#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取模块
从PDF文献中提取聚酰亚胺结构与性能数据，输出24列标准表格
"""

import os
import re
import time
import json
import requests
from typing import List, Dict, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    """数据提取器"""

    # 24列标准输出
    OUTPUT_COLUMNS = [
        "样品编号", "命名",
        "单体酸酐1英文全拼", "酸酐简写",
        "单体酸酐2英文全拼", "酸酐2简写",
        "单体二胺1英文全拼", "二胺简写",
        "单体二胺2英文全拼", "二胺2简写",
        "热分解温度 (Td5%, °C)", "玻璃化转变温度 (Tg, °C)",
        "热膨胀系数 (CTE, ppm·K⁻¹)", "截止波长 (λcutoff, nm)",
        "透光率 (T450nm, %)", "Tensile Strength",
        "Elongation at Break(%)", "a*", "b*", "L*",
        "Dielectric Constant", "dielectric loss", "YI",
        "来源文件"
    ]

    def __init__(self, api_url: str, api_key: str, model: str = "Kimi-K2.5",
                 extraction_prompt: str = None, max_workers: int = 3):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.extraction_prompt = extraction_prompt or self._default_prompt()
        self.max_workers = max_workers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _default_prompt(self) -> str:
        return """以一个材料领域的专家身份，用严谨的态度来分析文献中的文字图片和表格，重点分析表格与图片，提取数据，将文件中所有的结构以及对应性能列举出来"""

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """从PDF提取文本"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text_parts = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF提取文本失败 {pdf_path}: {e}")
            return ""

    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """从单个PDF提取数据"""
        try:
            pdf_text = self.extract_text_from_pdf(pdf_path)
            pdf_name = Path(pdf_path).name

            if not pdf_text.strip():
                return {col: "—" for col in self.OUTPUT_COLUMNS} | {"来源文件": pdf_name}

            # 截断文本避免超长
            if len(pdf_text) > 8000:
                pdf_text = pdf_text[:8000] + "\n\n[文本已截断]"

            prompt = f"""{self.extraction_prompt}

{pdf_text}

请严格按照以下24列格式输出表格，只输出表格内容不要思考过程：
| 样品编号 | 命名 | 单体酸酐1英文全拼 | 酸酐简写 | 单体酸酐2英文全拼 | 酸酐2简写 | 单体二胺1英文全拼 | 二胺简写 | 单体二胺2英文全拼 | 二胺2简写 | 热分解温度 (Td5%, °C) | 玻璃化转变温度 (Tg, °C) | 热膨胀系数 (CTE, ppm·K⁻¹) | 截止波长 (λcutoff, nm) | 透光率 (T450nm, %) | Tensile Strength | Elongation at Break(%) | a* | b* | L* | Dielectric Constant | dielectric loss | YI | 来源文件 |

要求：
1. 将文件中所有的结构及对应性能全部列出，每个样品一行
2. 无数据用短划线 —
3. 全拼和简写单元格不允许出现中文
4. 缩写可在文中找到对应全拼
5. 来源文件列填入: {pdf_name}
6. 严格按24列输出"""

            response_text = self._call_api(prompt)
            if response_text:
                return self._parse_table(response_text, pdf_name)
            else:
                return {col: "—" for col in self.OUTPUT_COLUMNS} | {"来源文件": pdf_name}

        except Exception as e:
            logger.error(f"提取失败 {pdf_path}: {e}")
            return {col: "—" for col in self.OUTPUT_COLUMNS} | {"来源文件": pdf_name}

    def _call_api(self, prompt: str) -> Optional[str]:
        """调用API"""
        for attempt in range(3):
            try:
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4096,
                    "temperature": 0.1
                }
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=180
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content']
                else:
                    logger.error(f"API错误 {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.error(f"API调用失败 第{attempt+1}次: {e}")
                time.sleep(3)
        return None

    def _parse_table(self, text: str, pdf_name: str) -> Dict:
        """
        解析LLM返回的表格文本为DataFrame行
        支持markdown表格、CSV、纯文本表格
        """
        rows_data = []
        lines = text.strip().split("\n")

        # 尝试找markdown表格行（包含 | 分隔符的行）
        table_lines = [l for l in lines if "|" in l and not l.strip().startswith("|--")]

        if table_lines:
            # 去掉表头行（包含"样品编号"的行）
            data_lines = [l for l in table_lines if "样品编号" not in l and not l.startswith("|--")]
            for line in data_lines:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                row = {}
                for i, col in enumerate(self.OUTPUT_COLUMNS):
                    if i < len(cells):
                        row[col] = cells[i]
                    else:
                        row[col] = "—"
                # 确保来源文件
                row["来源文件"] = pdf_name
                rows_data.append(row)

        # 如果没有解析到任何行，尝试用正则匹配数据行
        if not rows_data:
            row = {col: "—" for col in self.OUTPUT_COLUMNS}
            row["来源文件"] = pdf_name
            # 取前500字符作为原始文本参考
            row["命名"] = text[:200].replace("\n", " ").strip()[:100]
            rows_data.append(row)
            return row

        # 返回第一行（批量提取时每个PDF返回一行）
        return rows_data[0]

    def extract_from_folder(self, folder_path: str, output_file: str,
                          progress_callback=None,
                          cancel_event=None) -> pd.DataFrame:
        """从文件夹批量提取"""
        folder = Path(folder_path)
        pdf_files = sorted(folder.glob("*.pdf"))
        results = []
        total = len(pdf_files)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {executor.submit(self.extract_from_pdf, str(p)): p for p in pdf_files}
            pending = set(future_to_pdf)
            completed = 0
            while pending:
                # 主动轮询取消：每 0.2s 检查一次，不被 as_completed 阻塞。
                # 否则点取消后要等下一个 PDF 处理完（最坏 180s API 超时）才会响应。
                if cancel_event and cancel_event.is_set():
                    for f in pending:
                        f.cancel()
                    break
                done_now = [f for f in pending if f.done()]
                if not done_now:
                    time.sleep(0.2)
                    continue
                for future in done_now:
                    pending.discard(future)
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"提取完成: {future_to_pdf[future].name}")
                    except Exception as e:
                        logger.error(f"提取失败: {e}")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total)

        df = pd.DataFrame(results)
        # 确保24列完整
        for col in self.OUTPUT_COLUMNS:
            if col not in df.columns:
                df[col] = "—"
        df = df[self.OUTPUT_COLUMNS]

        df.to_excel(output_file, index=False)
        logger.info(f"结果已保存到: {output_file}")
        return df


# ==================== 提取结果清洗 ====================
# 占位符统一视为“无数据”：转成 NaN 便于后续 notna/删除
_BLANK_TOKENS = {"", "-", "—", "–", "—", "/", "\\", "n/a", "na", "N/A", "NA",
                 "nan", "NaN", "None", "null", "无", "未知", "未提供", "未列出",
                 "---", "—", "—"}

# 4 组单体：判断“酸酐/二胺都没有”时同时看全拼与简写
_MONOMER_GROUPS = [
    ("单体酸酐1英文全拼", "酸酐简写"),
    ("单体酸酐2英文全拼", "酸酐2简写"),
    ("单体二胺1英文全拼", "二胺简写"),
    ("单体二胺2英文全拼", "二胺2简写"),
]

# 性能列（判断“性能全都没有”）
_PERF_COLS = [
    "热分解温度 (Td5%, °C)", "玻璃化转变温度 (Tg, °C)",
    "热膨胀系数 (CTE, ppm·K⁻¹)", "截止波长 (λcutoff, nm)",
    "透光率 (T450nm, %)", "Tensile Strength",
    "Elongation at Break(%)", "a*", "b*", "L*",
    "Dielectric Constant", "dielectric loss", "YI",
]

# 性能列中文 → DATA-smi 英文标准名（供 SMILES/描述符页对接时规整列名）
PERF_COL_MAP = {
    "热分解温度 (Td5%, °C)": "Td5%, °C",
    "玻璃化转变温度 (Tg, °C)": "Tg, °C",
    "热膨胀系数 (CTE, ppm·K⁻¹)": "CTE, ppm/K",
    "截止波长 (λcutoff, nm)": "λcutoff, nm",
    "透光率 (T450nm, %)": "T450nm, %",
    "Tensile Strength": "Tensile Strength",
    "Elongation at Break(%)": "Elongation at Break(%)",
    "a*": "a*", "b*": "b*", "L*": "L*",
    "Dielectric Constant": "Dielectric Constant",
    "dielectric loss": "dielectric loss", "YI": "YI",
}


def _is_blank_val(v) -> bool:
    if v is None:
        return True
    try:
        if pd.isna(v):
            return True
    except (TypeError, ValueError):
        pass
    return str(v).strip() in _BLANK_TOKENS


def clean_extraction_table(df, drop_duplicates=True, renumber=True):
    """对提取结果做自动清洗，返回 (cleaned_df, stats)。

    清洗步骤（与 DATA-smi.xlsx 目标格式对齐）：
      1. 占位符(—/-/无/未知/N/A/nan 等)归一为 NaN；
      2. 删除“酸酐和二胺都没有”的行（4 组单体全拼+简写全空）；
      3. 删除“性能全都没有”的行（13 个性能列全空）；
      4. 可选删除完全重复行（保留首次出现）；
      5. 可选重置样品编号为 1..N 连续。

    stats: dict，记录每步删/改了多少行，供 UI 展示。
    """
    if df is None or len(df) == 0:
        return df, {"input": 0, "output": 0, "steps": []}

    stats = {"input": int(len(df)), "output": 0, "steps": []}
    out = df.copy()

    # 1) 占位符归一为 NaN（只对 object/字符串列处理，避免误伤数值）
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].where(~out[col].apply(_is_blank_val))

    # 2) 删除“酸酐和二胺都没有”的行
    mon_cols = [c for grp in _MONOMER_GROUPS for c in grp if c in out.columns]
    if mon_cols:
        all_blank = out[mon_cols].map(_is_blank_val).all(axis=1)
        n_drop_monomer = int(all_blank.sum())
        if n_drop_monomer > 0:
            out = out[~all_blank].reset_index(drop=True)
            stats["steps"].append({"rule": "删除酸酐和二胺都没有的行", "removed": n_drop_monomer})

    # 3) 删除“性能全都没有”的行
    perf_cols = [c for c in _PERF_COLS if c in out.columns]
    if perf_cols:
        perf_blank = out[perf_cols].map(_is_blank_val).all(axis=1)
        n_drop_perf = int(perf_blank.sum())
        if n_drop_perf > 0:
            out = out[~perf_blank].reset_index(drop=True)
            stats["steps"].append({"rule": "删除性能全都没有的行", "removed": n_drop_perf})

    # 4) 删除完全重复行
    if drop_duplicates:
        before = len(out)
        out = out.drop_duplicates().reset_index(drop=True)
        n_dup = before - len(out)
        if n_dup > 0:
            stats["steps"].append({"rule": "删除完全重复行", "removed": n_dup})

    # 5) 重置样品编号
    if renumber and "样品编号" in out.columns:
        out["样品编号"] = range(1, len(out) + 1)

    stats["output"] = int(len(out))
    return out, stats


if __name__ == "__main__":
    e = DataExtractor(api_url="http://10.2.39.6:20004/v1", api_key="your-api-key")
    print("数据提取模块加载成功")