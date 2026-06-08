# PI_ASS — 聚酰亚胺智能筛选系统

**PI-SCREEN: AI-Powered Polyimide Performance Prediction System**

基于机器学习的聚酰亚胺（PI）材料性能预测与高通量筛选平台。

## 功能模块

| 模块 | 说明 |
|------|------|
| 📚 文献下载 | 自动从学术数据库检索并下载 PI 相关文献 |
| 📊 文献评分 | AI 驱动的文献相关性评分与筛选 |
| 🔍 数据提取 | 从文献中自动提取 PI 结构与性能数据 |
| 🧬 描述符计算 | 基于分子结构计算理化描述符 |
| 🤖 模型训练 | 多算法 ML 模型训练与交叉验证 |
| 🔬 高通量筛选 | 基于训练模型的大规模虚拟筛选 |

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/PI_ASS.git
cd PI_ASS

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
streamlit run src/app.py
```

## 项目结构

```
PI_ASS/
├── src/
│   └── app.py              # Streamlit 主应用
├── modules/
│   ├── __init__.py
│   ├── download_module.py   # 文献下载
│   ├── scoring_module.py    # 文献评分
│   ├── extraction_module.py # 数据提取
│   ├── descriptor_module.py # 描述符计算
│   ├── training_module.py   # 模型训练
│   └── hts_module.py        # 高通量筛选
├── data/                    # 数据文件
├── docs/                    # 文档
├── tests/                   # 测试
├── requirements.txt
├── .gitignore
└── README.md
```

## 技术栈

- **前端**: Streamlit
- **数据处理**: Pandas, NumPy
- **机器学习**: scikit-learn, joblib
- **化学信息学**: RDKit
- **可视化**: Matplotlib

## License

MIT
