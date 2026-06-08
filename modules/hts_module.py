#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高通量筛选模块
预测二酐-二胺组合的性能
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

from rdkit import Chem
from rdkit.Chem import AllChem

logger = logging.getLogger(__name__)

# 尝试导入其他模块
try:
    from descriptor_module import DescriptorCalculator
    from training_module import ModelTrainer
except ImportError:
    # 本地导入
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from descriptor_module import DescriptorCalculator
    from training_module import ModelTrainer


class HighThroughputScreener:
    """高通量筛选器"""
    
    # 内置二酐数据库
    DIANHYDRIDES = {
        'PMDA': 'O=C1C(=O)c2ccccc2C1=O',
        'BPDA': 'O=C1C(=O)c2ccc3c2C3=O',
        'ODPA': 'O=C1C(=O)c2ccc(Oc3ccc(C(=O)O5)cc3)cc2C1=O',
        'BTDA': 'O=C1C(=O)c2ccc3c2C(=O)c4ccc(cc4C3=O)C(=O)O1',
        '6FDA': 'O=C1C(=O)C(F)(F)C(F)(F)C(F)(F)C1=O',
        'DSDA': 'O=C1C(=O)c2ccc3c(c2)C(=O)c4ccc(cc4C3=O)C1=O',
        'JPDA': 'O=C1C(=O)c2cccc3c2C1=O',
    }
    
    # 内置二胺数据库  
    DIAMINES = {
        'ODA': 'COc1ccc(N)cc1OC',
        'MDA': 'Cc1ccc(N)cc1',
        'DDE': 'NCCNCCN',
        'm-PDA': 'Nc1cccc(N)c1',
        'p-PDA': 'Nc1ccc(N)cc1',
        '4,4-ODA': 'COc1ccc(Nc2ccc(OC)cc2)cc1',
        'TFDB': 'Nc1c(N)ccc(N)c1',
        'BAPP': 'CC(C)(C)c1ccc(NCCOCCOc2ccc(C(C)(C)C)cc2)cc1',
    }
    
    def __init__(self, output_dir: str = None):
        """
        初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path('output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 描述符计算器
        self.calculator = DescriptorCalculator(output_dir=str(self.output_dir))
        
        # 模型训练器
        self.trainer = ModelTrainer(output_dir=str(self.output_dir / 'models'))
        
    def generate_combinations(self, custom_dianhydrides: Dict = None,
                              custom_diamines: Dict = None) -> List[Dict]:
        """
        生成所有二酐-二胺组合
        
        Args:
            custom_dianhydrides: 自定义二酐字典
            custom_diamines: 自定义二胺字典
            
        Returns:
            组合列表
        """
        dianhydrides = custom_dianhydrides or self.DIANHYDRIDES
        diamines = custom_diamines or self.DIAMINES
        
        combinations = []
        
        for da_name, da_smiles in dianhydrides.items():
            for di_name, di_smiles in diamines.items():
                # 生成组合SMILES（简化版）
                combo_smiles = self._combine_smiles(da_smiles, di_smiles)
                
                combinations.append({
                    '二酐': da_name,
                    '二胺': di_name,
                    '二酐SMILES': da_smiles,
                    '二胺SMILES': di_smiles,
                    'SMILES': combo_smiles
                })
                
        return combinations
        
    def _combine_smiles(self, da_smiles: str, di_smiles: str) -> str:
        """
        合并二酐和二胺SMILES
        
        Args:
            da_smiles: 二酐SMILES
            di_smiles: 二胺SMILES
            
        Returns:
            组合SMILES
        """
        # 简化处理：连接两个SMILES
        # 实际应该生成完整的聚合物链
        return f"{da_smiles}.{di_smiles}"
        
    def calculate_descriptors(self, combinations: List[Dict],
                             calc_rdkit: bool = True,
                             calc_morgan: bool = True) -> pd.DataFrame:
        """
        计算描述符
        
        Args:
            combinations: 组合列表
            calc_rdkit: 是否计算RDKit
            calc_morgan: 是否计算Morgan
            
        Returns:
            描述符DataFrame
        """
        smiles_list = [c['SMILES'] for c in combinations]
        
        dfs = []
        
        if calc_rdkit:
            rdkit_df = self.calculator.calculate_rdkit(smiles_list)
            if not rdkit_df.empty:
                dfs.append(rdkit_df)
                
        if calc_morgan:
            morgan_df = self.calculator.calculate_morgan(smiles_list)
            if not morgan_df.empty:
                dfs.append(morgan_df)
                
        if not dfs:
            return pd.DataFrame()
            
        # 合并
        combined = dfs[0]
        for df in dfs[1:]:
            if 'SMILES' in df.columns:
                combined = pd.merge(combined, df, on='SMILES', how='outer')
                
        return combined
        
    def predict_performance(self, combinations: List[Dict],
                          descriptors_df: pd.DataFrame,
                          target_models: Dict[str, str]) -> pd.DataFrame:
        """
        预测性能
        
        Args:
            combinations: 组合列表
            descriptors_df: 描述符DataFrame
            target_models: 目标-模型文件路径字典
            
        Returns:
            预测结果DataFrame
        """
        import joblib
        
        # 准备特征
        X = descriptors_df.drop(columns=['SMILES'], errors='ignore')
        X = X.select_dtypes(include=[np.number])
        X = X.fillna(0)
        
        # 预测结果
        results = []
        
        for idx, combo in enumerate(combinations):
            row = {
                '二酐': combo['二酐'],
                '二胺': combo['二胺'],
                'SMILES': combo['SMILES']
            }
            
            # 确保特征数量匹配
            if len(X.columns) > 0 and idx < len(X):
                x_pred = X.iloc[idx:idx+1]
                
                # 补齐特征
                if x_pred.shape[1] < X.shape[1]:
                    for col in X.columns:
                        if col not in x_pred.columns:
                            x_pred[col] = 0
                    x_pred = x_pred[X.columns]
                    
                # 使用各模型预测
                for target, model_path in target_models.items():
                    try:
                        model = joblib.load(model_path)
                        pred = model.predict(x_pred)[0]
                        row[target] = pred
                    except Exception as e:
                        logger.warning(f"预测失败 {target}: {e}")
                        row[target] = None
                        
            results.append(row)
            
        return pd.DataFrame(results)
        
    def run_screening(self,
                     custom_dianhydrides: Dict = None,
                     custom_diamines: Dict = None,
                     target_models: Dict[str, str] = None,
                     output_file: str = None) -> pd.DataFrame:
        """
        运行高通量筛选
        
        Args:
            custom_dianhydrides: 自定义二酐
            custom_diamines: 自定义二胺
            target_models: 目标-模型路径字典
            output_file: 输出文件路径
            
        Returns:
            筛选结果DataFrame
        """
        logger.info("开始高通量筛选...")
        
        # 1. 生成组合
        logger.info("生成二酐-二胺组合...")
        combinations = self.generate_combinations(custom_dianhydrides, custom_diamines)
        logger.info(f"生成 {len(combinations)} 种组合")
        
        # 2. 计算描述符
        logger.info("计算分子描述符...")
        descriptors_df = self.calculate_descriptors(combinations)
        logger.info(f"描述符维度: {descriptors_df.shape}")
        
        # 3. 性能预测
        if target_models:
            logger.info("预测性能...")
            results_df = self.predict_performance(combinations, descriptors_df, target_models)
        else:
            # 只返回组合信息
            results_df = pd.DataFrame(combinations)
            
        # 4. 保存结果
        if output_file:
            results_df.to_csv(output_file, index=False)
            logger.info(f"结果已保存: {output_file}")
            
        logger.info(f"高通量筛选完成，共 {len(results_df)} 种组合")
        
        return results_df
        
    def filter_by_threshold(self, results_df: pd.DataFrame,
                           thresholds: Dict[str, float]) -> pd.DataFrame:
        """
        根据阈值筛选
        
        Args:
            results_df: 结果DataFrame
            thresholds: 阈值字典 {目标: 最小值}
            
        Returns:
            筛选后的结果
        """
        filtered = results_df.copy()
        
        for target, min_val in thresholds.items():
            if target in filtered.columns:
                filtered = filtered[filtered[target] >= min_val]
                
        return filtered
        
    def get_top_combinations(self, results_df: pd.DataFrame,
                           target: str, top_n: int = 10) -> pd.DataFrame:
        """
        获取最优组合
        
        Args:
            results_df: 结果DataFrame
            target: 目标性能
            top_n: 返回数量
            
        Returns:
            最优组合
        """
        if target not in results_df.columns:
            return pd.DataFrame()
            
        sorted_df = results_df.sort_values(target, ascending=False)
        return sorted_df.head(top_n)


# 测试
if __name__ == "__main__":
    screener = HighThroughputScreener(output_dir="D:/PI_Project/output")
    
    # 生成组合
    combinations = screener.generate_combinations()
    print(f"生成组合数: {len(combinations)}")
    print(f"二酐: {list(screener.DIANHYDRIDES.keys())}")
    print(f"二胺: {list(screener.DIAMINES.keys())}")
    
    print("高通量筛选模块加载成功")
