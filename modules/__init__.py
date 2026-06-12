# PI-SCREEN 业务模块 — 懒加载导入

import importlib

__all__ = [
    'LiteratureScorer',
    'LiteratureDownloader',
    'DataExtractor',
    'DescriptorCalculator',
    'ModelTrainer',
    'HighThroughputScreener',
]

_module_map = {
    'LiteratureScorer': '.scoring_module',
    'LiteratureDownloader': '.download_module',
    'DataExtractor': '.extraction_module',
    'DescriptorCalculator': '.descriptor_module',
    'ModelTrainer': '.training_module',
    'HighThroughputScreener': '.hts_module',
}


def __getattr__(name):
    """仅在实际使用时才导入子模块，避免启动时因可选依赖缺失而崩溃"""
    if name in _module_map:
        mod = importlib.import_module(_module_map[name], __package__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")