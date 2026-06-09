# -*- coding: utf-8 -*-
"""
PI-SCREEN 国际化模块 (i18n)
支持中英文切换
"""

# ==================== 翻译字典 ====================
TRANSLATIONS = {
    # === 通用 ===
    "app_title": {
        "zh": "PI-SCREEN | 聚酰亚胺性能预测",
        "en": "PI-SCREEN | Polyimide Performance Prediction"
    },
    "app_subtitle": {
        "zh": "聚酰亚胺性能预测系统",
        "en": "Polyimide Performance Prediction System"
    },
    "app_full_name": {
        "zh": "聚酰亚胺性能预测与高通量筛选系统",
        "en": "Polyimide Performance Prediction & High-Throughput Screening System"
    },
    "powered_by_ai": {
        "zh": "AI 驱动研究",
        "en": "AI-Powered Research"
    },
    
    # === 侧边栏 ===
    "sidebar_title": {
        "zh": "📋 功能模块",
        "en": "📋 Modules"
    },
    "quick_links": {
        "zh": "💡 快速链接",
        "en": "💡 Quick Links"
    },
    "rdkit_ready": {
        "zh": "RDKit 已就绪",
        "en": "RDKit Ready"
    },
    "rdkit_running": {
        "zh": "分子计算引擎运行中",
        "en": "Molecular engine running"
    },
    "rdkit_not_installed": {
        "zh": "RDKit 未安装",
        "en": "RDKit not installed"
    },
    "rdkit_install_hint": {
        "zh": "运行: pip install rdkit",
        "en": "Run: pip install rdkit"
    },
    
    # === 导航菜单 ===
    "nav_home": {"zh": "🏠 首页", "en": "🏠 Home"},
    "nav_scoring": {"zh": "📚 文献评分", "en": "📚 Literature Scoring"},
    "nav_download": {"zh": "📥 文献下载", "en": "📥 Literature Download"},
    "nav_extraction": {"zh": "🔬 数据提取", "en": "🔬 Data Extraction"},
    "nav_descriptors": {"zh": "🧪 描述符计算", "en": "🧪 Descriptor Calculation"},
    "nav_training": {"zh": "🤖 模型训练", "en": "🤖 Model Training"},
    "nav_hts": {"zh": "🔍 高通量筛选", "en": "🔍 HTS Screening"},
    "nav_settings": {"zh": "⚙️ 系统设置", "en": "⚙️ Settings"},
    "nav_help": {"zh": "📖 使用说明", "en": "📖 User Guide"},
    
    # === 快速链接 ===
    "btn_project": {"zh": "📁 项目", "en": "📁 Project"},
    "btn_data": {"zh": "📊 数据", "en": "📊 Data"},
    "btn_model": {"zh": "🤖 模型", "en": "🤖 Model"},
    "btn_output": {"zh": "📤 输出", "en": "📤 Output"},
    
    # === 首页 ===
    "home_core_capabilities": {
        "zh": "系统核心能力",
        "en": "Core Capabilities"
    },
    "home_parallel_scoring": {
        "zh": "AI评委并行评分",
        "en": "Parallel AI Scoring"
    },
    "home_molecule_prediction": {
        "zh": "分子组合预测",
        "en": "Molecule Predictions"
    },
    "home_core_modules": {
        "zh": "核心功能模块",
        "en": "Core Modules"
    },
    "home_feature_title": {
        "zh": "核心功能模块",
        "en": "Core Feature Modules"
    },
    "home_feature_subtitle": {
        "zh": "探索聚酰亚胺材料的无限可能",
        "en": "Explore the Infinite Possibilities of Polyimide Materials"
    },
    "home_scoring_title": {"zh": "文献评分", "en": "Literature Scoring"},
    "home_scoring_desc": {
        "zh": "10评委AI系统智能筛选高相关度文献",
        "en": "10 AI reviewers intelligently screen high-relevance literature"
    },
    "home_extraction_title": {"zh": "数据提取", "en": "Data Extraction"},
    "home_extraction_desc": {
        "zh": "从文献PDF中自动提取结构与性能数据",
        "en": "Automatically extract structure and property data from literature PDFs"
    },
    "home_hts_title": {"zh": "高通量筛选", "en": "HTS Screening"},
    "home_hts_desc": {
        "zh": "预测80+二酐-二胺组合的性能表现",
        "en": "Predict performance of 80+ dianhydride-diamine combinations"
    },
    "home_enter_module": {"zh": "进入模块 →", "en": "Enter Module →"},
    "home_project_status": {
        "zh": "项目状态概览",
        "en": "Project Status Overview"
    },
    "home_realtime_monitor": {
        "zh": "实时数据监控",
        "en": "Real-time Data Monitoring"
    },
    "home_paper_count": {"zh": "文献数量", "en": "Papers"},
    "home_data_files": {"zh": "数据文件", "en": "Data Files"},
    "home_trained_models": {"zh": "训练模型", "en": "Trained Models"},
    "home_output_results": {"zh": "输出结果", "en": "Output Results"},
    "home_molecular_db": {
        "zh": "🧪 内置分子数据库",
        "en": "🧪 Built-in Molecular Database"
    },
    "home_molecular_db_sub": {
        "zh": "二酐与二胺分子结构库",
        "en": "Dianhydride & Diamine Structure Libraries"
    },
    "home_dianhydride_db": {"zh": "🧪 二酐数据库", "en": "🧪 Dianhydride Database"},
    "home_diamine_db": {"zh": "🧬 二胺数据库", "en": "🧬 Diamine Database"},
    "home_name_col": {"zh": "名称", "en": "Name"},
    "home_combinations": {
        "zh": "种二酐-二胺组合等待预测",
        "en": "dianhydride-diamine combinations await prediction"
    },
    "home_explore_possibilities": {
        "zh": "探索聚酰亚胺材料的无限可能",
        "en": "Explore the Infinite Possibilities of Polyimide Materials"
    },
    
    # === 使用说明 ===
    "help_title": {"zh": "📖 使用说明", "en": "📖 User Guide"},
    "help_subtitle": {
        "zh": "全面了解 PI-SCREEN 系统的使用方法",
        "en": "Comprehensive guide to using the PI-SCREEN system"
    },
    "help_overview_title": {"zh": "系统概述", "en": "System Overview"},
    "help_overview": {
        "zh": """PI-SCREEN 是一个基于人工智能的聚酰亚胺（PI）材料性能预测与高通量筛选系统。系统整合了文献挖掘、数据提取、分子描述符计算、机器学习建模和高通量虚拟筛选等全流程功能，旨在加速新型聚酰亚胺材料的研发。""",
        "en": """PI-SCREEN is an AI-powered polyimide (PI) material performance prediction and high-throughput screening system. It integrates the full pipeline of literature mining, data extraction, molecular descriptor calculation, machine learning modeling, and high-throughput virtual screening to accelerate the development of novel polyimide materials."""
    },
    "help_workflow_title": {"zh": "工作流程", "en": "Workflow"},
    "help_workflow": {
        "zh": """系统推荐的标准工作流程如下：

**Step 1: 文献下载** → 从学术数据库检索并下载 PI 相关文献 PDF
**Step 2: 文献评分** → AI 多评委系统对文献进行相关性评分和筛选
**Step 3: 数据提取** → 从高评分文献中自动提取结构与性能数据
**Step 4: 描述符计算** → 基于分子结构计算理化描述符
**Step 5: 模型训练** → 使用提取数据训练 ML 预测模型
**Step 6: 高通量筛选** → 利用模型对大量二酐-二胺组合进行性能预测""",
        "en": """The recommended standard workflow is:

**Step 1: Literature Download** → Search and download PI-related literature PDFs from academic databases
**Step 2: Literature Scoring** → AI multi-reviewer system scores and screens literature relevance
**Step 3: Data Extraction** → Automatically extract structure and property data from high-scoring papers
**Step 4: Descriptor Calculation** → Compute physicochemical descriptors from molecular structures
**Step 5: Model Training** → Train ML prediction models using extracted data
**Step 6: HTS Screening** → Predict performance of large dianhydride-diamine combinations using trained models"""
    },
    "help_modules_title": {"zh": "模块详细说明", "en": "Module Details"},
    "help_m_scoring": {
        "zh": """### 📚 文献评分模块
- **功能**: 使用 10 个 AI 评委并行评估文献相关性
- **输入**: 下载的文献 PDF 文件
- **输出**: 每篇文献的综合评分和排序
- **参数**: 可自定义评委数量、评分维度和阈值

使用步骤：
1. 进入「文献评分」模块
2. 确认文献目录中有 PDF 文件
3. 配置评分参数（评委数量、评分标准等）
4. 点击「开始评分」启动评估流程
5. 查看评分结果和文献排名""",
        "en": """### 📚 Literature Scoring Module
- **Function**: Use 10 AI reviewers to evaluate literature relevance in parallel
- **Input**: Downloaded literature PDF files
- **Output**: Comprehensive scores and rankings for each paper
- **Parameters**: Customizable reviewer count, scoring dimensions, and thresholds

Usage steps:
1. Enter the "Literature Scoring" module
2. Confirm PDF files exist in the paper directory
3. Configure scoring parameters (reviewer count, criteria, etc.)
4. Click "Start Scoring" to begin evaluation
5. Review scoring results and paper rankings"""
    },
    "help_m_download": {
        "zh": """### 📥 文献下载模块
- **功能**: 从学术数据库自动检索和下载文献
- **输入**: 搜索关键词、数据库配置
- **输出**: 文献 PDF 文件

使用步骤：
1. 进入「文献下载」模块
2. 设置搜索关键词（如 polyimide, dielectric, thermal stability 等）
3. 配置数据库源和下载数量
4. 点击「开始下载」
5. 下载完成后在「文献评分」模块中进行筛选""",
        "en": """### 📥 Literature Download Module
- **Function**: Automatically search and download literature from academic databases
- **Input**: Search keywords, database configuration
- **Output**: Literature PDF files

Usage steps:
1. Enter the "Literature Download" module
2. Set search keywords (e.g., polyimide, dielectric, thermal stability, etc.)
3. Configure database sources and download count
4. Click "Start Download"
5. After downloading, use "Literature Scoring" module to screen"""
    },
    "help_m_extraction": {
        "zh": """### 🔬 数据提取模块
- **功能**: 从 PDF 文献中自动提取 PI 结构与性能数据
- **输入**: 高评分的文献 PDF
- **输出**: CSV 格式的结构化数据

使用步骤：
1. 进入「数据提取」模块
2. 选择需要提取的文献
3. 配置提取模板和目标属性
4. 点击「开始提取」
5. 导出提取结果为 CSV 文件""",
        "en": """### 🔬 Data Extraction Module
- **Function**: Automatically extract PI structure and property data from PDF literature
- **Input**: High-scoring literature PDFs
- **Output**: Structured data in CSV format

Usage steps:
1. Enter the "Data Extraction" module
2. Select papers for extraction
3. Configure extraction templates and target properties
4. Click "Start Extraction"
5. Export extraction results as CSV files"""
    },
    "help_m_descriptors": {
        "zh": """### 🧪 描述符计算模块
- **功能**: 基于分子 SMILES 结构计算理化描述符
- **输入**: 分子结构数据（SMILES 格式）
- **输出**: 描述符矩阵
- **依赖**: RDKit 化学信息学库

使用步骤：
1. 进入「描述符计算」模块
2. 导入或选择分子结构数据
3. 选择需要计算的描述符类型
4. 点击「开始计算」
5. 计算完成后数据自动保存""",
        "en": """### 🧪 Descriptor Calculation Module
- **Function**: Compute physicochemical descriptors from molecular SMILES structures
- **Input**: Molecular structure data (SMILES format)
- **Output**: Descriptor matrix
- **Dependency**: RDKit cheminformatics library

Usage steps:
1. Enter the "Descriptor Calculation" module
2. Import or select molecular structure data
3. Choose descriptor types to calculate
4. Click "Start Calculation"
5. Data is automatically saved after calculation"""
    },
    "help_m_training": {
        "zh": """### 🤖 模型训练模块
- **功能**: 使用多种 ML 算法训练性能预测模型
- **输入**: 描述符矩阵 + 性能标签数据
- **输出**: 训练好的模型文件（.pkl）
- **支持算法**: RandomForest, GradientBoosting, SVR, MLP, Ridge, LinearRegression

使用步骤：
1. 进入「模型训练」模块
2. 加载训练数据（描述符 + 性能标签）
3. 选择目标属性和 ML 算法
4. 配置交叉验证参数
5. 点击「开始训练」
6. 查看训练指标（R², RMSE, MAE）
7. 保存训练好的模型""",
        "en": """### 🤖 Model Training Module
- **Function**: Train performance prediction models using multiple ML algorithms
- **Input**: Descriptor matrix + performance label data
- **Output**: Trained model files (.pkl)
- **Supported Algorithms**: RandomForest, GradientBoosting, SVR, MLP, Ridge, LinearRegression

Usage steps:
1. Enter the "Model Training" module
2. Load training data (descriptors + performance labels)
3. Select target properties and ML algorithms
4. Configure cross-validation parameters
5. Click "Start Training"
6. Review training metrics (R², RMSE, MAE)
7. Save the trained model"""
    },
    "help_m_hts": {
        "zh": """### 🔍 高通量筛选模块
- **功能**: 对二酐-二胺组合进行大规模性能预测
- **输入**: 训练好的模型 + 分子库
- **输出**: 预测结果排名和可视化

使用步骤：
1. 进入「高通量筛选」模块
2. 选择已训练好的预测模型
3. 配置筛选条件和目标性能
4. 点击「开始筛选」
5. 查看预测结果排名
6. 导出 Top-N 候选材料""",
        "en": """### 🔍 High-Throughput Screening Module
- **Function**: Large-scale performance prediction for dianhydride-diamine combinations
- **Input**: Trained model + molecular library
- **Output**: Prediction rankings and visualizations

Usage steps:
1. Enter the "HTS Screening" module
2. Select a trained prediction model
3. Configure screening criteria and target performance
4. Click "Start Screening"
5. Review prediction rankings
6. Export Top-N candidate materials"""
    },
    "help_tips_title": {"zh": "使用技巧", "en": "Tips & Best Practices"},
    "help_tips": {
        "zh": """1. **建议按流程执行**: 从文献下载开始，逐步完成各步骤
2. **定期备份数据**: 训练好的模型和提取的数据是核心资产
3. **RDKit 必需**: 描述符计算和高通量筛选依赖 RDKit，请确保安装
4. **文献质量**: 输入文献的质量直接影响最终预测结果
5. **参数调优**: 可根据需要调整各模块的参数以获得更好的效果""",
        "en": """1. **Follow the workflow**: Start from literature download and proceed step by step
2. **Backup regularly**: Trained models and extracted data are core assets
3. **RDKit required**: Descriptor calculation and HTS depend on RDKit — ensure it's installed
4. **Literature quality**: Input literature quality directly impacts final prediction results
5. **Parameter tuning**: Adjust parameters in each module for better results"""
    },
    "help_faq_title": {"zh": "常见问题", "en": "FAQ"},
    "help_faq": {
        "zh": """**Q: 如何安装 RDKit？**
A: 运行 `pip install rdkit` 或使用 conda: `conda install -c conda-forge rdkit`

**Q: 数据文件应该放在哪里？**
A: PDF 放在 `data/paper/`，CSV 数据在 `data/`，模型在 `models/`

**Q: 支持哪些 ML 算法？**
A: 目前支持 RandomForest、GradientBoosting、SVR、MLP Neural Network、Ridge 和 LinearRegression

**Q: 可以自定义二酐/二胺分子库吗？**
A: 可以，在系统设置中添加 SMILES 格式的新分子""",
        "en": """**Q: How to install RDKit?**
A: Run `pip install rdkit` or use conda: `conda install -c conda-forge rdkit`

**Q: Where should data files be placed?**
A: PDFs in `data/paper/`, CSV data in `data/`, models in `models/`

**Q: Which ML algorithms are supported?**
A: Currently supports RandomForest, GradientBoosting, SVR, MLP Neural Network, Ridge, and LinearRegression

**Q: Can I customize the dianhydride/diamine molecular library?**
A: Yes, add new molecules in SMILES format through system settings"""
    },
    
    # === 语言切换 ===
    "lang_label": {"zh": "🌐 语言 / Language", "en": "🌐 语言 / Language"},
    "lang_zh": {"zh": "🇨🇳 中文", "en": "🇨🇳 Chinese"},
    "lang_en": {"zh": "🇺🇸 English", "en": "🇺🇸 English"},
}


def t(key: str, lang: str = "zh") -> str:
    """获取翻译文本"""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key  # 返回 key 本身作为 fallback
    return entry.get(lang, entry.get("zh", key))


def get_page_names(lang: str) -> list:
    """获取导航页面名称列表"""
    keys = [
        "nav_home", "nav_scoring", "nav_download", "nav_extraction",
        "nav_descriptors", "nav_training", "nav_hts", "nav_settings", "nav_help"
    ]
    return [t(k, lang) for k in keys]


def get_page_key(page_name: str, lang: str) -> str:
    """根据页面显示名称返回内部 key"""
    keys = [
        "nav_home", "nav_scoring", "nav_download", "nav_extraction",
        "nav_descriptors", "nav_training", "nav_hts", "nav_settings", "nav_help"
    ]
    for k in keys:
        if t(k, lang) == page_name:
            return k
    return "nav_home"
