#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型训练模块
训练机器学习性能预测模型
"""

import os
import warnings
warnings.filterwarnings('ignore')

import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

# 尝试导入XGBoost和LightGBM
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False
    
try:
    import lightgbm as lgb
    LGB_AVAILABLE = True
except ImportError:
    LGB_AVAILABLE = False


class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path('models')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型配置
        self.models_config = {
            'rf': ('RandomForest', RandomForestRegressor),
            'gb': ('GradientBoosting', GradientBoostingRegressor),
            'xgb': ('XGBoost', xgb.XGBRegressor if XGB_AVAILABLE else None),
            'lgb': ('LightGBM', lgb.LGBMRegressor if LGB_AVAILABLE else None),
            'svr': ('SVR', SVR),
            'lr': ('LinearRegression', LinearRegression),
            'ridge': ('RidgeRegression', Ridge),
            'mlp': ('MLP', MLPRegressor),
        }
        
    def prepare_data(self, data_file: str, target_col: str) -> Tuple:
        """
        准备训练数据
        
        Args:
            data_file: 描述符数据文件
            target_col: 目标列名
            
        Returns:
            (X_train, X_test, y_train, y_test)
        """
        df = pd.read_csv(data_file)
        
        # 分离特征和标签
        if target_col not in df.columns:
            raise ValueError(f"未找到目标列: {target_col}")
            
        y = df[target_col].values
        
        # 移除非数值列和目标列
        X = df.drop(columns=[target_col, 'SMILES', '二酐SMILES', '二胺SMILES', 
                            '二酐名称', '二胺名称'], errors='ignore')
        
        # 移除非数值列
        X = X.select_dtypes(include=[np.number])
        
        # 处理缺失值
        X = X.fillna(0)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
        
    def train_model(self, model_type: str, X_train, y_train, 
                   iterations: int = 500) -> object:
        """
        训练单个模型
        
        Args:
            model_type: 模型类型
            X_train: 训练特征
            y_train: 训练标签
            iterations: 迭代次数
            
        Returns:
            训练好的模型
        """
        if model_type not in self.models_config:
            raise ValueError(f"未知模型类型: {model_type}")
            
        name, model_class = self.models_config[model_type]
        
        if model_class is None:
            raise ValueError(f"模型 {model_type} 所需的库未安装")
            
        # 配置模型参数
        params = self._get_model_params(model_type, iterations)
        
        model = model_class(**params)
        
        # 训练
        if model_type == 'mlp':
            model.fit(X_train, y_train)
        else:
            model.fit(X_train, y_train)
            
        return model
        
    def _get_model_params(self, model_type: str, iterations: int) -> Dict:
        """获取模型参数"""
        params = {
            'rf': {
                'n_estimators': iterations,
                'max_depth': 10,
                'random_state': 42,
                'n_jobs': -1
            },
            'gb': {
                'n_estimators': iterations,
                'max_depth': 5,
                'learning_rate': 0.1,
                'random_state': 42
            },
            'xgb': {
                'n_estimators': iterations,
                'max_depth': 6,
                'learning_rate': 0.1,
                'random_state': 42,
                'verbosity': 0
            },
            'lgb': {
                'n_estimators': iterations,
                'max_depth': 6,
                'learning_rate': 0.1,
                'random_state': 42,
                'verbose': -1
            },
            'svr': {
                'kernel': 'rbf',
                'C': 1.0
            },
            'lr': {},
            'ridge': {
                'alpha': 1.0
            },
            'mlp': {
                'hidden_layer_sizes': (100, 50),
                'max_iter': iterations,
                'random_state': 42
            }
        }
        
        return params.get(model_type, {})
        
    def evaluate(self, model, X_test, y_test) -> Dict:
        """
        评估模型
        
        Args:
            model: 训练好的模型
            X_test: 测试特征
            y_test: 测试标签
            
        Returns:
            评估指标字典
        """
        y_pred = model.predict(X_test)
        
        return {
            'R2': r2_score(y_test, y_pred),
            'RMSE': np.sqrt(mean_squared_error(y_test, y_pred)),
            'MAE': mean_absolute_error(y_test, y_pred)
        }
        
    def train_and_evaluate(self, data_file: str, target_col: str,
                          model_types: List[str] = None,
                          iterations: int = 500,
                          save_models: bool = True) -> Dict:
        """
        训练并评估多个模型
        
        Args:
            data_file: 描述符数据文件
            target_col: 目标列名
            model_types: 模型类型列表
            iterations: 迭代次数
            save_models: 是否保存模型
            
        Returns:
            评估结果字典
        """
        # 准备数据
        X_train, X_test, y_train, y_test = self.prepare_data(data_file, target_col)
        
        if model_types is None:
            model_types = ['rf', 'gb', 'lr']
            
        results = {}
        models = {}
        
        for model_type in model_types:
            logger.info(f"训练模型: {model_type}")
            
            try:
                start_time = time.time()
                
                # 训练
                model = self.train_model(model_type, X_train, y_train, iterations)
                
                # 评估
                metrics = self.evaluate(model, X_test, y_test)
                metrics['train_time'] = time.time() - start_time
                
                results[model_type] = metrics
                models[model_type] = model
                
                logger.info(f"{model_type} - R2: {metrics['R2']:.4f}, "
                          f"RMSE: {metrics['RMSE']:.4f}")
                  
                # 保存模型
                if save_models:
                    model_path = self.output_dir / f"{target_col}_{model_type}.pkl"
                    joblib.dump(model, model_path)
                    
            except Exception as e:
                logger.error(f"训练失败 {model_type}: {e}")
                results[model_type] = {'error': str(e)}
                
        # 保存评估结果
        self._save_results(results, target_col)
        
        # 找出最优模型
        best_model = max(results.items(), 
                        key=lambda x: x[1].get('R2', -999))
        
        logger.info(f"最优模型: {best_model[0]}, R2: {best_model[1].get('R2'):.4f}")
        
        return results
        
    def _save_results(self, results: Dict, target_col: str):
        """保存评估结果"""
        # 保存为CSV
        rows = []
        for model_type, metrics in results.items():
            row = {'model': model_type}
            row.update(metrics)
            rows.append(row)
            
        df = pd.DataFrame(rows)
        output_file = self.output_dir / f"{target_col}_model_summary.csv"
        df.to_csv(output_file, index=False)
        
        # 保存为JSON
        output_json = self.output_dir / f"{target_col}_results.json"
        with open(output_json, 'w') as f:
            json.dump(results, f, indent=2)
            
    def get_feature_importance(self, model, feature_names: List[str]) -> pd.DataFrame:
        """
        获取特征重要性
        
        Args:
            model: 训练好的模型
            feature_names: 特征名列表
            
        Returns:
            特征重要性DataFrame
        """
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importance = np.abs(model.coef_)
        else:
            return pd.DataFrame()
            
        df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return df


# 测试
if __name__ == "__main__":
    trainer = ModelTrainer(output_dir="D:/PI_Project/models")
    print("模型训练模块加载成功")
    print(f"XGBoost可用: {XGB_AVAILABLE}")
    print(f"LightGBM可用: {LGB_AVAILABLE}")
