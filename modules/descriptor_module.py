#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
描述符计算模块
计算RDKit、Morgan、Mordred、PaDEL、DeepChem描述符
"""

import os
import warnings
warnings.filterwarnings('ignore')

from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# 尝试导入各描述符计算库
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem, rdMolDescriptors
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit未安装")

try:
    from mordred import Calculator, descriptors
    MORDRED_AVAILABLE = True
except ImportError:
    MORDRED_AVAILABLE = False
    logger.warning("Mordred未安装")

try:
    from padelpy import from_smiles
    PADEL_AVAILABLE = True
except ImportError:
    PADEL_AVAILABLE = False
    logger.warning("PaDEL未安装")


class DescriptorCalculator:
    """描述符计算器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path('data')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # RDKit描述符列表
        self.rdkit_descriptors = [
            'MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
            'NumRotatableBonds', 'NumAromaticRings', 'NumHeteroatoms',
            'FractionCSP3', 'NumValenceElectrons', 'NumRadicalElectrons',
            'HeavyAtomCount', 'RingCount', 'NumAliphaticRings',
            'NumSaturatedRings', 'NumAromaticHeterocycles', 'NumAromaticCarbocycles',
            'NumHeavyAtoms', 'NumC', 'NumN', 'NumO', 'NumS', 'NumF', 'NumCl', 'NumBr',
            'LabuteASA', 'BalabanJ', 'BertzCT', 'Chi0', 'Chi1', 'Chi0n', 'Chi1n',
            'Kappa1', 'Kappa2', 'Kappa3', 'HallKierAlpha', 'LabuteASA',
            'PEOE_VSA1', 'PEOE_VSA2', 'PEOE_VSA3', 'PEOE_VSA4', 'PEOE_VSA5', 'PEOE_VSA6',
            'SMR_VSA1', 'SMR_VSA2', 'SMR_VSA3', 'SMR_VSA4', 'SMR_VSA5', 'SMR_VSA6',
            'MaxEStateIndex', 'MinEStateIndex', 'MaxAbsEStateIndex', 'MinAbsEStateIndex',
        ]
        
    def calculate_rdkit(self, smiles_list: List[str]) -> pd.DataFrame:
        """
        计算RDKit描述符
        
        Args:
            smiles_list: SMILES列表
            
        Returns:
            描述符DataFrame
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit未安装")
            return pd.DataFrame()
            
        results = []
        
        for idx, smiles in enumerate(smiles_list):
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    logger.warning(f"无法解析SMILES: {smiles}")
                    results.append({})
                    continue
                    
                # 计算描述符
                row = {'SMILES': smiles}
                
                for desc_name in self.rdkit_descriptors:
                    try:
                        func = getattr(Descriptors, desc_name, None)
                        if func:
                            row[desc_name] = func(mol)
                        else:
                            row[desc_name] = np.nan
                    except:
                        row[desc_name] = np.nan
                        
                results.append(row)
                
            except Exception as e:
                logger.error(f"计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
                
        return pd.DataFrame(results)
        
    def calculate_morgan(self, smiles_list: List[str], 
                         radius: int = 2, nBits: int = 2048) -> pd.DataFrame:
        """
        计算Morgan指纹
        
        Args:
            smiles_list: SMILES列表
            radius: 指纹半径
            nBits: 位数
            
        Returns:
            Morgan指纹DataFrame
        """
        if not RDKIT_AVAILABLE:
            logger.error("RDKit未安装")
            return pd.DataFrame()
            
        results = []
        
        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    results.append({'SMILES': smiles})
                    continue
                    
                # 计算Morgan指纹
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
                arr = np.zeros((nBits,), dtype=np.int8)
                
                for idx in fp.GetOnBits():
                    arr[idx] = 1
                    
                row = {'SMILES': smiles}
                row.update({f'Bit{i}': arr[i] for i in range(nBits)})
                results.append(row)
                
            except Exception as e:
                logger.error(f"计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
                
        return pd.DataFrame(results)
        
    def calculate_mordred(self, smiles_list: List[str]) -> pd.DataFrame:
        """
        计算Mordred描述符
        
        Args:
            smiles_list: SMILES列表
            
        Returns:
            描述符DataFrame
        """
        if not MORDRED_AVAILABLE:
            logger.error("Mordred未安装")
            return pd.DataFrame()
            
        calc = Calculator(descriptors, ignore_3D=True)
        
        results = []
        
        for smiles in smiles_list:
            try:
                mol = Chem.MolFromSmiles(smiles)
                if mol is None:
                    results.append({'SMILES': smiles})
                    continue
                    
                # 计算描述符
                row = {'SMILES': smiles}
                descs = calc(mol)
                
                for name, value in descs.items():
                    try:
                        row[str(name)] = float(value)
                    except:
                        row[str(name)] = np.nan
                        
                results.append(row)
                
            except Exception as e:
                logger.error(f"计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
                
        return pd.DataFrame(results)
        
    def calculate_padel(self, smiles_list: List[str]) -> pd.DataFrame:
        """
        计算PaDEL描述符
        
        Args:
            smiles_list: SMILES列表
            
        Returns:
            描述符DataFrame
        """
        if not PADEL_AVAILABLE:
            logger.error("PaDEL未安装")
            return pd.DataFrame()
            
        results = []
        
        for smiles in smiles_list:
            try:
                # 使用padelpy计算
                descriptors = from_smiles(smiles, fingerprints=True)
                row = {'SMILES': smiles}
                row.update(descriptors)
                results.append(row)
                
            except Exception as e:
                logger.error(f"计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
                
        return pd.DataFrame(results)
        
    def calculate_all(self, input_file: str,
                     calc_rdkit: bool = True,
                     calc_morgan: bool = True,
                     calc_mordred: bool = False,
                     calc_padel: bool = False,
                     morgan_radius: int = 2,
                     morgan_bits: int = 2048) -> Dict[str, pd.DataFrame]:
        """
        计算所有选择的描述符
        
        Args:
            input_file: 输入CSV文件
            calc_rdkit: 是否计算RDKit
            calc_morgan: 是否计算Morgan
            calc_mordred: 是否计算Mordred
            calc_padel: 是否计算PaDEL
            morgan_radius: Morgan指纹半径
            morgan_bits: Morgan指纹位数
            
        Returns:
            描述符文件路径字典
        """
        # 读取输入
        df = pd.read_csv(input_file)
        
        # 获取SMILES列
        smiles_col = None
        for col in df.columns:
            if 'smiles' in col.lower():
                smiles_col = col
                break
                
        if smiles_col is None:
            raise ValueError("未找到SMILES列")
            
        smiles_list = df[smiles_col].tolist()
        
        output_files = {}
        
        # 计算各类型描述符
        if calc_rdkit:
            logger.info("计算RDKit描述符...")
            rdkit_df = self.calculate_rdkit(smiles_list)
            output_file = self.output_dir / "rdkit_descriptors.csv"
            rdkit_df.to_csv(output_file, index=False)
            output_files['rdkit'] = str(output_file)
            logger.info(f"RDKit描述符已保存: {output_file}")
            
        if calc_morgan:
            logger.info("计算Morgan指纹...")
            morgan_df = self.calculate_morgan(smiles_list, morgan_radius, morgan_bits)
            output_file = self.output_dir / "morgan_fingerprints.csv"
            morgan_df.to_csv(output_file, index=False)
            output_files['morgan'] = str(output_file)
            logger.info(f"Morgan指纹已保存: {output_file}")
            
        if calc_mordred:
            logger.info("计算Mordred描述符...")
            mordred_df = self.calculate_mordred(smiles_list)
            output_file = self.output_dir / "mordred_descriptors.csv"
            mordred_df.to_csv(output_file, index=False)
            output_files['mordred'] = str(output_file)
            logger.info(f"Mordred描述符已保存: {output_file}")
            
        if calc_padel:
            logger.info("计算PaDEL描述符...")
            padel_df = self.calculate_padel(smiles_list)
            output_file = self.output_dir / "padel_descriptors.csv"
            padel_df.to_csv(output_file, index=False)
            output_files['padel'] = str(output_file)
            logger.info(f"PaDEL描述符已保存: {output_file}")
            
        # 合并所有描述符
        if len(output_files) > 1:
            self._combine_descriptors(list(output_files.values()))
            
        return output_files
        
    def _combine_descriptors(self, descriptor_files: List[str]):
        """合并描述符文件"""
        dfs = []
        
        for file in descriptor_files:
            df = pd.read_csv(file)
            if 'SMILES' in df.columns:
                dfs.append(df)
                
        if dfs:
            # 合并（按SMILES对齐）
            combined = dfs[0]
            for df in dfs[1:]:
                if 'SMILES' in df.columns:
                    combined = pd.merge(combined, df, on='SMILES', how='outer')
                    
            # 保存合并结果
            output_file = self.output_dir / "descriptors_combined.csv"
            combined.to_csv(output_file, index=False)
            logger.info(f"合并描述符已保存: {output_file}")


# 测试
if __name__ == "__main__":
    calculator = DescriptorCalculator(output_dir="D:/PI_Project/data")
    print("描述符计算模块加载成功")
    
    # 测试RDKit
    smiles = ['O=C1C(=O)c2ccccc2C1=O', 'COc1ccc(N)cc1OC']  # PMDA, ODA
    if RDKIT_AVAILABLE:
        df = calculator.calculate_rdkit(smiles)
        print(f"RDKit描述符形状: {df.shape}")
