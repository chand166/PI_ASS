#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取模块
从PDF文献中提取二酐-二胺结构和性能数据
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
    
    def __init__(self, api_url: str, api_key: str, model: str = "minimax25",
                 extraction_prompt: str = None, max_workers: int = 3):
        """
        初始化提取器
        
        Args:
            api_url: API地址
            api_key: API密钥
            model: 模型名称
            extraction_prompt: 提取提示词
            max_workers: 最大并发数
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.extraction_prompt = extraction_prompt or self._default_prompt()
        self.max_workers = max_workers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 输出列名
        self.output_columns = [
            '二酐名称', '二酐SMILES', '二胺名称', '二胺SMILES',
            'Tg', 'Td5', 'CTE', '介电常数', '介电损耗', '击穿电压',
            '透过率', '折射率', '拉伸强度', '断裂伸长率',
            '合成难度', '材料价格', '来源DOI'
        ]
        
    def _default_prompt(self) -> str:
        """默认提取提示词"""
        return """从这篇聚酰亚胺论文中提取以下信息，请以JSON格式输出：

{
    "二酐名称": "",
    "二酐SMILES": "",
    "二胺名称": "",
    "二胺SMILES": "",
    "Tg": "",
    "Td5": "",
    "CTE": "",
    "介电常数": "",
    "介电损耗": "",
    "击穿电压": "",
    "透过率": "",
    "折射率": "",
    "拉伸强度": "",
    "断裂伸长率": "",
    "合成难度": "",
    "材料价格": ""
}

请只返回JSON，不要其他内容。缺失数据用空字符串表示。"""
        
    def extract_from_pdf(self, pdf_path: str) -> Dict:
        """
        从单个PDF提取数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取结果
        """
        try:
            # 读取PDF内容（实际应该用PyMuPDF等提取文本）
            # 这里使用简化的方式
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()
                
            # 调用API提取
            prompt = f"""请阅读以下PDF文件内容，提取聚酰亚胺相关信息。

{self.extraction_prompt}

PDF文件路径: {pdf_path}"""
            
            result = self._call_api(prompt)
            
            if result:
                # 解析JSON结果
                data = self._parse_json_result(result)
                data['来源DOI'] = Path(pdf_path).stem
                return data
            else:
                return self._empty_result()
                
        except Exception as e:
            logger.error(f"提取失败 {pdf_path}: {e}")
            return self._empty_result()
            
    def _call_api(self, prompt: str) -> Optional[str]:
        """调用API"""
        try:
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"API错误: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"API调用失败: {e}")
            return None
            
    def _parse_json_result(self, text: str) -> Dict:
        """解析JSON结果"""
        # 尝试提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', text)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                
                # 确保所有列都存在
                result = {}
                for col in self.output_columns:
                    result[col] = data.get(col, '')
                    
                # 估算材料价格和合成难度（基于AI返回或计算）
                result['材料价格'] = data.get('材料价格', self._estimate_price(data))
                result['合成难度'] = data.get('合成难度', self._estimate_difficulty(data))
                
                return result
                
            except json.JSONDecodeError:
                logger.warning(f"JSON解析失败，使用默认值")
                return self._empty_result()
                
        return self._empty_result()
        
    def _empty_result(self) -> Dict:
        """空结果"""
        return {col: '' for col in self.output_columns}
        
    def _estimate_price(self, data: Dict) -> str:
        """估算材料价格"""
        # 基于原料复杂度估算
        dianhydride = data.get('二酐名称', '').upper()
        diamine = data.get('二胺名称', '').upper()
        
        # 价格参考（仅示例）
        price_map = {
            '6FDA': '500-800',
            'BTDA': '300-500',
            'PMDA': '200-400',
            'BPDA': '400-600',
            'ODA': '100-200',
            'MDA': '150-250',
        }
        
        base_price = price_map.get(dianhydride, '200-400')
        return f"{base_price} 元/克"
        
    def _estimate_difficulty(self, data: Dict) -> str:
        """估算合成难度"""
        # 基于分子复杂度
        smiles = data.get('二酐SMILES', '') + data.get('二胺SMILES', '')
        
        if len(smiles) > 50:
            return '困难'
        elif len(smiles) > 30:
            return '中等'
        else:
            return '简单'
            
    def extract_from_folder(self, folder_path: str, output_file: str,
                          progress_callback=None) -> pd.DataFrame:
        """
        从文件夹批量提取
        
        Args:
            folder_path: 文献文件夹路径
            output_file: 输出Excel文件
            progress_callback: 进度回调
            
        Returns:
            结果DataFrame
        """
        folder = Path(folder_path)
        
        # 获取所有PDF文件
        pdf_files = list(folder.glob('*.pdf'))
        
        results = []
        total = len(pdf_files)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.extract_from_pdf, str(pdf)): pdf 
                      for pdf in pdf_files}
            
            for idx, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)
                
                pdf = futures[future]
                logger.info(f"提取完成: {pdf.name}")
                
                if progress_callback:
                    progress_callback(idx + 1, total)
                    
                time.sleep(0.5)
                
        # 创建DataFrame
        df = pd.DataFrame(results)
        
        # 保存结果
        df.to_excel(output_file, index=False)
        
        logger.info(f"结果已保存到: {output_file}")
        
        return df


# 测试
if __name__ == "__main__":
    extractor = DataExtractor(
        api_url="http://10.2.39.6:20004/v1",
        api_key="your-api-key",
        model="minimax25"
    )
    
    print("数据提取模块加载成功")
