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
            futures = {executor.submit(self.extract_from_pdf, str(p)): p for p in pdf_files}
            for idx, future in enumerate(as_completed(futures)):
                if cancel_event and cancel_event.is_set():
                    for f in futures:
                        f.cancel()
                    break
                result = future.result()
                results.append(result)
                pdf = futures[future]
                logger.info(f"提取完成: {pdf.name}")
                if progress_callback:
                    progress_callback(idx + 1, total)
                time.sleep(0.5)

        df = pd.DataFrame(results)
        # 确保24列完整
        for col in self.OUTPUT_COLUMNS:
            if col not in df.columns:
                df[col] = "—"
        df = df[self.OUTPUT_COLUMNS]

        df.to_excel(output_file, index=False)
        logger.info(f"结果已保存到: {output_file}")
        return df


if __name__ == "__main__":
    e = DataExtractor(api_url="http://10.2.39.6:20004/v1", api_key="your-api-key")
    print("数据提取模块加载成功")