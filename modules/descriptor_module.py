#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
描述符计算模块
计算 RDKit / Morgan / Mordred / PaDEL 描述符
支持进度回调与取消事件（适配 Streamlit 后台线程模式）
"""

import os
import warnings
warnings.filterwarnings('ignore')

from typing import List, Dict, Optional, Callable
from pathlib import Path
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ---------------- 各描述符库可用性探测 ----------------
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
    PADEL_LIB_AVAILABLE = True
except ImportError:
    PADEL_LIB_AVAILABLE = False
    logger.warning("PaDEL未安装")


def _java_available() -> bool:
    """检测 Java；若不在 PATH 则回退搜索常见 JDK 路径，并把 bin 加入 PATH 供 padelpy 子进程使用"""
    import shutil, subprocess, os, glob
    java = shutil.which("java")
    if java:
        try:
            subprocess.run([java, "-version"], capture_output=True, timeout=10)
            return True
        except Exception:
            pass
    # 回退：常见 JDK 安装路径（winget/Temurin/Zulu/Adoptium 等）
    bases = [r"C:\Program Files\Microsoft", r"C:\Program Files\Eclipse Adoptium",
             r"C:\Program Files\Java", r"C:\Program Files (x86)\Java",
             r"C:\Program Files\Zulu", r"C:\Program Files\Temurin"]
    patterns = []
    for b in bases:
        patterns += [os.path.join(b, "jdk*", "bin", "java.exe"),
                     os.path.join(b, "*", "bin", "java.exe")]
    cand = []
    for p in patterns:
        cand += glob.glob(p)
    for jexe in cand:
        try:
            subprocess.run([jexe, "-version"], capture_output=True, timeout=10)
            os.environ["PATH"] = os.path.dirname(jexe) + os.pathsep + os.environ.get("PATH", "")
            logger.info(f"检测到Java: {jexe}，已加入PATH")
            return True
        except Exception:
            continue
    return False


JAVA_AVAILABLE = _java_available()
# PaDEL 真正可用 = padelpy 库 + Java 运行环境 双重满足
PADEL_AVAILABLE = PADEL_LIB_AVAILABLE and JAVA_AVAILABLE
if PADEL_LIB_AVAILABLE and not JAVA_AVAILABLE:
    logger.warning("PaDEL已安装但未检测到Java运行环境，PaDEL不可用")


def _cancelled(cancel_event) -> bool:
    return cancel_event is not None and cancel_event.is_set()


class DescriptorCalculator:
    """描述符计算器（支持逐分子进度回调与取消）"""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path('data')
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # RDKit 内置描述符列表（去重）
        self.rdkit_descriptors = list(dict.fromkeys([
            'MolWt', 'MolLogP', 'TPSA', 'NumHDonors', 'NumHAcceptors',
            'NumRotatableBonds', 'NumAromaticRings', 'NumHeteroatoms',
            'FractionCSP3', 'NumValenceElectrons', 'NumRadicalElectrons',
            'HeavyAtomCount', 'RingCount', 'NumAliphaticRings',
            'NumSaturatedRings', 'NumAromaticHeterocycles', 'NumAromaticCarbocycles',
            'NumHeavyAtoms', 'NumC', 'NumN', 'NumO', 'NumS', 'NumF', 'NumCl', 'NumBr',
            'LabuteASA', 'BalabanJ', 'BertzCT', 'Chi0', 'Chi1', 'Chi0n', 'Chi1n',
            'Kappa1', 'Kappa2', 'Kappa3', 'HallKierAlpha',
            'PEOE_VSA1', 'PEOE_VSA2', 'PEOE_VSA3', 'PEOE_VSA4', 'PEOE_VSA5', 'PEOE_VSA6',
            'SMR_VSA1', 'SMR_VSA2', 'SMR_VSA3', 'SMR_VSA4', 'SMR_VSA5', 'SMR_VSA6',
            'MaxEStateIndex', 'MinEStateIndex', 'MaxAbsEStateIndex', 'MinAbsEStateIndex',
        ]))

    # ---------------- RDKit ----------------
    def calculate_rdkit(self, smiles_list, progress_callback=None, cancel_event=None) -> pd.DataFrame:
        if not RDKIT_AVAILABLE:
            logger.error("RDKit未安装")
            return pd.DataFrame()
        results = []
        n = len(smiles_list)
        for idx, smiles in enumerate(smiles_list):
            if _cancelled(cancel_event):
                break
            try:
                mol = Chem.MolFromSmiles(str(smiles))
                if mol is None:
                    results.append({'SMILES': smiles})
                else:
                    row = {'SMILES': smiles}
                    for desc_name in self.rdkit_descriptors:
                        try:
                            func = getattr(Descriptors, desc_name, None)
                            row[desc_name] = float(func(mol)) if func else np.nan
                        except Exception:
                            row[desc_name] = np.nan
                    results.append(row)
            except Exception as e:
                logger.error(f"RDKit计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
            if progress_callback:
                progress_callback(idx + 1, n)
        return pd.DataFrame(results)

    # ---------------- Morgan 指纹 ----------------
    def calculate_morgan(self, smiles_list, radius: int = 2, nBits: int = 2048,
                         progress_callback=None, cancel_event=None) -> pd.DataFrame:
        if not RDKIT_AVAILABLE:
            logger.error("RDKit未安装")
            return pd.DataFrame()
        results = []
        n = len(smiles_list)
        for idx, smiles in enumerate(smiles_list):
            if _cancelled(cancel_event):
                break
            try:
                mol = Chem.MolFromSmiles(str(smiles))
                if mol is None:
                    results.append({'SMILES': smiles})
                else:
                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
                    arr = np.zeros((nBits,), dtype=np.int8)
                    for i in fp.GetOnBits():
                        arr[i] = 1
                    row = {'SMILES': smiles}
                    row.update({f'Bit{i}': int(arr[i]) for i in range(nBits)})
                    results.append(row)
            except Exception as e:
                logger.error(f"Morgan计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
            if progress_callback:
                progress_callback(idx + 1, n)
        return pd.DataFrame(results)

    # ---------------- Mordred ----------------
    def calculate_mordred(self, smiles_list, ignore_3D: bool = True,
                          progress_callback=None, cancel_event=None) -> pd.DataFrame:
        if not MORDRED_AVAILABLE:
            logger.error("Mordred未安装")
            return pd.DataFrame()
        calc = Calculator(descriptors, ignore_3D=ignore_3D)
        results = []
        n = len(smiles_list)
        for idx, smiles in enumerate(smiles_list):
            if _cancelled(cancel_event):
                break
            try:
                mol = Chem.MolFromSmiles(str(smiles))
                if mol is None:
                    results.append({'SMILES': smiles})
                else:
                    row = {'SMILES': smiles}
                    descs = calc(mol)
                    for name, value in descs.items():
                        try:
                            row[str(name)] = float(value)
                        except Exception:
                            row[str(name)] = np.nan
                    results.append(row)
            except Exception as e:
                logger.error(f"Mordred计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
            if progress_callback:
                progress_callback(idx + 1, n)
        return pd.DataFrame(results)

    # ---------------- PaDEL ----------------
    def calculate_padel(self, smiles_list, fingerprints: bool = False,
                        timeout: int = 60, progress_callback=None,
                        cancel_event=None) -> pd.DataFrame:
        if not PADEL_AVAILABLE:
            logger.error("PaDEL不可用（padelpy或Java缺失）")
            return pd.DataFrame()
        results = []
        n = len(smiles_list)
        for idx, smiles in enumerate(smiles_list):
            if _cancelled(cancel_event):
                break
            try:
                descs = from_smiles(str(smiles), fingerprints=fingerprints, timeout=timeout)
                row = {'SMILES': smiles}
                if descs:
                    d = descs[0] if isinstance(descs, list) else descs
                    row.update(d)
                results.append(row)
            except Exception as e:
                logger.error(f"PaDEL计算失败 {smiles}: {e}")
                results.append({'SMILES': smiles})
            if progress_callback:
                progress_callback(idx + 1, n)
        return pd.DataFrame(results)

    # ---------------- 统一编排入口 ----------------
    def compute(self, smiles_list,
                calc_rdkit: bool = True, calc_morgan: bool = True,
                calc_mordred: bool = False, calc_padel: bool = False,
                morgan_radius: int = 2, morgan_bits: int = 2048,
                mordred_3d: bool = False, padel_fp: bool = False,
                padel_timeout: int = 60,
                progress_callback=None, cancel_event=None) -> Dict[str, pd.DataFrame]:
        """
        统一计算入口，按启用项依次计算，返回 {source: DataFrame}。
        progress_callback(done, total) 在每个分子完成后回调。
        """
        smiles_list = [s for s in smiles_list
                       if s is not None and str(s).strip()
                       and str(s).lower() != 'nan']
        out: Dict[str, pd.DataFrame] = {}
        if calc_rdkit:
            logger.info("计算RDKit描述符...")
            out['rdkit'] = self.calculate_rdkit(smiles_list, progress_callback, cancel_event)
        if _cancelled(cancel_event):
            return out
        if calc_morgan:
            logger.info("计算Morgan指纹...")
            out['morgan'] = self.calculate_morgan(smiles_list, morgan_radius, morgan_bits,
                                                  progress_callback, cancel_event)
        if _cancelled(cancel_event):
            return out
        if calc_mordred:
            logger.info("计算Mordred描述符...")
            out['mordred'] = self.calculate_mordred(smiles_list, not mordred_3d,
                                                    progress_callback, cancel_event)
        if _cancelled(cancel_event):
            return out
        if calc_padel:
            logger.info("计算PaDEL描述符...")
            out['padel'] = self.calculate_padel(smiles_list, padel_fp, padel_timeout,
                                               progress_callback, cancel_event)
        return out

    def combine(self, frames: List[pd.DataFrame]) -> pd.DataFrame:
            """按 SMILES 列横向合并多个描述符 DataFrame（自动去重复列，合并前先去重避免笛卡尔积膨胀）"""
            dfs = [f for f in frames if f is not None and not f.empty]
            if not dfs:
                return pd.DataFrame()
            # 每个源按 SMILES 去重，避免后续 merge 产生笛卡尔积
            combined = dfs[0].drop_duplicates(subset=['SMILES']).reset_index(drop=True)
            for df in dfs[1:]:
                cols = [c for c in df.columns if c != 'SMILES']
                if not cols:
                    continue
                df_deduped = df[['SMILES'] + cols].drop_duplicates(subset=['SMILES']).reset_index(drop=True)
                combined = pd.merge(combined, df_deduped, on='SMILES', how='outer')
                combined = combined.loc[:, ~combined.columns.duplicated()]
            return combined

    def combine_monomer_pairs(
        self,
        descriptor_dfs: Dict[str, pd.DataFrame],
        pair_df: pd.DataFrame,
        da_smiles_col: str = "酸酐1_SMILES",
        di_smiles_col: str = "二胺1_SMILES",
        perf_cols: Optional[List[str]] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        将酸酐和二胺的单体描述符等权加和（按 SMILES 配对对齐）,
        返回 {source: combined_df}，每行包含 SMILES列 + 加和后的描述符列。

        Parameters
        ----------
        descriptor_dfs : {source_name: DataFrame_with_SMILES_col}
        pair_df : DataFrame，必须包含 da_smiles_col / di_smiles_col + 可选性能列
        da_smiles_col : 酸酐 SMILES 列名
        di_smiles_col : 二胺 SMILES 列名
        perf_cols : 需要保留到输出中的性能标签列

        Returns
        -------
        {source: DataFrame} 每行对应一个聚合物（酸酐+二胺配对），
        描述符列 = 酸酐描述符 + 二胺描述符（等权加和），
        额外保留 da_smiles_col / di_smiles_col 及 perf_cols。
        """
        if perf_cols is None:
            perf_cols = []

        pair_df = pair_df.copy()
        # 确保 SMILES 列字符串化，去空白
        for sc in [da_smiles_col, di_smiles_col]:
            if sc in pair_df.columns:
                pair_df[sc] = pair_df[sc].astype(str).str.strip()

        out: Dict[str, pd.DataFrame] = {}
        for src, ddf in descriptor_dfs.items():
            if ddf is None or ddf.empty:
                continue
            ddf = ddf.copy()
            # 列名归一化：确保有 'SMILES' 列
            if 'SMILES' not in ddf.columns:
                continue
            ddf['SMILES'] = ddf['SMILES'].astype(str).str.strip()

            # 构建 SMILES → 描述符向量 的查找表（排除 SMILES 本身）
            desc_cols = [c for c in ddf.columns if c != 'SMILES']
            if not desc_cols:
                continue

            # 去重：同一 SMILES 可能对应多行，取均值
            lookup = ddf.groupby('SMILES')[desc_cols].mean().reset_index()
            sm2vec = {row['SMILES']: row[desc_cols].to_dict()
                      for _, row in lookup.iterrows()}

            rows = []
            for _, prow in pair_df.iterrows():
                da_smi = prow.get(da_smiles_col, '')
                di_smi = prow.get(di_smiles_col, '')
                da_vec = sm2vec.get(da_smi)
                di_vec = sm2vec.get(di_smi)

                # 至少一个能找到才保留
                if da_vec is None and di_vec is None:
                    continue

                combined_row = {}
                # 保留原始 SMILES 列
                combined_row[da_smiles_col] = da_smi
                combined_row[di_smiles_col] = di_smi

                # 等权加和：每个描述符列 = da值 + di值
                for col in desc_cols:
                    v_da = da_vec.get(col, 0.0) if da_vec else 0.0
                    v_di = di_vec.get(col, 0.0) if di_vec else 0.0
                    combined_row[col] = v_da + v_di

                # 保留性能标签列
                for pc in perf_cols:
                    if pc in pair_df.columns:
                        combined_row[pc] = prow.get(pc)

                rows.append(combined_row)

            if rows:
                result_df = pd.DataFrame(rows)
                # 调整列序：原始 SMILES 列 + 描述符 + 性能标签
                cols_order = [da_smiles_col, di_smiles_col] + [
                    c for c in desc_cols if c in result_df.columns
                ] + [c for c in perf_cols if c in result_df.columns]
                cols_order = [c for c in cols_order if c in result_df.columns]
                result_df = result_df[cols_order]
                out[src] = result_df
            else:
                out[src] = pd.DataFrame()

        return out


# 测试
if __name__ == "__main__":
    calc = DescriptorCalculator(output_dir="D:/PI_Project/data")
    print("描述符计算模块加载成功")
    print("RDKIT:", RDKIT_AVAILABLE, "MORDRED:", MORDRED_AVAILABLE,
          "PADEL_LIB:", PADEL_LIB_AVAILABLE, "JAVA:", JAVA_AVAILABLE, "PADEL:", PADEL_AVAILABLE)
    smiles = ['O=C1C(=O)c2ccccc2C1=O', 'COc1ccc(N)cc1OC']  # PMDA, ODA
    if RDKIT_AVAILABLE:
        df = calc.calculate_rdkit(smiles)
        print(f"RDKit描述符形状: {df.shape}")
    if MORDRED_AVAILABLE:
        df = calc.calculate_mordred(smiles)
        print(f"Mordred描述符形状: {df.shape}")