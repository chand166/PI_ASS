#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文献评分模块
使用多评委AI系统对文献进行评分筛选
"""

import os
import re
import json
import time
import threading
import pandas as pd
import requests
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)

# 添加文件日志
log_file = Path("D:/PI_ASS/output/scoring_debug.log")


class LiteratureScorer:
    """文献评分器"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "minimax25",
                 expert_count: int = 10, score_threshold: float = 0.8):
        """
        初始化评分器
        
        Args:
            api_url: API地址
            api_key: API密钥
            model: 模型名称
            expert_count: 专家数量
            score_threshold: 评分阈值
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.expert_count = expert_count
        self.score_threshold = score_threshold
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def score_single_paper(self, title: str, abstract: str, doi: str,
                          scoring_prompt: str) -> Dict:
        """
        对单篇文献评分（多评委）
        
        Args:
            title: 文献标题
            abstract: 文献摘要
            doi: DOI
            scoring_prompt: 评分提示词
            
        Returns:
            评分结果字典
        """
        scores = []
        reasons = []
        
        # 构建评分提示 - 强调主要根据摘要评分，并在最后用【】输出评分
        full_prompt = f"""请作为聚酰亚胺材料领域专家进行文献评分。

【重要】请主要根据文献摘要进行评分，标题仅作为辅助参考。

{scoring_prompt}

文献标题: {title}

文献摘要: {abstract}

请根据以上摘要进行分析，并给出评分。
请严格按照以下格式输出：
评分依据：[简要说明评分原因]
最终评分：【0.XX】

例如：
评分依据：该文献研究了聚酰亚胺在显示器领域的应用，关注了热性能和机械性能，符合研究领域
最终评分：【0.85】"""
        
        # 并行调用多个专家评分
        with ThreadPoolExecutor(max_workers=self.expert_count) as executor:
            futures = []
            for i in range(self.expert_count):
                future = executor.submit(self._call_api, full_prompt)
                futures.append(future)
                
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        score, reason = self._parse_response(result)
                        scores.append(score)
                        reasons.append(reason)
                except Exception as e:
                    error_msg = f"评分失败: {e}"
                    logger.error(error_msg)
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"ERROR: {error_msg}\n")
        
        # 调试：写入最终结果
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Scores collected: {scores}\n")
            f.write(f"Average: {sum(scores) / len(scores) if scores else 0.0}\n\n")
                    
        # 计算平均分
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        # 综合所有专家的评分依据
        combined_reason = "; ".join(set(reasons)) if reasons else ""
        
        return {
            'title': title,
            'abstract': abstract,
            'doi': doi,
            'scores': scores,
            'avg_score': avg_score,
            'reason': combined_reason,
            'selected': avg_score >= self.score_threshold
        }
        
    def _call_api(self, prompt: str) -> Optional[str]:
        """调用API - 增加超时和重试"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                data = {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
                
                response = requests.post(
                    f"{self.api_url}/chat/completions",
                    headers=self.headers,
                    json=data,
                    timeout=120  # 增加到120秒
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_msg = f"API错误: {response.status_code}"
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"Attempt {attempt+1} - {error_msg}\n")
                    
            except requests.exceptions.Timeout:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Attempt {attempt+1} - Timeout, retrying...\n")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
            except Exception as e:
                error_msg = f"API调用失败: {e}"
                logger.error(error_msg)
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"Attempt {attempt+1} - {error_msg}\n")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        return None
            
    def _parse_response(self, response: str) -> Tuple[float, str]:
        """解析API响应 - 优先从【】中提取评分"""
        # 调试：写入文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"=== RAW RESPONSE ===\n{response[:1000]}\n\n")
        
        score = 0.0
        reason = ""
        
        # 优先从【】中提取评分
        bracket_match = re.search(r'【\s*([0-9.]+)\s*】', response)
        if bracket_match:
            score = float(bracket_match.group(1))
            if score > 1:
                score = score / 100
            score = max(0.0, min(1.0, score))
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"Found score in 【】: {score}\n")
        
        # 如果从【】没找到，尝试其他模式
        if score == 0.0:
            score_patterns = [
                r'评分[：:\s]*([0-9.]+)',
                r'分数[：:\s]*([0-9.]+)',
                r'([0-9.]+)\s*分',
                r'Score[：:\s]*([0-9.]+)',
                r'(0\.[0-9]+)',
            ]
            for pattern in score_patterns:
                match = re.search(pattern, response)
                if match:
                    score = float(match.group(1))
                    if score > 1:
                        score = score / 100
                    score = max(0.0, min(1.0, score))
                    break
        
        # 提取评分依据 - 优先取"评分依据："后的内容
        reason_match = re.search(r'评分依据[：:]\s*(.+?)(?:最终评分|\\n|$)', response, re.DOTALL)
        if reason_match:
            reason = reason_match.group(1).strip()
        else:
            reason_patterns = [
                r'依据[：:]?\s*(.+?)(?:。|$)',
                r'原因[：:]?\s*(.+?)(?:。|$)',
                r'理由[：:]?\s*(.+?)(?:。|$)',
            ]
            for pattern in reason_patterns:
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    reason = match.group(1).strip()
                    break
        
        if not reason:
            reason = response[:150].strip()
        
        return score, reason
        
    def score_from_file(self, input_file: str, output_file: str,
                        scoring_prompt: str, 
                        progress_callback=None) -> pd.DataFrame:
        """
        从文件批量评分
        
        Args:
            input_file: 输入文件路径（CSV/Excel）
            output_file: 输出文件路径
            scoring_prompt: 评分提示词
            progress_callback: 进度回调函数
            
        Returns:
            评分结果DataFrame
        """
        # 读取输入文件
        if input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        elif input_file.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(input_file)
        else:
            raise ValueError(f"不支持的文件格式: {input_file}")
            
        # 检查列名
        required_cols = ['标题', '摘要', 'DOI']
        alt_cols = ['title', 'abstract', 'doi', 'Title', 'Abstract', 'DOI']
        
        # 映射列名
        col_mapping = {}
        for req, alt in zip(required_cols, alt_cols):
            if req in df.columns:
                col_mapping[req] = req
            elif alt in df.columns:
                col_mapping[req] = alt
                
        # 重命名列
        if col_mapping:
            df = df.rename(columns=col_mapping)
            
        # 评分
        results = []
        total = len(df)
        
        for idx, row in df.iterrows():
            title = row.get('标题', row.get('title', ''))
            abstract = row.get('摘要', row.get('abstract', ''))
            doi = row.get('DOI', row.get('doi', ''))
            
            result = self.score_single_paper(title, abstract, doi, scoring_prompt)
            results.append(result)
            
            if progress_callback:
                progress_callback(idx + 1, total)
                
            # 避免API限流
            time.sleep(0.5)
            
        # 保存结果
        result_df = pd.DataFrame(results)
        result_df.to_excel(output_file, index=False)
        
        # 保存高分文献DOI
        selected_dois = result_df[result_df['selected']]['doi'].tolist()
        if selected_dois:
            doi_output = output_file.replace('.xlsx', '_selected_dois.txt')
            with open(doi_output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(selected_dois))
                
        return result_df


# 测试
if __name__ == "__main__":
    scorer = LiteratureScorer(
        api_url="http://10.2.39.6:20004/v1",
        api_key="your-api-key",
        model="minimax25",
        expert_count=3,
        score_threshold=0.8
    )
    
    print("文献评分模块加载成功")
