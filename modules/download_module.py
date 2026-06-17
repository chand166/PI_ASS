#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献下载模块
根据DOI批量下载学术文献PDF（支持评分结果筛选 + 可配置下载源）
"""

import os
import re
import time
import requests
from typing import List, Dict, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import bs4

logger = logging.getLogger(__name__)


class LiteratureDownloader:
    """文献下载器"""

    def __init__(self, output_dir: str, max_workers: int = 3,
                 timeout: int = 30, scihub_url: str = "https://sci-hub.ru"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.timeout = timeout

        self.scihub_urls = [
            scihub_url,
            "https://sci-hub.se",
            "https://sci-hub.st",
            "https://sci-hub.nu",
        ]

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def parse_doi_file(self, file_path: str) -> List[str]:
        dois = []
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    doi = line.strip()
                    if doi and not doi.startswith('#'):
                        dois.append(doi)
        elif file_path.endswith(('.csv', '.xlsx', '.xls')):
            import pandas as pd
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            doi_col = None
            for col in df.columns:
                if 'doi' in col.lower():
                    doi_col = col
                    break
            if doi_col:
                dois = df[doi_col].dropna().astype(str).tolist()
        return list(set(dois))

    def get_dois_from_scored(self, scored_df, title_col="title",
                              doi_col="doi", threshold=0.7) -> List[Dict]:
        results = []
        for _, row in scored_df.iterrows():
            score = row.get('avg_score', 0)
            if score >= threshold:
                doi = row.get(doi_col, "")
                title = row.get(title_col, "")
                if doi and str(doi).strip():
                    results.append({
                        "title": str(title).strip(),
                        "doi": self.clean_doi(str(doi)),
                        "score": score,
                    })
        return results

    def clean_doi(self, doi: str) -> str:
        doi = doi.strip()
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi)
        doi = re.sub(r'^doi:', '', doi)
        return doi.strip()

    def download_single(self, doi: str, retry: int = 2) -> Dict:
        doi = self.clean_doi(doi)
        errors = []

        for attempt in range(retry):
            for base_url in self.scihub_urls:
                try:
                    download_url = f"{base_url}/{doi}"
                    resp = requests.get(
                        download_url, headers=self.headers,
                        timeout=self.timeout, allow_redirects=True
                    )

                    if resp.status_code != 200:
                        errors.append(f"{base_url} 返回 {resp.status_code}")
                        continue

                    content_type = resp.headers.get('Content-Type', '')

                    # 情况1：直接返回PDF
                    if 'pdf' in content_type.lower() or resp.headers.get('Content-Disposition'):
                        return self._save_pdf(resp.content, doi)

                    # 情况2：BeautifulSoup解析HTML提取PDF链接
                    pdf_url = self._extract_pdf_url_bs4(resp.content, base_url)

                    if not pdf_url:
                        errors.append(f"{base_url} 页面未找到PDF链接")
                        continue

                    pdf_headers = {**self.headers, "Referer": download_url}
                    pdf_resp = requests.get(
                        pdf_url, headers=pdf_headers,
                        timeout=self.timeout, allow_redirects=True
                    )

                    if pdf_resp.status_code == 200:
                        return self._save_pdf(pdf_resp.content, doi)
                    else:
                        errors.append(f"PDF链接 {pdf_url[:80]} 返回 {pdf_resp.status_code}")

                except requests.exceptions.ConnectTimeout:
                    errors.append(f"{base_url} 连接超时")
                except requests.exceptions.ConnectionError:
                    errors.append(f"{base_url} 连接被拒绝（可能被墙）")
                except requests.exceptions.ReadTimeout:
                    errors.append(f"{base_url} 读取超时")
                except Exception as e:
                    errors.append(f"{base_url}: {e}")

            if attempt < retry - 1:
                time.sleep(2)

        return {
            'doi': doi,
            'status': 'failed',
            'filepath': None,
            'error': '; '.join(errors) if errors else '所有镜像均失败'
        }

    def _save_pdf(self, content: bytes, doi: str) -> Dict:
        filename = self._sanitize_filename(doi)
        filepath = self.output_dir / f"{filename}.pdf"
        with open(filepath, 'wb') as f:
            f.write(content)
        return {'doi': doi, 'status': 'success', 'filepath': str(filepath), 'error': None}

    def _extract_pdf_url_bs4(self, html_content: bytes, base_url: str) -> Optional[str]:
        """
        使用BeautifulSoup从Sci-Hub页面提取PDF链接
        优先级：object > iframe > embed > a.pdf > button onclick
        """
        soup = bs4.BeautifulSoup(html_content, 'html.parser')
        pdf_url = None

        # 1) <object type="application/pdf" data="...">
        obj = soup.find('object', type='application/pdf')
        if obj and 'data' in obj.attrs:
            pdf_url = obj['data'].split('#')[0]

        # 2) <iframe src="...">
        if not pdf_url:
            iframe = soup.find('iframe')
            if iframe and 'src' in iframe.attrs:
                pdf_url = iframe['src']

        # 3) <embed type="application/pdf" src="...">
        if not pdf_url:
            embed = soup.find('embed', type='application/pdf')
            if embed and 'src' in embed.attrs:
                pdf_url = embed['src']

        # 4) <a href="...pdf"> / 包含 storage/downloads 的链接
        if not pdf_url:
            for a in soup.find_all('a', href=True):
                h = a['href'].lower()
                if h.endswith('.pdf') or '/storage/' in h or '/downloads/' in h:
                    pdf_url = a['href']
                    break

        # 5) button onclick="location.href='...'"
        if not pdf_url:
            btn = soup.find('button', onclick=True)
            if btn:
                m = re.search(r"location\.href='(.*?)'", btn['onclick'])
                if m:
                    pdf_url = m.group(1)

        # 处理相对路径
        if pdf_url:
            pdf_url = pdf_url.strip()
            if pdf_url.startswith('//'):
                pdf_url = 'https:' + pdf_url
            elif not pdf_url.startswith('http'):
                base = base_url.rstrip('/')
                pdf_url = base + ('/' if not pdf_url.startswith('/') else '') + pdf_url

        return pdf_url

    def _sanitize_filename(self, doi: str) -> str:
        doi = doi.replace('/', '_').replace(':', '_')
        doi = re.sub(r'[<>:"/\\|?*]', '', doi)
        return doi[:100]

    def _max_existing_index(self) -> int:
        """扫描下载目录中已有的 N.pdf，返回最大数字（无则0）。"""
        max_n = 0
        try:
            for p in self.output_dir.glob("[0-9]*.pdf"):
                if p.stem.isdigit():
                    max_n = max(max_n, int(p.stem))
        except Exception:
            pass
        return max_n

    def download_batch(self, dois: List[str],
                      progress_callback=None,
                      cancel_event=None) -> Dict:
        results = []
        success_count = 0
        failed_count = 0
        failed_dois = []
        total = len(dois)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_single, doi): doi for doi in dois}
            for idx, future in enumerate(as_completed(futures)):
                if cancel_event and cancel_event.is_set():
                    for f in futures:
                        f.cancel()
                    break
                result = future.result()
                results.append(result)
                if result['status'] == 'success':
                    success_count += 1
                    logger.info(f"下载成功: {result['doi']}")
                else:
                    failed_count += 1
                    failed_dois.append(result['doi'])
                    logger.error(f"下载失败: {result['doi']} - {result['error']}")
                if progress_callback:
                    progress_callback(idx + 1, total)
                time.sleep(0.5)

        if failed_dois:
            failed_file = self.output_dir / "failed_dois.txt"
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(failed_dois))

        # 下载完成后，按 dois 列表顺序把成功文件重命名为 数字.pdf（续号，失败不占号）
        base = self._max_existing_index()
        seq = base + 1
        success_by_doi = {r['doi']: r for r in results if r['status'] == 'success'}
        mapping_lines = []
        for doi in dois:
            r = success_by_doi.get(doi)
            if not r or not r.get('filepath'):
                continue
            old_path = Path(r['filepath'])
            if not old_path.exists():
                continue
            new_path = self.output_dir / f"{seq}.pdf"
            try:
                old_path.rename(new_path)
                r['filepath'] = str(new_path)
                mapping_lines.append(f"{seq}.pdf\t{doi}")
                seq += 1
            except Exception as e:
                logger.error(f"重命名失败 {doi}: {e}")

        if mapping_lines:
            map_file = self.output_dir / "download_index.txt"
            with open(map_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(mapping_lines))

        return {'total': total, 'success': success_count, 'failed': failed_count,
                'failed_dois': failed_dois, 'results': results}


if __name__ == "__main__":
    dl = LiteratureDownloader(output_dir="D:/PI_Project/paper", max_workers=3, scihub_url="https://sci-hub.ru")
    print("文献下载模块加载成功")