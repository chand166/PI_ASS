#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献下载模块
根据DOI批量下载学术文献PDF
"""

import os
import re
import time
import requests
from typing import List, Dict, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class LiteratureDownloader:
    """文献下载器"""
    
    def __init__(self, output_dir: str, max_workers: int = 3, timeout: int = 30):
        """
        初始化下载器
        
        Args:
            output_dir: 输出目录
            max_workers: 最大并发数
            timeout: 超时时间（秒）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.timeout = timeout
        
        # Sci-Hub镜像列表
        self.scihub_urls = [
            "https://sci-hub.se",
            "https://sci-hub.st",
            "https://sci-hub.nu",
            "https://sci-hub.wf",
        ]
        
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
    def parse_doi_file(self, file_path: str) -> List[str]:
        """
        解析DOI文件
        
        Args:
            file_path: DOI文件路径
            
        Returns:
            DOI列表
        """
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
                
            # 尝试找到DOI列
            doi_col = None
            for col in df.columns:
                if 'doi' in col.lower():
                    doi_col = col
                    break
                    
            if doi_col:
                dois = df[doi_col].dropna().astype(str).tolist()
                
        return list(set(dois))  # 去重
        
    def clean_doi(self, doi: str) -> str:
        """清理DOI格式"""
        # 移除URL前缀
        doi = doi.strip()
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi)
        doi = re.sub(r'^doi:', '', doi)
        return doi.strip()
        
    def download_single(self, doi: str, retry: int = 2) -> Dict:
        """
        下载单篇文献
        
        Args:
            doi: DOI
            retry: 重试次数
            
        Returns:
            下载结果
        """
        doi = self.clean_doi(doi)
        
        for attempt in range(retry):
            # 尝试多个Sci-Hub镜像
            for base_url in self.scihub_urls:
                try:
                    # 构建设下载URL
                    download_url = f"{base_url}/{doi}"
                    
                    response = requests.get(
                        download_url,
                        headers=self.headers,
                        timeout=self.timeout,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        # 检查是否是PDF
                        content_type = response.headers.get('Content-Type', '')
                        
                        if 'pdf' in content_type.lower() or response.headers.get('Content-Disposition'):
                            # 保存文件
                            filename = self._sanitize_filename(doi)
                            filepath = self.output_dir / f"{filename}.pdf"
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                                
                            return {
                                'doi': doi,
                                'status': 'success',
                                'filepath': str(filepath),
                                'error': None
                            }
                            
                        # 尝试从响应中提取PDF链接
                        pdf_url = self._extract_pdf_url(response.text, base_url)
                        if pdf_url:
                            pdf_response = requests.get(pdf_url, headers=self.headers, timeout=self.timeout)
                            if pdf_response.status_code == 200:
                                filename = self._sanitize_filename(doi)
                                filepath = self.output_dir / f"{filename}.pdf"
                                
                                with open(filepath, 'wb') as f:
                                    f.write(pdf_response.content)
                                    
                                return {
                                    'doi': doi,
                                    'status': 'success',
                                    'filepath': str(filepath),
                                    'error': None
                                }
                                
                except Exception as e:
                    logger.debug(f"尝试 {base_url} 失败: {e}")
                    continue
                    
            # 等待后重试
            time.sleep(1)
            
        return {
            'doi': doi,
            'status': 'failed',
            'filepath': None,
            'error': '下载失败'
        }
        
    def _extract_pdf_url(self, html: str, base_url: str) -> Optional[str]:
        """从HTML中提取PDF链接"""
        # 查找PDF链接
        patterns = [
            r'href="([^"]*\.pdf[^"]*)"',
            r'src="([^"]*\.pdf[^"]*)"',
            r'download\.href\s*=\s*["\']([^"\']+)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                url = match.group(1)
                # 相对路径转绝对路径
                if not url.startswith('http'):
                    url = base_url + url
                return url
                
        return None
        
    def _sanitize_filename(self, doi: str) -> str:
        """清理文件名"""
        # 替换非法字符
        doi = doi.replace('/', '_').replace(':', '_')
        doi = re.sub(r'[<>:"/\\|?*]', '', doi)
        return doi[:100]  # 限制长度
        
    def download_batch(self, dois: List[str], 
                      progress_callback=None) -> Dict:
        """
        批量下载
        
        Args:
            dois: DOI列表
            progress_callback: 进度回调函数
            
        Returns:
            下载统计
        """
        results = []
        success_count = 0
        failed_count = 0
        failed_dois = []
        
        total = len(dois)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_single, doi): doi for doi in dois}
            
            for idx, future in enumerate(as_completed(futures)):
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
                    
                # 避免请求过快
                time.sleep(0.5)
                
        # 保存失败列表
        if failed_dois:
            failed_file = self.output_dir / "failed_dois.txt"
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(failed_dois))
                
        return {
            'total': total,
            'success': success_count,
            'failed': failed_count,
            'failed_dois': failed_dois,
            'results': results
        }


# 测试
if __name__ == "__main__":
    downloader = LiteratureDownloader(
        output_dir="D:/PI_Project/paper",
        max_workers=3
    )
    
    print("文献下载模块加载成功")
