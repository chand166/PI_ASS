#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PI-SCREEN 聚酰亚胺性能预测系统 - 网页版 V2
基于Streamlit框架 + Corporate Trust设计风格（升级版）
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import time
import json
import sys
import os
import threading

# 将 src 目录加入 path 以便导入 i18n
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from i18n import t, get_page_names, get_page_key

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="PI-SCREEN | 聚酰亚胺性能预测",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== Corporate Trust 设计风格 V2 ====================
st.markdown("""
<style>
    /* 导入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    /* 全局背景 */
    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
        font-family: 'Plus Jakarta Sans', 'Segoe UI', 'PingFang SC', sans-serif;
    }
    
    /* 侧边栏 - 玻璃拟态效果 */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95);
        border-right: 1px solid rgba(79, 70, 229, 0.1);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        padding: 12px 16px;
        border-radius: 12px;
        transition: all 0.2s ease;
        margin: 2px 0;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(79, 70, 229, 0.08);
    }
    
    /* 选中项 - 整个label容器的浅紫色渐变 */
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.10) 0%, rgba(124, 58, 237, 0.08) 50%, rgba(139, 92, 246, 0.06) 100%);
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.12), inset 0 0 0 1px rgba(79, 70, 229, 0.15);
    }
    
    [data-testid="stSidebar"] .stRadio label:has(input:checked) > div {
        color: #4F46E5;
        font-weight: 600;
    }
    
    /* 隐藏原生radio圆点 */
    [data-testid="stSidebar"] .stRadio label input[type="radio"] {
        accent-color: #4F46E5;
    }
    
    /* 标题系统 */
    h1 {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #6366F1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 3rem !important;
        letter-spacing: -0.02em;
        line-height: 1.1 !important;
    }
    
    h2 {
        color: #0F172A !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        letter-spacing: -0.01em;
    }
    
    h3 {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 1.25rem !important;
    }
    
    /* 主按钮 - 渐变悬浮效果 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        padding: 14px 32px;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3), 
                    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button[kind="primary"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button[kind="primary"]:hover::before {
        left: 100%;
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.4),
                    0 0 0 1px rgba(255, 255, 255, 0.1) inset;
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
    }
    
    /* 次级按钮 */
    .stButton > button:not([kind="primary"]) {
        background: rgba(255, 255, 255, 0.8);
        color: #4F46E5;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        font-weight: 500;
        transition: all 0.2s;
        backdrop-filter: blur(10px);
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background: rgba(79, 70, 229, 0.05);
        border-color: #4F46E5;
        color: #4F46E5;
    }
    
    /* 卡片系统 - 玻璃拟态 */
    .card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.08),
                    0 1px 3px rgba(0, 0, 0, 0.05);
        margin: 16px 0;
        border: 1px solid rgba(79, 70, 229, 0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .card:hover {
        box-shadow: 0 12px 40px rgba(79, 70, 229, 0.15),
                    0 4px 12px rgba(0, 0, 0, 0.05);
        transform: translateY(-4px);
        border-color: rgba(79, 70, 229, 0.15);
    }
    
    /* Hero卡片 - 3D透视效果 */
    .hero-card {
        perspective: 2000px;
        margin: 24px 0;
    }
    
    .hero-card-content {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(79, 70, 229, 0.1);
        box-shadow: 0 20px 60px rgba(79, 70, 229, 0.15),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        transform: rotateX(3deg) rotateY(-8deg);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }
    
    .hero-card-content::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(79, 70, 229, 0.03) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .hero-card:hover .hero-card-content {
        transform: rotateX(1deg) rotateY(-4deg) translateY(-8px);
        box-shadow: 0 30px 80px rgba(79, 70, 229, 0.2);
    }
    
    /* Feature卡片 - 交替3D效果 */
    .feature-card-left {
        transform: perspective(1000px) rotateY(3deg);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .feature-card-right {
        transform: perspective(1000px) rotateY(-3deg);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .feature-card-left:hover,
    .feature-card-right:hover {
        transform: perspective(1000px) rotateY(0deg) translateY(-6px);
    }
    
    /* 图标容器 - 渐变发光 */
    .icon-container {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #DDD6FE 100%);
        border-radius: 16px;
        padding: 18px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.2),
                    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
        transition: all 0.3s;
    }
    
    .icon-container:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
    }
    
    .icon-gradient {
        font-size: 32px;
        filter: drop-shadow(0 2px 4px rgba(79, 70, 229, 0.2));
    }
    
    /* Stats卡片 - 数字发光效果 */
    .stat-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid rgba(79, 70, 229, 0.08);
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4F46E5, #7C3AED, #6366F1);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .stat-card:hover::before {
        opacity: 1;
    }
    
    .stat-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 40px rgba(79, 70, 229, 0.15);
    }
    
    .stat-number {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        letter-spacing: -0.02em;
    }
    
    .stat-label {
        color: #64748B;
        font-weight: 600;
        font-size: 0.9rem;
        margin-top: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stat-type {
        color: #94A3B8;
        font-size: 0.75rem;
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Badge - 发光效果 */
    .badge-glow {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.75rem;
        box-shadow: 0 0 20px rgba(79, 70, 229, 0.4),
                    0 4px 10px rgba(79, 70, 229, 0.2);
        display: inline-block;
        letter-spacing: 0.02em;
    }
    
    /* 输入框 - 聚焦发光 */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1.5px solid #E2E8F0 !important;
        border-radius: 12px !important;
        transition: all 0.2s;
        font-size: 0.95rem;
        outline: none !important;
        box-shadow: none !important;
    }

    /* 聚焦时仅变边框色，无多余光晕 */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #4F46E5 !important;
    }

    /* 消除所有父级容器的多余边框/阴影 */
    .stTextInput div, .stTextArea div,
    .stTextInput [data-testid], .stTextArea [data-testid] {
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* 全局禁用 Streamlit 默认的焦点环 */
    *:focus {
        outline: none !important;
    }
    
    /* 进度条 - 渐变动画 */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #4F46E5, #6366F1, #7C3AED, #4F46E5) !important;
        background-size: 200% 100% !important;
        animation: gradient-shift 2s linear infinite;
        border-radius: 999px;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    
    /* 标签页 - 现代风格 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(248, 250, 252, 0.8);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid rgba(79, 70, 229, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        font-weight: 500;
        color: #64748B;
        transition: all 0.2s;
        padding: 10px 20px;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(79, 70, 229, 0.05);
        color: #4F46E5;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    }
    
    /* 提示框 - 现代化 */
    .stSuccess {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 1px solid #6EE7B7;
        border-radius: 16px;
        color: #064E3B;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 1px solid #FCD34D;
        border-radius: 16px;
        color: #92400E;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.1);
    }
    
    .stError {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 1px solid #FCA5A5;
        border-radius: 16px;
        color: #991B1B;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
    }
    
    .stInfo {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border: 1px solid #93C5FD;
        border-radius: 16px;
        color: #1E40AF;
        padding: 16px 20px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }
    
    /* 表格 - 现代风格 */
    .stDataFrame {
        border-radius: 16px;
        border: 1px solid rgba(79, 70, 229, 0.08);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        overflow: hidden;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        font-weight: 600;
        color: #0F172A;
        border-bottom: 2px solid #E2E8F0;
    }
    
    /* 下载按钮 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.25);
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
    }
    
    /* 分割线 */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #E2E8F0, transparent);
        margin: 32px 0;
    }
    
    /* 数字输入框 */
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
    }
    
    /* 滑块 - 渐变轨道 */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #E0E7FF, #DDD6FE);
        border-radius: 999px;
    }
    
    .stSlider > div > div > span {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
    }
    
    /* 多选框 */
    .stMultiSelect > div > div {
        border-color: #E2E8F0 !important;
        border-radius: 12px !important;
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stMultiSelect > div > div:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1) !important;
    }
    
    /* 展开器 - 现代风格 */
    .stExpander {
        border: 1px solid rgba(79, 70, 229, 0.08);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
    }
    
    .stExpander > div > div > div:first-child {
        font-weight: 600;
        color: #0F172A;
    }
    
    /* 文件上传器 */
    .stFileUploader > div > div {
        border: 2px dashed #E2E8F0;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.5);
        transition: all 0.2s;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #4F46E5;
        background: rgba(79, 70, 229, 0.02);
    }
    
    /* 悬浮提示框 - Tooltip样式 */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: #fff;
        text-align: center;
        border-radius: 12px;
        padding: 12px 16px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* 动画背景装饰 */
    .bg-decoration {
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        filter: blur(100px);
        opacity: 0.15;
        pointer-events: none;
        z-index: 0;
    }
    
    .bg-decoration-1 {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        top: -200px;
        right: -100px;
        animation: float 20s ease-in-out infinite;
    }
    
    .bg-decoration-2 {
        background: linear-gradient(135deg, #7C3AED, #6366F1);
        bottom: -200px;
        left: -100px;
        animation: float 25s ease-in-out infinite reverse;
    }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -30px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
    }
    
    /* 步骤指示器 */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 24px 0;
    }
    
    .step {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.3s;
    }
    
    .step-active {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
    }
    
    .step-completed {
        background: #10B981;
        color: white;
    }
    
    .step-pending {
        background: #E2E8F0;
        color: #64748B;
    }
    
    .step-line {
        flex: 1;
        height: 2px;
        background: #E2E8F0;
        border-radius: 1px;
    }
    
    .step-line-active {
        background: linear-gradient(90deg, #4F46E5, #7C3AED);
    }
    
    /* 数据卡片网格 */
    .data-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin: 24px 0;
    }
    
    .data-item {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(79, 70, 229, 0.08);
        transition: all 0.2s;
    }
    
    .data-item:hover {
        border-color: rgba(79, 70, 229, 0.2);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.1);
    }
    
    .data-label {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    
    .data-value {
        color: #0F172A;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* 响应式调整 */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        .hero-card-content {
            transform: none;
            padding: 24px;
        }
        
        .stat-number {
            font-size: 2rem;
        }
        
        .card {
            padding: 20px;
        }
    }
    
    /* 右上角控制栏 - 固定在顶部右侧 */
    .top-right-bar {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 4px 0;
    }
    
    /* 语言选择器样式 */
    [data-testid="stVerticalBlock"] > div:first-child > div > div > [data-testid="stSelectbox"] > div {
        min-width: 130px;
    }
    
    /* 顶部控制行紧凑化 */
    [data-testid="column"] > div > div > [data-testid="stSelectbox"] label,
    [data-testid="column"] > div > div > [data-testid="stButton"] button {
        border-radius: 10px;
        font-size: 0.85rem;
    }
    
    [data-testid="column"] > div > div > [data-testid="stButton"] button {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border: none;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(79, 70, 229, 0.25);
        transition: all 0.2s;
    }
    
    [data-testid="column"] > div > div > [data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
    }
</style>

<!-- 背景装饰 -->
<div class="bg-decoration bg-decoration-1"></div>
<div class="bg-decoration bg-decoration-2"></div>
""", unsafe_allow_html=True)

# ==================== 配置类 ====================
class Config:
    BASE_DIR = Path("D:/PI_ASS")
    DATA_DIR = BASE_DIR / "data"
    PAPER_DIR = BASE_DIR / "data" / "paper"
    MODEL_DIR = BASE_DIR / "models"
    OUTPUT_DIR = BASE_DIR / "output"
    TEMP_DIR = BASE_DIR / "temp"
    
    for d in [BASE_DIR, DATA_DIR, PAPER_DIR, MODEL_DIR, OUTPUT_DIR, TEMP_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    
    # API配置
    MINIMAX_API = "http://10.2.39.3:1025/v1"
    MINIMAX_MODEL = "Kimi-K2.5"
    DEFAULT_API_KEY = "EMPTY"
    
    # 默认参数
    DEFAULT_EXPERT_COUNT = 10
    DEFAULT_SCORE_THRESHOLD = 0.8
    DEFAULT_ITERATIONS = 500
    DEFAULT_PARALLEL_WORKERS = 4

    # 二酐数据库 (与 hts_module.py 保持一致)
    DIANHYDRIDES = {
        'PMDA': 'O=C1C(=O)c2ccccc2C1=O',
        'BPDA': 'O=C1C(=O)c2ccc3c2C3=O',
        'ODPA': 'O=C1C(=O)c2ccc(Oc3ccc(C(=O)O5)cc3)cc2C1=O',
        'BTDA': 'O=C1C(=O)c2ccc3c2C(=O)c4ccc(cc4C3=O)C(=O)O1',
        '6FDA': 'O=C1C(=O)C(F)(F)C(F)(F)C(F)(F)C1=O',
    }

    # 二胺数据库 (与 hts_module.py 保持一致)
    DIAMINES = {
        'ODA': 'COc1ccc(N)cc1OC',
        'MDA': 'Cc1ccc(N)cc1',
        'DDE': 'NCCNCCN',
        'm-PDA': 'Nc1cccc(N)c1',
        'p-PDA': 'Nc1ccc(N)cc1',
    }

    # 性能目标
    PERFORMANCE_TARGETS = [
        ('玻璃化转变温度 Tg', 'tg', '°C'),
        ('介电常数', 'dielectric', ''),
        ('介电损耗', 'dielectric_loss', ''),
        ('击穿电压', 'breakdown_voltage', 'kV/mm'),
        ('透过率', 'transmittance', '%'),
    ]
    
    # 筛选标准提示词
    DEFAULT_SCORING_PROMPT = """请作为聚酰亚胺材料领域专家，评估以下文献与你研究领域的相关性。

【筛选标准】
1. 必须是对聚酰亚胺分子结构的改进（使用二酐和二胺单体合成），而非共混掺杂体系
2. 不能出现无机物等非二酐和二胺结构
3. 研究领域必须是：半导体、光刻胶、取向、微电子领域
4. 着重关注材料的表征与性能：光学、热性能、电性能、力学性能
5. 排除气体传输/分离领域

请严格按照以下格式输出最终评分和评分依据：
最终评分：【0.XX】
评分依据：[简要说明评分原因]"""

    # 数据提取提示词
    DEFAULT_EXTRACTION_PROMPT = """以一个材料领域的专家身份，用严谨的态度来分析文献中的文字图片和表格，重点分析表格与图片，提取数据，将文件中所有的结构以及对应性能列举出来，不需要筛选，进行统计，找到缩写对应的全拼并将数据汇总为丨样品编号丨命名丨单体酸酐1英文全拼（例如4,4'-(Hexafluoroisopropylidene)diphthalic anhydride)要求不允许出现简写、括号等丨酸酐简写（例如PMDA）丨单体酸酐2英文全拼，要求不允许出现简写、括号等丨酸酐2简写（例如PMDA）丨单体二胺1英文全拼（例如4,4'-Oxydianiline）丨二胺简写（例如ODA）丨单体二胺2英文全拼（例如4,4'-Oxydianiline）丨二胺2简写（例如ODA）丨热分解温度 (Td5%, °C)丨玻璃化转变温度 (Tg, °C)丨热膨胀系数 (CTE, ppm·K⁻¹)丨截止波长 (λcutoff, nm)丨透光率 (T450nm, %)丨Tensile Strength丨Elongation at Break(%)丨a*丨b*丨L*丨Dielectric Constant丨dielectric loss丨YI丨来源文件(上传的pdf文件名不是文章题目) 这样的列标题表格中，严格控制为24列表格，将文件中所有的结构以及对应性能列举出来，无数据则用短划线表示，不允许出现缩写如（PMDA等），缩写都可以在文中找到，严格按照要求，每一格一个数据，最严格格式要求，总合在表格中，只输出表格内容，不输出思考过程，在全拼和简写单元格不允许出现中文，仔细检查确保相应列标题对应的数据与原文一致，数据自动分行，确保所有样品都被提及"""


# ==================== 辅助函数 ====================


def _smart_read_excel(file_obj, scan_rows: int = 30):
    """智能读取Excel，自动扫描并定位真正的表头行"""
    _TITLE_KW = ['Title', '标题', 'Article Title', 'Article title', 'article title']
    _ABSTRACT_KW = ['Abstract', '摘要', 'abstract']
    raw = pd.read_excel(file_obj, header=None, nrows=scan_rows)
    header_row = None
    for i in range(len(raw)):
        row_strs = [str(v).strip() for v in raw.iloc[i].tolist()]
        has_title = any(any(k.lower() == v.lower() for k in _TITLE_KW) for v in row_strs)
        has_abstract = any(any(k.lower() == v.lower() for k in _ABSTRACT_KW) for v in row_strs)
        if has_title and has_abstract:
            header_row = i
            break
    file_obj.seek(0)
    if header_row is not None:
        df = pd.read_excel(file_obj, header=header_row)
        df = df.dropna(how='all').reset_index(drop=True)
        return df
    return pd.read_excel(file_obj)
def init_session_state():
    """初始化会话状态"""
    if 'scoring_results' not in st.session_state:
        st.session_state.scoring_results = None
    if 'scoring_df' not in st.session_state:
        st.session_state.scoring_df = None
    if 'scoring_title_col' not in st.session_state:
        st.session_state.scoring_title_col = None
    if 'scoring_abstract_col' not in st.session_state:
        st.session_state.scoring_abstract_col = None
    if 'scoring_doi_col' not in st.session_state:
        st.session_state.scoring_doi_col = None
    if 'scoring_show_input' not in st.session_state:
        st.session_state.scoring_show_input = False
    if 'scoring_show_output' not in st.session_state:
        st.session_state.scoring_show_output = False
    if 'scoring_output_folder' not in st.session_state:
        st.session_state.scoring_output_folder = str(Config.OUTPUT_DIR)
    if 'scoring_output_filename' not in st.session_state:
        st.session_state.scoring_output_filename = "scoring_results.xlsx"
    if 'download_scored_df' not in st.session_state:
        st.session_state.download_scored_df = None
    if 'download_thread' not in st.session_state:
        st.session_state.download_thread = None
    if 'download_cancel' not in st.session_state:
        st.session_state.download_cancel = None
    if 'extraction_results' not in st.session_state:
        st.session_state.extraction_results = None
    if 'training_results' not in st.session_state:
        st.session_state.training_results = None
    if 'hts_results' not in st.session_state:
        st.session_state.hts_results = None
    if 'scoring_pause' not in st.session_state:
        st.session_state.scoring_pause = False

    if 'lang' not in st.session_state:
        st.session_state.lang = 'zh'
    if 'page' not in st.session_state:
        st.session_state.page = get_page_names('zh')[0]
    if 'show_help_dialog' not in st.session_state:
        st.session_state.show_help_dialog = False



@st.cache_resource
def _get_extraction_state():
    """持久化提取共享状态"""
    return {"results": None, "progress": {}, "thread": None, "cancel": None}

_EXTRACTION_STATE = _get_extraction_state()


@st.cache_resource
def _get_smiles_state():
    """持久化SMILES转化共享状态"""
    return {"results": None, "progress": {}, "thread": None, "cancel": None}

_SMILES_STATE = _get_smiles_state()


@st.cache_resource
def _get_descriptor_state():
    """持久化描述符计算共享状态"""
    return {"results": None, "progress": {}, "thread": None, "cancel": None}

_DESCRIPTOR_STATE = _get_descriptor_state()



@st.cache_resource
def _get_download_state():
    return {'results': None, 'progress': {}, 'download_results': None}
_DOWNLOAD_STATE = _get_download_state()


@st.cache_resource
def _get_scoring_state():
    """持久化评分共享状态。
    thread/cancel 必须放在这里（cache_resource 跨 rerun 持久），
    不能用模块级全局变量——否则每次 Streamlit rerun 重新执行脚本顶层，
    会把 _scoring_thread_ref 重置为 None，导致 UI 检测不到正在运行的线程，
    表现为"点了开始评分没反应"。
    """
    return {'results': None, 'progress': {}, 'error': None,
            'thread': None, 'cancel': None}

_SCORING_STATE = _get_scoring_state()

def check_rdkit():
    """检查RDKit是否可用"""
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, AllChem
        return True
    except ImportError:
        return False


def create_tooltip(text, tooltip_text):
    """创建悬浮提示"""
    return f'''
    <div class="tooltip">
        {text}
        <span class="tooltiptext">{tooltip_text}</span>
    </div>
    '''


# ==================== 顶部控制栏 ====================
def create_top_right_controls():
    """语言切换 + 使用说明：Streamlit 原生按钮 + CSS 固定定位到 header 区域"""
    lang = st.session_state.get('lang', 'zh')
    page = st.session_state.get('page', '')
    page_key = get_page_key(page, lang) if page else 'nav_home'

    # 语言按钮文本：不用缩写
    lang_btn_text = 'English' if lang == 'zh' else '中文'
    help_btn_text = '📖 使用说明' if lang == 'zh' else '📖 User Guide'

    # CSS: 固定定位到 header Deploy 按钮左侧
    st.markdown("""
    <style>
    /* 固定定位容器 */
    div[data-testid="stVerticalBlock"]:has(> div > div > button[data-testid="stBaseButton-secondary"]) {
        /* fallback */
    }
    div[data-testid="element-container"]:has(> div.st-key-top_ctrl) {
        position: fixed;
        top: 6px;
        right: 140px;
        z-index: 999;
    }
    /* 让按钮看起来和 Deploy 一致 */
    div.st-key-top_ctrl button {
        display: inline-flex !important;
        align-items: center;
        padding: 0 12px !important;
        border-radius: 8px !important;
        min-height: 28px !important;
        border: none !important;
        background: transparent !important;
        color: rgb(49, 51, 63) !important;
        font-size: 14px !important;
        line-height: 28px !important;
        cursor: pointer;
        white-space: nowrap;
    }
    div.st-key-top_ctrl button:hover {
        background: rgba(49, 51, 63, 0.04) !important;
    }
    div.st-key-top_ctrl [data-testid="column"] {
        flex: none !important;
        width: auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 用 st.container + key 来标记（CSS 通过 key class 定位）
    with st.container(key='top_ctrl'):
        c1, c2, _ = st.columns([0.08, 0.12, 0.8])
        with c1:
            if st.button(lang_btn_text, key='top_lang_btn'):
                st.session_state.lang = 'en' if lang == 'zh' else 'zh'
                st.rerun()
        with c2:
            if st.button(help_btn_text, key='top_help_btn'):
                st.session_state.show_help_dialog = not st.session_state.get('show_help_dialog', False)
                st.rerun()

    # 使用说明 expander
    if st.session_state.get('show_help_dialog', False):
        with st.expander('📖 ' + ('使用说明' if lang == 'zh' else 'User Guide'), expanded=True):
            col_close, _ = st.columns([1, 8])
            with col_close:
                if st.button('✖', key='close_help_expander'):
                    st.session_state.show_help_dialog = False
                    st.rerun()

            help_key_map = {
                'nav_home': 'help_overview',
                'nav_scoring': 'help_m_scoring',
                'nav_download': 'help_m_download',
                'nav_extraction': 'help_m_extraction',
                'nav_smiles': 'help_m_smiles',
                'nav_descriptors': 'help_m_descriptors',
                'nav_training': 'help_m_training',
                'nav_hts': 'help_m_hts',
                'nav_settings': 'help_tips',
                'nav_help': 'help_faq'
            }

            help_key = help_key_map.get(page_key, 'help_overview')
            st.markdown(t(help_key, lang))
            st.markdown('---')
            st.markdown(f"**{t('help_workflow_title', lang)}**")
            st.markdown(t('help_workflow', lang))
            st.markdown('---')
            st.markdown(f"**{t('help_faq_title', lang)}**")
            st.markdown(t('help_faq', lang))





# ==================== 侧边栏 ====================
def create_sidebar():
    """创建侧边栏导航 - 高端玻璃拟态风格 + i18n"""
    lang = st.session_state.get('lang', 'zh')
    
    # Logo区域
    st.sidebar.markdown(f'''
<div style="padding: 20px 0; text-align: center;">
<div style="
background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
width: 60px;
height: 60px;
border-radius: 16px;
display: inline-flex;
align-items: center;
justify-content: center;
font-size: 28px;
box-shadow: 0 8px 30px rgba(79, 70, 229, 0.3);
margin-bottom: 12px;
">
🧪
</div>
<h2 style="margin: 0; font-size: 1.5rem; font-weight: 800; 
background: linear-gradient(135deg, #0F172A 0%, #4F46E5 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;">
PI-SCREEN
</h2>
<p style="color: #64748B; font-size: 0.8rem; margin-top: 4px;">
{t('app_subtitle', lang)}
</p>
</div>
    ''', unsafe_allow_html=True)
    
    # RDKit状态指示器
    if check_rdkit():
        st.sidebar.markdown(f'''
<div style="
background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
border: 1px solid #6EE7B7;
border-radius: 12px;
padding: 12px 16px;
margin-bottom: 16px;
display: flex;
align-items: center;
gap: 10px;
">
<span style="font-size: 1.2rem;">✅</span>
<div>
<div style="font-weight: 600; color: #064E3B; font-size: 0.85rem;">{t('rdkit_ready', lang)}</div>
<div style="color: #059669; font-size: 0.75rem;">{t('rdkit_running', lang)}</div>
</div>
        ''', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f'''
<div style="
background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
border: 1px solid #FCD34D;
border-radius: 12px;
padding: 12px 16px;
margin-bottom: 16px;
display: flex;
align-items: center;
gap: 10px;
">
<span style="font-size: 1.2rem;">⚠️</span>
<div>
<div style="font-weight: 600; color: #92400E; font-size: 0.85rem;">{t('rdkit_not_installed', lang)}</div>
<div style="color: #B45309; font-size: 0.75rem;">{t('rdkit_install_hint', lang)}</div>
</div>
        ''', unsafe_allow_html=True)
    
    # 导航选项 (使用 i18n)
    pages = get_page_names(lang)
    
    page = st.sidebar.radio(
        t('sidebar_title', lang),
        pages,
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown(f'''
<hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #E2E8F0, transparent); margin: 24px 0;">
<div style="padding: 0 8px;">
<h4 style="color: #0F172A; font-size: 0.85rem; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em;">
{t('quick_links', lang)}
</h4>
    ''', unsafe_allow_html=True)
    
    # 快速链接按钮
    col1, col2 = st.sidebar.columns(2)
    
    project_label = t('btn_project', lang)
    data_label = t('btn_data', lang)
    model_label = t('btn_model', lang)
    output_label = t('btn_output', lang)
    
    with col1:
        if st.button(project_label, use_container_width=True):
            st.toast(f"Project: {Config.BASE_DIR}")
    
    with col2:
        if st.button(data_label, use_container_width=True):
            st.toast(f"Data: {Config.DATA_DIR}")
    
    col3, col4 = st.sidebar.columns(2)
    
    with col3:
        if st.button(model_label, use_container_width=True):
            st.toast(f"Models: {Config.MODEL_DIR}")
    
    with col4:
        if st.button(output_label, use_container_width=True):
            st.toast(f"Output: {Config.OUTPUT_DIR}")
    
    # 底部信息
    st.sidebar.markdown('''
<div style="
position: fixed;
bottom: 20px;
left: 20px;
right: 20px;
background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
border: 1px solid #E2E8F0;
border-radius: 12px;
padding: 12px 16px;
text-align: center;
">
<div style="color: #64748B; font-size: 0.75rem;">
PI-SCREEN v2.0
</div>
<div style="color: #94A3B8; font-size: 0.7rem; margin-top: 2px;">
Powered by AI
</div>
    ''', unsafe_allow_html=True)
    
    return page


# ==================== 首页 ====================
def create_home_page():
    """首页 - 高端Corporate Trust设计风格 + i18n"""
    lang = st.session_state.get('lang', 'zh')
    
    # Hero Section with 3D Card
    st.markdown(
        '<div class="hero-card">'
        '<div class="hero-card-content">'
        '<div style="display:flex;align-items:center;gap:20px;margin-bottom:24px;">'
        '<div class="icon-container"><span class="icon-gradient">🧪</span></div>'
        '<div>'
        '<div style="font-size:3rem;margin:0;line-height:1;font-weight:800;'
        'background:linear-gradient(135deg,#4F46E5 0%,#7C3AED 50%,#6366F1 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">PI-SCREEN</div>'
        f'<div style="color:#64748B;font-size:1.1rem;margin:8px 0 0 0;font-weight:500;">{t("app_full_name", lang)}</div>'
        '</div></div>'
        f'<div style="margin-bottom:24px;"><span class="badge-glow">✨ {t("powered_by_ai", lang)}</span></div>'
        '<div style="background:linear-gradient(135deg,rgba(79,70,229,0.05) 0%,rgba(124,58,237,0.05) 100%);'
        'border-radius:16px;padding:24px;border:1px solid rgba(79,70,229,0.1);">'
        f'<div style="color:#0F172A;font-weight:600;margin-bottom:20px;font-size:1rem;">{t("home_core_capabilities", lang)}</div>'
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;">'
        '<div style="text-align:center;padding:16px;background:rgba(255,255,255,0.5);border-radius:12px;">'
        '<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#4F46E5 0%,#6366F1 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">10</div>'
        f'<div style="color:#64748B;font-size:0.85rem;font-weight:500;margin-top:4px;">{t("home_parallel_scoring", lang)}</div></div>'
        '<div style="text-align:center;padding:16px;background:rgba(255,255,255,0.5);border-radius:12px;">'
        '<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#7C3AED 0%,#A855F7 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">80+</div>'
        f'<div style="color:#64748B;font-size:0.85rem;font-weight:500;margin-top:4px;">{t("home_molecule_prediction", lang)}</div></div>'
        '<div style="text-align:center;padding:16px;background:rgba(255,255,255,0.5);border-radius:12px;">'
        '<div style="font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#6366F1 0%,#8B5CF6 100%);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">6</div>'
        f'<div style="color:#64748B;font-size:0.85rem;font-weight:500;margin-top:4px;">{t("home_core_modules", lang)}</div></div>'
        '</div></div></div></div>',
        unsafe_allow_html=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Feature Cards with 3D Effects
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 8px;'>{t('home_feature_title', lang)}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #64748B; margin-bottom: 32px;'>{t('home_feature_subtitle', lang)}</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    features = [
        ("📚", t('home_scoring_title', lang), t('home_scoring_desc', lang), "home_scoring", t('nav_scoring', lang), "left"),
        ("🔬", t('home_extraction_title', lang), t('home_extraction_desc', lang), "home_extraction", t('nav_extraction', lang), "right"),
        ("🔍", t('home_hts_title', lang), t('home_hts_desc', lang), "home_hts", t('nav_hts', lang), "left"),
    ]
    
    for i, (icon, title, desc, key, page_name, side) in enumerate(features):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="feature-card-{side}">
                <div class="card" style="position: relative; overflow: hidden; height: 100%;">
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100px; 
                         background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #DDD6FE 100%); 
                         opacity: 0.3;"></div>
                    <div style="position: relative; z-index: 1;">
                        <div class="icon-container" style="margin-bottom: 20px;">
                            <span class="icon-gradient">{icon}</span>
                        </div>
                        <h3 style="color: #0F172A; margin: 0 0 12px 0; font-size: 1.2rem;">{title}</h3>
                        <p style="color: #64748B; font-size: 0.9rem; line-height: 1.6; margin: 0;">{desc}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(t('home_enter_module', lang), key=key, use_container_width=True):
                st.session_state.nav_radio = page_name
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Stats Section with Glow Cards
    st.markdown(f"<h2 style='text-align: center; margin-bottom: 8px;'>{t('home_project_status', lang)}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #64748B; margin-bottom: 32px;'>{t('home_realtime_monitor', lang)}</p>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    stats = [
        (len(list(Config.PAPER_DIR.glob("*.pdf"))), t('home_paper_count', lang), "PDF"),
        (len(list(Config.DATA_DIR.glob("*.csv"))), t('home_data_files', lang), "CSV"),
        (len(list(Config.MODEL_DIR.glob("*.pkl"))), t('home_trained_models', lang), "PKL"),
        (len(list(Config.OUTPUT_DIR.glob("*"))), t('home_output_results', lang), "Files"),
    ]
    
    for i, (count, label, type_) in enumerate(stats):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{count}</div>
                <div class="stat-label">{label}</div>
                <div class="stat-type">{type_}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Database Preview with Gradient Headers
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 28px;
        box-shadow: 0 8px 30px rgba(79, 70, 229, 0.3);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.4rem; font-weight: 700;">{t('home_molecular_db', lang)}</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 0.9rem;">{t('home_molecular_db_sub', lang)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    name_col = t('home_name_col', lang)
    
    with col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 16px; padding: 24px; 
                    border: 1px solid rgba(79, 70, 229, 0.1); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);">
            <h3 style="color: #4F46E5; margin: 0 0 16px 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">🧪</span> {t('home_dianhydride_db', lang)}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        da_df = pd.DataFrame([
            {name_col: k, "SMILES": v[:35] + "..." if len(v) > 35 else v} 
            for k, v in Config.DIANHYDRIDES.items()
        ])
        st.dataframe(da_df, hide_index=True, use_container_width=True)
        
    with col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 16px; padding: 24px; 
                    border: 1px solid rgba(79, 70, 229, 0.1); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);">
            <h3 style="color: #7C3AED; margin: 0 0 16px 0; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2rem;">🧬</span> {t('home_diamine_db', lang)}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        di_df = pd.DataFrame([
            {name_col: k, "SMILES": v[:35] + "..." if len(v) > 35 else v} 
            for k, v in Config.DIAMINES.items()
        ])
        st.dataframe(di_df, hide_index=True, use_container_width=True)
    
    total_comb = len(Config.DIANHYDRIDES) * len(Config.DIAMINES)
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 50%, #DDD6FE 100%);
        padding: 28px;
        border-radius: 16px;
        border: 1px solid rgba(79, 70, 229, 0.15);
        margin-top: 28px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.1);
    ">
        <div style="
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">
            ✨ {total_comb} {t('home_combinations', lang)}
        </div>
        <div style="color: #64748B; margin-top: 8px; font-weight: 500;">{t('home_explore_possibilities', lang)}</div>
    </div>
    """, unsafe_allow_html=True)


# ==================== 文献评分 ====================
def create_scoring_page():
    """文献评分页面 - 可点击卡片 + 自动列识别 + 多评委评分"""
    lang = st.session_state.get('lang', 'zh')

    st.title("📚 文献评分")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>上传Excel文献数据，AI多评委自动评分筛选</p>", unsafe_allow_html=True)

    # === 两列可点击卡片 ===
    col1, col2 = st.columns(2)

    with col1:
        # 输入文件卡片（点击切换）
        btn_label = "📥 输入文件" if lang == 'zh' else "📥 Input File"
        if st.button(btn_label, key="toggle_input_card", use_container_width=True, type="secondary"):
            st.session_state.scoring_show_input = not st.session_state.scoring_show_input

        if st.session_state.scoring_show_input:
            input_file = st.file_uploader(
                "上传文献数据文件",
                type=['xlsx', 'xls', 'csv'],
                help="支持Excel（.xlsx/.xls）和CSV格式，自动识别标题/摘要/DOI列",
                label_visibility="collapsed"
            )

            if input_file is not None:
                # 读取文件
                try:
                    if input_file.name.endswith('.csv'):
                        df = pd.read_csv(input_file)
                    else:
                        df = _smart_read_excel(input_file)
                except Exception as e:
                    st.error(f"文件读取失败: {e}")
                    df = None

                if df is not None:
                    st.session_state.scoring_df = df

                    # 自动识别列名
                    title_col = abstract_col = doi_col = None
                    title_kw = ['Article Title', '标题', 'Title', 'article title', 'Article title']
                    abstract_kw = ['Abstract', '摘要', 'abstract']
                    doi_kw = ['DOI', 'doi', 'Doi']

                    for c in df.columns:
                        cs = str(c).strip()
                        if any(k.lower() == cs.lower() for k in title_kw):
                            title_col = c
                        if any(k.lower() == cs.lower() for k in abstract_kw):
                            abstract_col = c
                        if any(k.lower() == cs.lower() for k in doi_kw):
                            doi_col = c

                    st.session_state.scoring_title_col = title_col
                    st.session_state.scoring_abstract_col = abstract_col
                    st.session_state.scoring_doi_col = doi_col

                    st.info(f"📊 读取到 {len(df)} 条文献记录")

                    ci1, ci2, ci3 = st.columns([1, 1, 1])
                    with ci1:
                        if title_col:
                            st.success(f"✅ 标题: {title_col}")
                        else:
                            tc = st.selectbox("⚠️ 选择标题列", df.columns, key="sel_title")
                            st.session_state.scoring_title_col = tc
                    with ci2:
                        if abstract_col:
                            st.success(f"✅ 摘要: {abstract_col}")
                        else:
                            ac = st.selectbox("⚠️ 选择摘要列", df.columns, key="sel_abstract")
                            st.session_state.scoring_abstract_col = ac
                    with ci3:
                        if doi_col:
                            st.success(f"✅ DOI: {doi_col}")
                        else:
                            st.info("DOI列可选，可忽略")

                    # 预览
                    show_cols = [c for c in [title_col, abstract_col, doi_col] if c]
                    st.dataframe(df[show_cols].head(5), use_container_width=True, hide_index=True)

    with col2:
        # 输出配置卡片（点击切换）
        btn_label2 = "📤 输出配置" if lang == 'zh' else "📤 Output Config"
        if st.button(btn_label2, key="toggle_output_card", use_container_width=True, type="secondary"):
            st.session_state.scoring_show_output = not st.session_state.scoring_show_output

        if st.session_state.scoring_show_output:
            of = st.text_input("输出文件夹", value=st.session_state.scoring_output_folder, key="out_folder")
            fn = st.text_input("输出文件名", value=st.session_state.scoring_output_filename, key="out_fname")
            st.session_state.scoring_output_folder = of
            st.session_state.scoring_output_filename = fn

            st.caption("输出格式: 标题 | 摘要 | DOI | 平均评分 | 评分依据")

    # === 评分参数 ===
    st.markdown("---")
    with st.expander("⚙️ 评分参数", expanded=True):
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            expert_count = st.number_input("👥 专家数量", min_value=1, max_value=20, value=3,
                                           help="每篇文献由N个AI评委独立评分后取平均")
        with col_e2:
            score_threshold = st.number_input("📊 评分阈值", min_value=0.1, max_value=1.0,
                                               value=Config.DEFAULT_SCORE_THRESHOLD, step=0.1)
        with col_e3:
            max_workers = st.number_input("⚡ 并发数", min_value=1, max_value=25, value=8,
                                                     help="同时评分多少篇文献（含所有专家请求）")

    with st.expander("📝 评分提示词", expanded=True):
        scoring_prompt = st.text_area("", value=Config.DEFAULT_SCORING_PROMPT, height=150)

    with st.expander("🔗 API配置", expanded=False):
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                api_url = st.text_input("API地址", value=Config.MINIMAX_API)
            with col_a2:
                api_key = st.text_input("API密钥", value=Config.DEFAULT_API_KEY, type="password")
            with col_a3:
                model_name = st.text_input("模型名称", value=Config.MINIMAX_MODEL)

    # === 开始评分 ===
    st.markdown("---")

    # 检测临时文件（中断后残留）
    from pathlib import Path as _P
    out_dir = st.session_state.get("scoring_output_folder", "D:/PI_ASS/output")
    out_name = st.session_state.get("scoring_output_filename", "scoring_results.xlsx")
    parts_dir = _P(out_dir) / ".parts"
    part_files = sorted(parts_dir.glob("part_*.xlsx")) if parts_dir.exists() else []

    # 检查是否有评分结果（合并完成 或 评分完成）
    if _SCORING_STATE.get("results") is not None:
        st.markdown("---")
        st.subheader("📋 评分结果")
        st.dataframe(_SCORING_STATE["results"], use_container_width=True)
        csv_data = _SCORING_STATE["results"].to_csv(index=False)
        st.download_button("📥 下载CSV", csv_data, "scoring_results.csv", "text/csv")

    if part_files:
        import pandas as _pd
        last_part = part_files[-1]
        try:
            partial_df = _pd.read_excel(last_part)
            n = len(partial_df)
            st.markdown(f"""<div style="background:#FEF3C7;border:1px solid #F59E0B;border-radius:12px;padding:16px;margin:12px 0;">
                <b>📂 发现未完成的评分结果</b> — 共 {n} 篇文献已评分，但未完成合并
            </div>""", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📁 合并临时结果", type="primary", use_container_width=True):
                    full_path = _P(out_dir) / out_name
                    partial_df.to_excel(full_path, index=False)
                    import shutil
                    shutil.rmtree(parts_dir)
                    st.session_state.scoring_results = partial_df
                    # 不 rerun，直接在本轮显示
            with c2:
                if st.button("🗑 丢弃临时文件", use_container_width=True):
                    import shutil
                    shutil.rmtree(parts_dir)
        except Exception as e:
            st.error(f"临时文件读取失败: {e}")

    # 显示错误（评分失败后保留，不管线程是否存活）
    if _SCORING_STATE.get("error"):
        st.error(f"❌ {_SCORING_STATE['error']}")

    # 开始评分 / 结束评分
    # 线程引用从 _SCORING_STATE（cache_resource）读取，跨 rerun 持久
    scoring_thread = _SCORING_STATE.get("thread")
    if scoring_thread is not None and scoring_thread.is_alive():
        # 正在评分：显示进度 + 结束按钮
        p = _SCORING_STATE.get("progress", {})
        st.markdown("### ⏳ 评分进行中...")
        st.progress(p.get("pct", 0))
        st.text(p.get("text", ""))
        st.text(p.get("status", ""))

        if st.button("⏹ 结束评分", type="primary", use_container_width=True):
            _SCORING_STATE["cancel"].set()
            scoring_thread.join(timeout=30)
            _SCORING_STATE["thread"] = None
            st.rerun()

        # 短暂延迟后 rerun，让浏览器有空渲染进度
        time.sleep(1)
        st.rerun()

    else:
        # 空闲状态：开始评分按钮
        # 注：API 仅有 Kimi-K2.5（推理模型），无法做"简单快评"，
        # 故只保留详细评分（评分+依据）。
        start_clicked = st.button("🚀 开始评分", type="primary", use_container_width=True,
                                    help="AI 多评委并行评分（评分 + 评分依据）")
        if start_clicked:
            df = st.session_state.get("scoring_df")
            tcol = st.session_state.get("scoring_title_col")
            if df is None:
                st.error("请先上传文献数据文件")
            elif not tcol:
                st.error("请先选择/确认标题列")
            else:
                # 取消并等待可能残留的旧评分线程。
                # 修复进度条来回跳动（26%↔30%）：多个并发线程各自维护独立 done_count，
                # 交替覆盖 _SCORING_STATE["progress"]，导致百分比在多个值间乱跳。
                _old_thread = _SCORING_STATE.get("thread")
                if _old_thread is not None and _old_thread.is_alive():
                    _old_cancel = _SCORING_STATE.get("cancel")
                    if _old_cancel:
                        _old_cancel.set()
                    _old_thread.join(timeout=30)
                    _SCORING_STATE["thread"] = None
                if parts_dir.exists():
                    import shutil
                    shutil.rmtree(parts_dir)
                parts_dir.mkdir(parents=True, exist_ok=True)
                # 保险：确保输出父目录存在（修复 to_excel "non-existent directory"）
                _P(out_dir).mkdir(parents=True, exist_ok=True)

                cancel_ev = threading.Event()
                st.session_state.scoring_results = None
                _SCORING_STATE["results"] = None
                _SCORING_STATE["progress"] = {}
                _SCORING_STATE["error"] = None
                _SCORING_STATE["cancel"] = cancel_ev

                # 关键：在主线程（有 ScriptRunContext）预先读取所有 session_state，
                # 后台线程不能安全访问 st.session_state（会抛 "missing ScriptRunContext"，
                # 导致评分线程刚启动就崩溃，表现为"点了开始评分没反应"）
                _s_title = st.session_state.scoring_title_col
                _s_abs = st.session_state.scoring_abstract_col
                _s_doi = st.session_state.scoring_doi_col
                _s_outfolder = st.session_state.scoring_output_folder
                _s_outname = st.session_state.scoring_output_filename

                def run_in_thread():
                    import datetime as _dt, traceback as _tb
                    _log = lambda m: None
                    try:
                        with open("D:/PI_ASS/scoring_debug.log", "a", encoding="utf-8") as _f:
                            _f.write(f"\n[{_dt.datetime.now()}] THREAD_STARTED\n")
                        scoreLiterature_v2(
                            df, _s_title, _s_abs, _s_doi,
                            scoring_prompt, api_url, api_key,
                            expert_count, score_threshold, max_workers,
                            _s_outfolder, _s_outname,
                            model_name=model_name,
                            cancel_event=cancel_ev
                        )
                        with open("D:/PI_ASS/scoring_debug.log", "a", encoding="utf-8") as _f:
                            _f.write(f"[{_dt.datetime.now()}] THREAD_FINISHED_OK\n")
                    except Exception as _e:
                        # 转义反斜杠避免 Streamlit st.error 渲染 markdown 时吃掉路径分隔符
                        _SCORING_STATE["error"] = f"评分线程异常: {str(_e).replace(chr(92), '/')}"
                        with open("D:/PI_ASS/scoring_debug.log", "a", encoding="utf-8") as _f:
                            _f.write(f"[{_dt.datetime.now()}] THREAD_CRASH: {_e}\n{_tb.format_exc()}\n")

                t = threading.Thread(target=run_in_thread, daemon=True)
                _SCORING_STATE["thread"] = t
                t.start()
                st.rerun()

def scoreLiterature_v2(df, title_col, abstract_col, doi_col,
                      scoring_prompt, api_url, api_key,
                      expert_count, score_threshold, max_workers,
                      output_folder, output_filename,
                      model_name=None, cancel_event=None):
    """评分函数（后台线程安全版）：写入 _SCORING_STATE 而非 st.session_state"""
    import requests
    import re
    import shutil
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from collections import defaultdict
    from pathlib import Path

    def _set_progress(pct, text, status=""):
        _SCORING_STATE["progress"] = {"pct": pct, "text": text, "status": status}

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        total = len(df)
        total_tasks = total * expert_count
        SAVE_INTERVAL = 50
        actual_model = model_name or Config.MINIMAX_MODEL

        papers = []
        for _, row in df.iterrows():
            title = str(row.get(title_col, "")) if pd.notna(row.get(title_col, "")) else ""
            abstract = str(row.get(abstract_col, "")) if abstract_col and pd.notna(row.get(abstract_col, "")) else ""
            doi = str(row.get(doi_col, "")) if doi_col and pd.notna(row.get(doi_col, "")) else ""
            papers.append({"title": title, "abstract": abstract, "doi": doi})

        collector = defaultdict(lambda: {"scores": [], "reasons": []})
        done_count = 0
        fail_count = 0
        paper_expert_count = defaultdict(int)

        parts_dir = Path(output_folder) / ".parts"
        parts_dir.mkdir(parents=True, exist_ok=True)

        def call_expert(title, abstract):
            full_prompt = f"""请作为聚酰亚胺材料领域专家进行文献评分。

{scoring_prompt}

文献标题: {title}

文献摘要: {abstract}

重要：请先输出最终评分，再写评分依据！
格式：
最终评分：【0.XX】
评分依据：...

例如：
最终评分：【0.85】
评分依据：该文献研究了聚酰亚胺在显示器领域的应用，关注了热性能和机械性能，符合研究领域"""
            max_tok = 1024
            payload = {
                "model": actual_model,
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": max_tok,
                "temperature": 0.7
            }
            try:
                resp = requests.post(
                    f"{api_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=120
                )
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
            except Exception:
                pass
            return None

        def build_results():
            rows = []
            for pi, paper in enumerate(papers):
                if not paper["title"]:
                    continue
                c = collector[pi]
                avg = sum(c["scores"]) / len(c["scores"]) if c["scores"] else 0.0
                basis = "; ".join(dict.fromkeys(r for r in c["reasons"] if r)) if c["reasons"] else ""
                rows.append({
                    "标题": paper["title"][:100] if len(paper["title"]) > 100 else paper["title"],
                    "摘要": (paper["abstract"][:300] + "...") if len(paper["abstract"]) > 300 else paper["abstract"],
                    "DOI": paper["doi"],
                    "平均评分": round(avg, 4),
                    "评分依据": basis
                })
            return pd.DataFrame(rows)

        _set_progress(0, "准备中...", "")
        pi = 0
        actual_max = min(max_workers, total_tasks)
        with ThreadPoolExecutor(max_workers=actual_max) as pool:
            fut_to_paper = {}
            for pi, paper in enumerate(papers):
                if not paper["title"]:
                    continue
                for _ in range(expert_count):
                    fut = pool.submit(call_expert, paper["title"], paper["abstract"])
                    fut_to_paper[fut] = pi

            for fut in as_completed(fut_to_paper):
                if cancel_event and cancel_event.is_set():
                    for f in fut_to_paper:
                        f.cancel()
                    break

                pi = fut_to_paper[fut]
                try:
                    txt = fut.result(timeout=120)
                    if txt:
                        m = re.search(r"【\s*([0-9.]+)\s*】", txt)
                        if m:
                            s = float(m.group(1))
                            if s > 1:
                                s /= 100
                            collector[pi]["scores"].append(max(0.0, min(1.0, s)))
                        rm = re.search(r"评分依据[：:]\s*(.+?)(?:最终评分|$)", txt, re.DOTALL)
                        if rm:
                            collector[pi]["reasons"].append(rm.group(1).strip())
                    else:
                        fail_count += 1
                except Exception:
                    fail_count += 1

                paper_expert_count[pi] += 1
                done_count += 1
                pct = min(done_count / total_tasks, 1.0) if total_tasks else 0
                _set_progress(pct, f"文献: {len(paper_expert_count)}/{total} | API: {done_count}/{total_tasks} (失败: {fail_count})", f"当前文献: {papers[pi]['title'][:50]}" if pi < len(papers) else "")

                if done_count % (SAVE_INTERVAL * expert_count) == 0:
                    # 保险：多进程残留 rmtree 时序问题可能删除 .parts，这里确保存在
                    if not parts_dir.exists():
                        parts_dir.mkdir(parents=True, exist_ok=True)
                    part_path = parts_dir / f"part_{done_count:06d}.xlsx"
                    build_results().to_excel(part_path, index=False)

        full_df = build_results()
        # 保险：确保最终输出目录存在（修复 "non-existent directory"）
        Path(output_folder).mkdir(parents=True, exist_ok=True)
        output_path = Path(output_folder) / output_filename
        full_df.to_excel(output_path, index=False)
        _SCORING_STATE["results"] = full_df
        _set_progress(1.0, f"完成！共 {len(full_df)} 篇", "完成")

        if parts_dir.exists():
            shutil.rmtree(parts_dir)

        selected = full_df[full_df["平均评分"] >= score_threshold] if not full_df.empty else pd.DataFrame()
        if len(selected) > 0:
            doi_path = Path(output_folder) / (Path(output_filename).stem + "_selected_dois.txt")
            selected[["DOI"]].to_csv(doi_path, index=False, header=False)

    except Exception as e:
        import traceback
        err_text = f"评分失败: {e}"
        _SCORING_STATE["progress"] = {"pct": 0, "text": err_text, "status": "错误"}
        _SCORING_STATE["results"] = None
        _SCORING_STATE["error"] = err_text
    # ==================== 文献下载 ====================
def create_download_page():
    """文献下载页面 - 评分结果批量下载PDF"""
    lang = st.session_state.get("lang", "zh")
    st.title("📥 文献下载")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>从评分结果筛选高分文献，通过Sci-Hub批量下载PDF</p>", unsafe_allow_html=True)
    col_src, col_cfg = st.columns(2)
    with col_src:
        st.markdown("### 📋 来源选择")
        # 评分完成在后台线程，结果只写 _SCORING_STATE["results"]（线程安全共享字典）；
        # session_state["scoring_results"] 仅在"合并临时结果"路径（主线程）被赋值。
        # 两个源都要查，否则正常跑完评分后下载页继承不到 DOI。
        scored_results = _SCORING_STATE.get("results")
        if scored_results is None:
            scored_results = st.session_state.get("scoring_results")
        if scored_results is not None:
            st.success(f"✅ \u68c0\u6d4b\u5230\u8bc4\u5206\u7ed3\u679c\uff1a{len(scored_results)} \u7bc7\u6587\u732e\u5df2\u8bc4\u5206")
            src_option = st.radio("DOI\u6765\u6e90", ["\u8bc4\u5206\u7ed3\u679c", "\u4e0a\u4f20\u6587\u4ef6"], index=0, horizontal=True, label_visibility="collapsed")
        else:
            st.info("\u24d8 \u8bf7\u5148\u5728\u300c\u6587\u732e\u8bc4\u5206\u300d\u6a21\u5757\u5b8c\u6210\u8bc4\u5206\uff0c\u6216\u4e0a\u4f20\u8bc4\u5206\u7ed3\u679c\u6587\u4ef6")
            src_option = st.radio("DOI\u6765\u6e90", ["\u8bc4\u5206\u7ed3\u679c", "\u4e0a\u4f20\u6587\u4ef6"], index=1, horizontal=True, label_visibility="collapsed")
        if src_option == "\u8bc4\u5206\u7ed3\u679c" and scored_results is not None:
            st.session_state.download_scored_df = scored_results
        elif src_option == "\u4e0a\u4f20\u6587\u4ef6":
            uploaded = st.file_uploader("\u4e0a\u4f20\u8bc4\u5206\u7ed3\u679c\u6587\u4ef6\uff08xlsx/csv\uff09", type=["xlsx", "xls", "csv"], label_visibility="collapsed")
            if uploaded is not None:
                try:
                    if uploaded.name.endswith(".csv"): df = pd.read_csv(uploaded)
                    else: df = _smart_read_excel(uploaded)
                    st.session_state.download_scored_df = df
                    st.success(f"\u8bfb\u53d6\u5230 {len(df)} \u6761\u8bb0\u5f55")
                except Exception as e: st.error(f"\u6587\u4ef6\u8bfb\u53d6\u5931\u8d25: {e}")
        elif scored_results is None and src_option == "\u8bc4\u5206\u7ed3\u679c":
            st.warning("\u6682\u65e0\u8bc4\u5206\u7ed3\u679c\uff0c\u8bf7\u5148\u5b8c\u6210\u8bc4\u5206\u6216\u4e0a\u4f20\u6587\u4ef6")
    with col_cfg:
        st.markdown("### \u2699\ufe0f \u7b5b\u9009\u4e0e\u4e0b\u8f7d")
        threshold = st.number_input("\u8bc4\u5206\u9608\u503c", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        scihub_url = st.text_input("Sci-Hub\u955c\u50cf\u5730\u5740", value="https://sci-hub.ru")
        output_folder = st.text_input("\u4fdd\u5b58\u6587\u4ef6\u5939", value=str(Config.PAPER_DIR))
        with st.expander("\u5e76\u53d1\u914d\u7f6e", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a: max_workers = st.slider("\u5e76\u53d1\u6570", 1, 10, 3)
            with col_b: timeout = st.slider("\u8d85\u65f6(\u79d2)", 10, 120, 30)
    st.markdown("---")
    df = st.session_state.get("download_scored_df")
    if df is not None:
        score_col = None
        for c in ['\u5e73\u5747\u8bc4\u5206', 'avg_score', 'score', '\u8bc4\u5206']:
            if c in df.columns: score_col = c; break
        doi_col = 'DOI' if 'DOI' in df.columns else ('doi' if 'doi' in df.columns else None)
        dois = []
        for _, row in df.iterrows():
            score = row.get(score_col, 0) or 0 if score_col else 1.0
            if score >= threshold:
                doi = row.get(doi_col, '') if doi_col else ''
                if doi and str(doi).strip(): dois.append({"doi": str(doi).strip(), "score": score})
        seen = set()
        unique_dois = [d for d in dois if not (d["doi"] in seen or seen.add(d["doi"]))]
        if unique_dois:
            st.info(f"\U0001f4ca \u8bc4\u5206>={threshold}\uff1a{len(unique_dois)} \u7bc7\u5f85\u4e0b\u8f7d")
            st.dataframe(pd.DataFrame(unique_dois), use_container_width=True, hide_index=True)
        elif not score_col and df is not None:
            all_dois = []
            dc = doi_col or 'DOI'
            for _, row in df.iterrows():
                doi = row.get(dc, '') if dc in df.columns else ''
                if doi and str(doi).strip(): all_dois.append({"doi": str(doi).strip()})
            seen2 = set()
            unique_all = [d for d in all_dois if not (d["doi"] in seen2 or seen2.add(d["doi"]))]
            if unique_all:
                st.info(f"\U0001f4ca \u5171 {len(unique_all)} \u4e2aDOI\uff08\u65e0\u8bc4\u5206\u5217\uff0c\u5168\u90e8\u663e\u793a\uff09")
                st.dataframe(pd.DataFrame(unique_all), use_container_width=True, hide_index=True)
            else: st.warning(f"\u672a\u627e\u5230DOI\u5217\uff0c\u53ef\u7528\u7684\u5217\uff1a{list(df.columns)}")
        else: st.warning(f"\u6ca1\u6709\u8bc4\u5206>={threshold}\u7684\u6587\u732e\uff0c\u8bf7\u964d\u4f4e\u9608\u503c\u6216\u68c0\u67e5\u8bc4\u5206\u7ed3\u679c")
    dl_thread = st.session_state.get("download_thread")
    if dl_thread is not None and dl_thread.is_alive():
        p = _DOWNLOAD_STATE.get("progress", {})
        st.markdown("### \u23f3 \u4e0b\u8f7d\u8fdb\u884c\u4e2d...")
        st.progress(p.get("pct", 0))
        st.text(p.get("text", ""))
        st.text(p.get("status", ""))
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("\u23f9 \u53d6\u6d88\u4e0b\u8f7d", type="primary", width='stretch'):
                ev = st.session_state.get("download_cancel")
                if ev: ev.set(); st.rerun()
        with col_b2:
            if st.button("\U0001f504 \u5237\u65b0\u8fdb\u5ea6"): st.rerun()
        time.sleep(2); st.rerun()
    else:
        dl_res = _DOWNLOAD_STATE.get("download_results")
        if dl_res is not None:
            c1, c2, c3 = st.columns(3)
            c1.metric("\u603b\u6570", dl_res.get("total", 0))
            c2.metric("\u2705 \u6210\u529f", dl_res.get("success", 0))
            c3.metric("\u274c \u5931\u8d25", dl_res.get("failed", 0))
            if dl_res.get("failed", 0) > 0:
                with st.expander("\u67e5\u770b\u5931\u8d25\u7684DOI"):
                    for d in dl_res.get("failed_dois", []): st.code(d)
            if st.button("\U0001f5d1 \u6e05\u9664\u7ed3\u679c", use_container_width=True):
                _DOWNLOAD_STATE["download_results"] = None; _DOWNLOAD_STATE["progress"] = {}; st.rerun()
        if st.button("\u25b6 \u5f00\u59cb\u4e0b\u8f7d", type="primary", use_container_width=True):
            df = st.session_state.get("download_scored_df")
            if df is None: st.error("\u8bf7\u5148\u9009\u62e9\u8bc4\u5206\u7ed3\u679c\u6216\u4e0a\u4f20\u6587\u4ef6"); st.stop()
            score_col = None
            for c in ['\u5e73\u5747\u8bc4\u5206', 'avg_score', 'score', '\u8bc4\u5206']:
                if c in df.columns: score_col = c; break
            doi_col = 'DOI' if 'DOI' in df.columns else ('doi' if 'doi' in df.columns else None)
            targets = []
            for _, row in df.iterrows():
                score = row.get(score_col, 0) or 0 if score_col else 1.0
                if score >= threshold:
                    doi = row.get(doi_col, '') if doi_col else ''
                    if doi and str(doi).strip(): targets.append(str(doi).strip())
            seen3 = set()
            unique_targets = [d for d in targets if not (d in seen3 or seen3.add(d))]
            if not unique_targets: st.error(f"\u6ca1\u6709\u8bc4\u5206>={threshold}\u7684\u6587\u732eDOI\uff0c\u8bf7\u964d\u4f4e\u9608\u503c"); st.stop()
            from modules.download_module import LiteratureDownloader
            import threading as _th
            cancel_ev = _th.Event()
            st.session_state.download_cancel = cancel_ev
            _DOWNLOAD_STATE["download_results"] = None; _DOWNLOAD_STATE["progress"] = {}
            def run_dl():
                dl = LiteratureDownloader(output_dir=output_folder, max_workers=max_workers, timeout=timeout, scihub_url=scihub_url)
                def on_prog(c, t): _DOWNLOAD_STATE["progress"] = {"pct": c/t if t>0 else 0, "text": f"\u4e0b\u8f7d {c}/{t}", "status": ""}
                r = dl.download_batch(unique_targets, progress_callback=on_prog, cancel_event=cancel_ev)
                _DOWNLOAD_STATE["download_results"] = r
            t = _th.Thread(target=run_dl, daemon=True)
            st.session_state.download_thread = t; t.start(); time.sleep(0.5); st.rerun()
    st.markdown("---")
    st.info("\u24d8 \u4e0b\u8f7d\u6e90\u9ed8\u8ba4\u4e3a Sci-Hub\uff0c\u53ef\u4fee\u6539\u4e3a\u5176\u4ed6\u955c\u50cf\u6216\u81ea\u5efa\u4ee3\u7406")# ==================== 数据提取 ====================
def create_extraction_page():
    """数据提取页面 - LLM提取24列表格"""
    st.title("🔬 数据提取")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>从文献PDF中提取聚酰亚胺24列标准表格</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📁 PDF文件夹")
        pdf_folder = st.text_input("路径", value=str(Config.PAPER_DIR), key="ext_pdf")
    with col2:
        st.markdown("### ⚙️ API")
        ext_api_url = st.text_input("地址", value=Config.MINIMAX_API, key="ext_api_url")
        ext_api_key = st.text_input("密钥", value=Config.DEFAULT_API_KEY, type="password", key="ext_api_key")
        ext_model = st.text_input("模型", value=Config.MINIMAX_MODEL, key="ext_model")
        ext_workers = st.slider("并发数", 1, 5, 2, key="ext_workers")
    output_folder = st.text_input("输出文件夹", value=str(Config.OUTPUT_DIR), key="ext_out")
    with st.expander("📝 提取提示词", expanded=False):
        extraction_prompt = st.text_area("", value=Config.DEFAULT_EXTRACTION_PROMPT, height=200)
    st.markdown("---")
    ext_thread = _EXTRACTION_STATE.get("thread")
    if ext_thread is not None and ext_thread.is_alive():
        p = _EXTRACTION_STATE.get("progress", {})
        st.markdown("### ⏳ 提取进行中...")
        st.progress(p.get("pct", 0))
        st.text(p.get("text", ""))
        st.text(p.get("status", ""))
        if st.button("⏹ 取消", type="primary", width='stretch'):
            ev = _EXTRACTION_STATE.get("cancel")
            if ev: ev.set()
            # 立即解除“进行中”状态：后台 daemon 线程会因 cancel 标志尽快 break 收尾
            # （正在跑的 API 调用受 requests 阻塞无法强杀，会自然完成）。
            # with-Pool 的 shutdown(wait=True) 仍要等当前并发任务跑完，所以直接清 thread 引用，
            # 让 UI 立刻恢复可用，不再卡在进度条。已提取的部分结果会随后台收尾自动保留。
            _EXTRACTION_STATE["thread"] = None
            _EXTRACTION_STATE["cancel"] = None
            _EXTRACTION_STATE["progress"] = {"pct": 0, "text": "已取消", "status": "已取消"}
            st.rerun()
        if st.button("🔄 刷新"): st.rerun()
        time.sleep(2); st.rerun()
    else:
        ext_res = _EXTRACTION_STATE.get("results")
        if ext_res is not None:
            st.subheader("📋 提取结果")
            st.dataframe(ext_res, use_container_width=True)
            csv_data = ext_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 CSV", csv_data, "extracted_data.csv", "text/csv")
            if st.button("🗑 清除", use_container_width=True):
                _EXTRACTION_STATE["results"] = None
                _EXTRACTION_STATE["progress"] = {}
                st.rerun()
        if st.button("▶ 开始提取", type="primary", use_container_width=True):
            folder = Path(pdf_folder)
            if not folder.exists() or not list(folder.glob("*.pdf")):
                st.error("文件夹中未找到PDF文件"); st.stop()
            from modules.extraction_module import DataExtractor
            import threading as _th
            cancel_ev = _th.Event()
            _EXTRACTION_STATE["cancel"] = cancel_ev
            _EXTRACTION_STATE["results"] = None
            _EXTRACTION_STATE["progress"] = {}
            def run_ext():
                ext = DataExtractor(api_url=ext_api_url, api_key=ext_api_key, model=ext_model, extraction_prompt=extraction_prompt, max_workers=ext_workers)
                def on_prog(c, t):
                    _EXTRACTION_STATE["progress"] = {"pct": c/t if t>0 else 0, "text": f"提取 {c}/{t}", "status": ""}
                out_path = Path(output_folder) / "extracted_data.xlsx"
                df = ext.extract_from_folder(str(folder), str(out_path), progress_callback=on_prog, cancel_event=cancel_ev)
                _EXTRACTION_STATE["results"] = df
                _EXTRACTION_STATE["progress"] = {"pct": 1.0, "text": f"完成！共 {len(df)} 条", "status": "完成"}
            t = _th.Thread(target=run_ext, daemon=True)
            _EXTRACTION_STATE["thread"] = t
            t.start(); time.sleep(0.5); st.rerun()
    st.info("💡 提取使用评分页的API配置")

# ==================== SMILES 转化 ====================
def create_smiles_page():
    """SMILES转化页面 - LLM把单体全拼/简写转SMILES + RDKit校验"""
    import pandas as _pd
    from modules.smiles_module import SmilesConverter, MONOMER_COLS, rdkit_available, SMILES_PROMPT_TEMPLATE

    st.title("🧬 SMILES 转化")
    st.markdown(
        "<p style='color: #64748B; margin-bottom: 24px;'>"
        "将单体【英文全拼 + 简写】交给大模型转成规范 SMILES，再用 RDKit 校验结构合法性"
        "</p>", unsafe_allow_html=True)

    # RDKit 状态提示
    if rdkit_available():
        st.success("✅ 已加载 RDKit，将进行严格化学校验（括号闭合 / 芳香性 / 价键 / 原子数）")
    else:
        st.warning("⚠️ 未检测到 RDKit，仅做括号配平等的语法校验（可靠性下降，建议 pip install rdkit）")

    # ---- API 配置（复用提取页配置）----
    c1, c2, c3 = st.columns(3)
    with c1:
        sm_api_url = st.text_input("API 地址", value=Config.MINIMAX_API, key="sm_api_url")
        sm_api_key = st.text_input("API 密钥", value=Config.DEFAULT_API_KEY, type="password", key="sm_api_key")
    with c2:
        sm_model = st.text_input("模型", value=Config.MINIMAX_MODEL, key="sm_model")
        sm_timeout = st.slider("超时(秒)", 30, 300, 180, key="sm_timeout")
    with c3:
        st.markdown("**数据来源**")
        ext_df = _EXTRACTION_STATE.get("results")
        use_ext = st.checkbox("使用「数据提取」结果", value=(ext_df is not None),
                              key="sm_use_ext", disabled=(ext_df is None))
        up_file = st.file_uploader("或上传 Excel/CSV", type=["xlsx", "xls", "csv"], key="sm_up")

    with st.expander("📝 转化提示词模板", expanded=False):
        st.code(SMILES_PROMPT_TEMPLATE, language="markdown")

    # 准备输入数据
    src_df = None
    if use_ext and ext_df is not None:
        src_df = ext_df
        from modules.smiles_module import normalize_input_columns
        src_df, _rename = normalize_input_columns(src_df)
        st.info(f"📊 已选用「数据提取」结果：{len(src_df)} 行")
    if up_file is not None:
        try:
            if up_file.name.lower().endswith(".csv"):
                src_df = _pd.read_csv(up_file)
            else:
                src_df = _pd.read_excel(up_file)
            from modules.smiles_module import normalize_input_columns
            src_df, _rename = normalize_input_columns(src_df)
            if _rename:
                st.info(f"📋 列名归一化：{_rename}")
            st.info(f"📂 已读取上传文件：{len(src_df)} 行")
        except Exception as e:
            st.error(f"读取上传文件失败：{e}")
            src_df = None

    # 预览单体相关列
    if src_df is not None:
        monomer_cols = [c for c, _, _, _ in MONOMER_COLS] + [c for _, c, _, _ in MONOMER_COLS]
        monomer_cols = [c for c in monomer_cols if c in src_df.columns]
        st.markdown("#### 输入预览（单体列）")
        st.dataframe(src_df[monomer_cols].head(20) if monomer_cols else src_df.head(20),
                     use_container_width=True)

    st.markdown("---")

    # ---- 后台转化（bg-thread + 进度/取消，与提取页同款）----
    sm_thread = _SMILES_STATE.get("thread")
    if sm_thread is not None and sm_thread.is_alive():
        p = _SMILES_STATE.get("progress", {})
        st.markdown("### ⏳ SMILES 转化进行中...")
        st.progress(p.get("pct", 0))
        st.text(p.get("text", ""))
        st.text(p.get("status", ""))
        if st.button("⏹ 取消", type="primary", width='stretch'):
            ev = _SMILES_STATE.get("cancel")
            if ev:
                ev.set()
            _SMILES_STATE["thread"] = None
            _SMILES_STATE["cancel"] = None
            _SMILES_STATE["progress"] = {"pct": 0, "text": "已取消", "status": "已取消"}
            st.rerun()
        if st.button("🔄 刷新"):
            st.rerun()
        time.sleep(2)
        st.rerun()
    else:
        sm_res = _SMILES_STATE.get("results")
        if sm_res is not None:
            st.subheader("📋 转化结果")
            st.dataframe(sm_res, use_container_width=True)
            csv_data = sm_res.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 下载 CSV", csv_data, "smiles_converted.csv", "text/csv",
                               help="UTF-8 BOM编码，Excel打开可正常显示中文")
            try:
                import io
                buf = io.BytesIO()
                with _pd.ExcelWriter(buf, engine="openpyxl") as w:
                    sm_res.to_excel(w, index=False)
                st.download_button("📥 下载 Excel", buf.getvalue(), "smiles_converted.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception:
                pass
            if st.button("🗑 清除", use_container_width=True):
                _SMILES_STATE["results"] = None
                _SMILES_STATE["progress"] = {}
                st.rerun()

        if st.button("▶ 开始转化", type="primary", use_container_width=True):
            if src_df is None:
                st.error("请先选择数据来源（数据提取结果 或 上传文件）")
                st.stop()
            # 校验必要列
            need = [c for c, _, _, _ in MONOMER_COLS] + [c for _, c, _, _ in MONOMER_COLS]
            missing = [c for c in need if c not in src_df.columns]
            if missing:
                st.warning(f"以下单体列缺失，对应位置将留空：{missing}")

            import threading as _th
            cancel_ev = _th.Event()
            _SMILES_STATE["cancel"] = cancel_ev
            _SMILES_STATE["results"] = None
            _SMILES_STATE["progress"] = {}
            _input_df = src_df.copy()

            def run_sm():
                conv = SmilesConverter(api_url=sm_api_url, api_key=sm_api_key,
                                       model=sm_model, timeout=sm_timeout)

                def on_prog(c, t):
                    _SMILES_STATE["progress"] = {
                        "pct": c / t if t > 0 else 0,
                        "text": f"转化 {c}/{t}", "status": ""}

                out = conv.process_dataframe(_input_df, progress_callback=on_prog,
                                             cancel_event=cancel_ev)
                _SMILES_STATE["results"] = out
                sm_cols = [t_col for _, _, t_col, _ in MONOMER_COLS]
                nonempty = int(
                    out[sm_cols].astype(str)
                    .apply(lambda s: (~s.isin(["", "nan", "None"]))).sum().sum()
                )
                _SMILES_STATE["progress"] = {
                    "pct": 1.0,
                    "text": f"完成！有效 SMILES {nonempty} 个",
                    "status": "完成"}

            t = _th.Thread(target=run_sm, daemon=True)
            _SMILES_STATE["thread"] = t
            t.start()
            time.sleep(0.5)
            st.rerun()

    st.info("💡 复用「数据提取」页的 API 配置；相同单体自动去重以减少调用。")


def create_descriptors_page():
    """描述符计算页面 - RDKit/Morgan/Mordred/PaDEL 多源"""
    import threading as _th
    from modules.descriptor_module import (
        DescriptorCalculator, RDKIT_AVAILABLE, MORDRED_AVAILABLE,
        PADEL_AVAILABLE, PADEL_LIB_AVAILABLE, JAVA_AVAILABLE,
    )

    st.title("🧪 描述符计算")
    st.markdown("<p style='color: #64748B; margin-bottom: 20px;'>RDKit / Morgan / Mordred / PaDEL 多源分子描述符</p>", unsafe_allow_html=True)

    # ---- 可用性徽章 ----
    if not RDKIT_AVAILABLE:
        st.error("⚠️ RDKit未安装，描述符计算无法运行")
        st.code("pip install rdkit")
        return
    badges = [("RDKit", "ok"), ("Morgan", "ok")]
    if MORDRED_AVAILABLE: badges.append(("Mordred 1613", "ok"))
    if PADEL_AVAILABLE: badges.append(("PaDEL", "ok"))
    elif PADEL_LIB_AVAILABLE: badges.append(("PaDEL", "warn"))
    bcols = st.columns(len(badges))
    for c, (name, lv) in zip(bcols, badges):
        icon = "✅" if lv == "ok" else "⚠️"
        c.markdown(f"**{icon} {name}**")

    if PADEL_LIB_AVAILABLE and not JAVA_AVAILABLE:
        st.warning("⚠️ PaDEL：padelpy 已安装，但未检测到 Java 运行环境。"
                   "在【管理员】终端执行后重启应用即可启用 PaDEL：")
        st.code("winget install --id Microsoft.OpenJDK.17 -e", language="bash")

    # ---- 数据来源 ----
    st.markdown("#### 📥 数据来源")
    src_df = None
    sm_df = _SMILES_STATE.get("results")
    use_sm = st.checkbox("使用「SMILES 转化」结果", value=(sm_df is not None),
                         disabled=(sm_df is None), key="desc_use_sm")
    up_file = st.file_uploader("或上传 CSV（需含 SMILES 列）",
                               type=["csv"], key="desc_up")

    if use_sm and sm_df is not None:
        src_df = sm_df
        st.info(f"📊 已选用 SMILES 转化结果：{len(src_df)} 行")
    if up_file is not None:
        try:
            src_df = pd.read_csv(up_file)
            st.info(f"📂 已读取上传文件：{len(src_df)} 行")
        except Exception as e:
            st.error(f"读取失败：{e}")
            src_df = None

    sm_col = None
    if src_df is not None:
        cand = [c for c in src_df.columns if 'smiles' in str(c).lower()]
        sm_col = cand[0] if cand else None
        if len(cand) > 1:
            sm_col = st.selectbox("选择 SMILES 列", cand, key="desc_smcol")
        if sm_col is None:
            st.error("未找到 SMILES 列")
        else:
            st.success(f"SMILES 列：{sm_col}")
            st.dataframe(src_df[[sm_col]].dropna().head(15), use_container_width=True)

    # ---- 计算选项 ----
    st.markdown("#### 🧪 计算选项")
    with st.expander("描述符源与参数", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            calc_rdkit = st.checkbox("RDKit 描述符", value=True, key="desc_rdkit")
        with c2:
            calc_morgan = st.checkbox("Morgan 指纹", value=True, key="desc_morgan")
        with c3:
            calc_mordred = st.checkbox("Mordred (1613)", value=True,
                                       disabled=(not MORDRED_AVAILABLE), key="desc_mordred")
        with c4:
            calc_padel = st.checkbox("PaDEL", value=False,
                                     disabled=(not PADEL_AVAILABLE), key="desc_padel")
        p1, p2, p3 = st.columns(3)
        with p1:
            morgan_radius = st.number_input("Morgan 半径", 1, 4, 2, key="desc_mr")
            morgan_bits = st.select_slider("Morgan 位数", [512, 1024, 2048, 4096], 2048, key="desc_mb")
        with p2:
            mordred_3d = st.checkbox("Mordred 含3D描述符", value=False, key="desc_m3d")
        with p3:
            padel_fp = st.checkbox("PaDEL 含 PubChem指纹", value=False,
                                   disabled=(not PADEL_AVAILABLE), key="desc_pfp")
            padel_to = st.number_input("PaDEL 单分子超时(秒)", 30, 600, 60, key="desc_pto")

    if not any([calc_rdkit, calc_morgan, calc_mordred, calc_padel]):
        st.warning("请至少选择一个描述符源"); st.stop()

    st.markdown("---")

    # ---- 后台计算（线程/进度/取消）----
    dthread = _DESCRIPTOR_STATE.get("thread")
    if dthread is not None and dthread.is_alive():
        p = _DESCRIPTOR_STATE.get("progress", {})
        st.markdown("### ⏳ 描述符计算进行中...")
        st.progress(min(p.get("pct", 0.0), 1.0))
        st.text(p.get("text", ""))
        if st.button("⏹ 取消", type="primary", width='stretch'):
            ev = _DESCRIPTOR_STATE.get("cancel")
            if ev: ev.set()
            _DESCRIPTOR_STATE["thread"] = None
            _DESCRIPTOR_STATE["cancel"] = None
            st.rerun()
        time.sleep(2); st.rerun()
    else:
        dres = _DESCRIPTOR_STATE.get("results")
        if dres:
            st.subheader("📋 计算结果")
            src_tabs = st.tabs(list(dres.keys()))
            for tab, (src, ddf) in zip(src_tabs, dres.items()):
                with tab:
                    st.caption(f"{src}：{ddf.shape[0]} 行 × {ddf.shape[1]} 列")
                    st.dataframe(ddf, use_container_width=True)
                    csv = ddf.to_csv(index=False).encode("utf-8")
                    st.download_button(f"📥 下载 {src}.csv", csv,
                                       f"descriptors_{src}.csv", "text/csv", key=f"dl_{src}")
            try:
                comb = DescriptorCalculator().combine(list(dres.values()))
                if comb is not None and not comb.empty:
                    st.markdown("**合并预览（按 SMILES 对齐）**")
                    st.dataframe(comb.head(), use_container_width=True)
                    import io
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as w:
                        for src, ddf in dres.items():
                            ddf.to_excel(w, sheet_name=str(src)[:31], index=False)
                        comb.to_excel(w, sheet_name="combined", index=False)
                    st.download_button("📥 下载全部（Excel 多Sheet）",
                                       buf.getvalue(), "descriptors_all.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.warning(f"合并/导出出错：{e}")
            if st.button("🗑 清除结果", width='stretch'):
                _DESCRIPTOR_STATE["results"] = None
                _DESCRIPTOR_STATE["progress"] = {}
                st.rerun()

        if st.button("▶ 开始计算", type="primary", width='stretch'):
            if src_df is None or sm_col is None:
                st.error("请先提供数据来源（SMILES 转化结果 或 上传 CSV）"); st.stop()
            smiles_list = [s for s in src_df[sm_col].tolist()
                           if s is not None and str(s).strip() and str(s).lower() != 'nan']
            if not smiles_list:
                st.error("SMILES 列无有效数据"); st.stop()
            cancel_ev = _th.Event()
            _DESCRIPTOR_STATE["cancel"] = cancel_ev
            _DESCRIPTOR_STATE["results"] = None
            _DESCRIPTOR_STATE["progress"] = {}
            _opts = dict(calc_rdkit=calc_rdkit, calc_morgan=calc_morgan,
                         calc_mordred=calc_mordred, calc_padel=calc_padel,
                         morgan_radius=int(morgan_radius), morgan_bits=int(morgan_bits),
                         mordred_3d=mordred_3d, padel_fp=padel_fp, padel_timeout=int(padel_to))

            def _run_desc():
                calc = DescriptorCalculator(output_dir=str(Config.DATA_DIR))
                phases = sum([_opts['calc_rdkit'], _opts['calc_morgan'],
                              _opts['calc_mordred'], _opts['calc_padel']]) or 1
                phase = [0]
                def on_prog(done, total):
                    if total <= 0: return
                    pct = (phase[0] + done / total) / phases
                    _DESCRIPTOR_STATE["progress"] = {"pct": min(pct, 1.0),
                                                     "text": f"[{phase[0]+1}/{phases}] {done}/{total}"}
                out = {}
                sm = smiles_list
                if _opts['calc_rdkit']:
                    out['rdkit'] = calc.calculate_rdkit(sm, on_prog, cancel_ev)
                if _opts['calc_morgan']:
                    phase[0] = 1
                    out['morgan'] = calc.calculate_morgan(sm, _opts['morgan_radius'], _opts['morgan_bits'], on_prog, cancel_ev)
                if _opts['calc_mordred']:
                    phase[0] = 2
                    out['mordred'] = calc.calculate_mordred(sm, not _opts['mordred_3d'], on_prog, cancel_ev)
                if _opts['calc_padel']:
                    phase[0] = 3
                    out['padel'] = calc.calculate_padel(sm, _opts['padel_fp'], _opts['padel_timeout'], on_prog, cancel_ev)
                _DESCRIPTOR_STATE["results"] = out
                _DESCRIPTOR_STATE["progress"] = {"pct": 1.0,
                                                 "text": f"完成：{ {k: v.shape[0] for k, v in out.items()} }"}

            t = _th.Thread(target=_run_desc, daemon=True)
            _DESCRIPTOR_STATE["thread"] = t
            t.start(); time.sleep(0.5); st.rerun()


# ==================== 模型训练 ====================

def _show_training_comparison(hist, y_train=None, y_train_pred=None,
                              y_val=None, y_val_pred=None,
                              y_test=None, y_test_pred=None,
                              target_var=None):
    """显示训练结果对比图（R²散点图 + 历史对比条形图）"""
    from sklearn.metrics import r2_score
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # 如果有新训练的散点数据，显示三组散点图
    if y_train is not None and y_test is not None:
        fig = make_subplots(rows=1, cols=3,
                            subplot_titles=[f"训练集 (R²={r2_score(y_train, y_train_pred):.4f})",
                                            f"验证集 (R²={r2_score(y_val, y_val_pred):.4f})",
                                            f"测试集 (R²={r2_score(y_test, y_test_pred):.4f})"],
                            shared_yaxes=False)
        for col, (yt, yp, color, name) in enumerate([
            (y_train, y_train_pred, "#4F46E5", "训练"),
            (y_val, y_val_pred, "#F59E0B", "验证"),
            (y_test, y_test_pred, "#10B981", "测试"),
        ], start=1):
            fig.add_trace(go.Scatter(
                x=yt, y=yp, mode="markers",
                marker=dict(color=color, size=6, opacity=0.6),
                name=name,
            ), row=1, col=col)
            vmin = min(yt.min(), yp.min())
            vmax = max(yt.max(), yp.max())
            fig.add_trace(go.Scatter(
                x=[vmin, vmax], y=[vmin, vmax],
                mode="lines", line=dict(color="gray", dash="dash"),
                showlegend=False,
            ), row=1, col=col)
            fig.update_xaxes(title_text="真实值", row=1, col=col)
            fig.update_yaxes(title_text="预测值", row=1, col=col)
        fig.update_layout(height=400, title_text=f"🎯 {target_var} 预测结果",
                          showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # 历史对比条形图
    if hist:
        df = pd.DataFrame(hist)
        if all(c in df.columns for c in ["model", "R2_test"]):
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df["model"], y=df["R2_test"],
                marker_color="#4F46E5",
                text=df["R2_test"].round(3),
                textposition="outside",
            ))
            fig2.update_layout(
                title="📊 模型历史测试R²对比",
                xaxis_title="模型",
                yaxis_title="R²(测试)",
                height=300,
                yaxis=dict(range=[-0.5, 1.0]),
            )
            st.plotly_chart(fig2, use_container_width=True)
            with st.expander("📋 详细结果", expanded=False):
                st.dataframe(df, use_container_width=True, hide_index=True)

def create_training_page():
    """模型训练页面 — 描述符-性能合并 + 9种算法 + Optuna + K折CV"""
    import optuna, io, zipfile, joblib
    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import KFold, train_test_split
    from modules.descriptor_module import DescriptorCalculator

    MODEL_MAP = {
        'RF': '随机森林 (Random Forest)',
        'ET': '极端随机树 (Extra Trees)',
        'XGB': 'XGBoost',
        'CatBoost': 'CatBoost',
        'LGBM': 'LightGBM',
        'SVM': '支持向量机 (SVR)',
        'KNN': 'K近邻 (KNN)',
        'ANN': '人工神经网络 (MLP)',
        'DNN': '深度神经网络 (Deep MLP)',
    }

    merge_out_dir = Config.OUTPUT_DIR / "training_data"
    merge_out_dir.mkdir(parents=True, exist_ok=True)

    st.title("🧠 模型训练")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>描述符-性能合并 → 自动生成训练数据集 → 9种ML算法 + Optuna + K折CV</p>", unsafe_allow_html=True)

    # ===================== Step 1：描述符-性能合并 =====================
    st.markdown("---")
    st.markdown("### 📦 Step 1：描述符-性能自动合并")
    st.caption("从磁盘CSV加载描述符（rdkit/morgan/mordred/padel）+ 上传性能数据 → 酸酐+二胺等权加和 → 自动生成训练文件")

    desc_dir = Config.OUTPUT_DIR
    desc_files = {
        'rdkit': desc_dir / 'descriptors_rdkit.csv',
        'morgan': desc_dir / 'descriptors_morgan.csv',
        'mordred': desc_dir / 'descriptors_mordred.csv',
        'padel': desc_dir / 'descriptors_padel.csv',
    }
    available_desc = {k: v for k, v in desc_files.items() if v.exists()}

    if not available_desc:
        st.warning("⚠️ 未找到描述符CSV文件，请先在「🧪 描述符计算」页面计算描述符")
    else:
        sel_desc_names = st.multiselect(
            "选择描述符源",
            list(available_desc.keys()),
            default=list(available_desc.keys()),
            key="merge_sel_desc",
            help="从磁盘加载已计算的描述符CSV文件"
        )

    perf_up = st.file_uploader("上传性能 Excel/CSV（需含酸酐SMILES、二胺SMILES和性能列）",
                               type=["csv", "xlsx"], key="merge_perf_up")

    if perf_up is not None and available_desc and sel_desc_names:
        try:
            if perf_up.name.endswith(".xlsx"):
                perf_df = pd.read_excel(perf_up)
            else:
                perf_df = pd.read_csv(perf_up)
            perf_df.columns = perf_df.columns.str.strip()

            all_cols = list(perf_df.columns)
            da_candidates = [c for c in all_cols
                             if '酸酐' in c and 'SMILES' in c] + \
                            [c for c in all_cols
                             if 'dianhydride' in str(c).lower() and 'smiles' in str(c).lower()]
            di_candidates = [c for c in all_cols
                             if '二胺' in c and 'SMILES' in c] + \
                            [c for c in all_cols
                             if 'diamine' in str(c).lower() and 'smiles' in str(c).lower()]

            if not da_candidates or not di_candidates:
                st.error("未找到酸酐SMILES/二胺SMILES列")
            else:
                da_col = da_candidates[0]
                di_col = di_candidates[0]

                perf_num_cols = [c for c in all_cols
                                 if c not in (da_col, di_col)
                                 and pd.api.types.is_numeric_dtype(perf_df[c])]
                if not perf_num_cols:
                    st.warning("性能表中没有检测到数字列")
                else:
                    sel_perf_cols = st.multiselect(
                        "选择要合并的性能目标列",
                        perf_num_cols,
                        default=perf_num_cols[:5],
                        key="merge_sel_perf"
                    )

                    if sel_perf_cols:
                        total_pairs = len(perf_df)
                        total_files = len(sel_desc_names) * len(sel_perf_cols)
                        c1, c2 = st.columns(2)
                        c1.metric("性能表行数", total_pairs)
                        c2.metric("预计生成文件数", total_files)

                        if st.button(f"▶ 生成 {total_files} 个训练文件 → 打包 ZIP",
                                     type="primary", use_container_width=True,
                                     key="merge_gen_btn"):
                            try:
                                calc = DescriptorCalculator()
                                pair_df = perf_df[[da_col, di_col] + sel_perf_cols].copy()

                                all_desc = {}
                                for dn in sel_desc_names:
                                    df = pd.read_csv(available_desc[dn])
                                    if not df.empty:
                                        all_desc[dn] = df

                                combined = calc.combine_monomer_pairs(
                                    descriptor_dfs=all_desc,
                                    pair_df=pair_df,
                                    da_smiles_col=da_col,
                                    di_smiles_col=di_col,
                                    perf_cols=sel_perf_cols,
                                )

                                zip_buf = io.BytesIO()
                                generated = []
                                total_steps = len(sel_desc_names) * len(sel_perf_cols)
                                step = 0
                                pbar = st.progress(0.0)
                                stext = st.empty()
                                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                                    for src, cdf in combined.items():
                                        if cdf.empty:
                                            step += len(sel_perf_cols)
                                            continue
                                        for pc in sel_perf_cols:
                                            step += 1
                                            pbar.progress(step / total_steps)
                                            stext.text(f"⏳ [{step}/{total_steps}] {src} × {pc}...")
                                            if pc not in cdf.columns:
                                                continue
                                            feature_cols = [c for c in cdf.columns
                                                            if c not in (da_col, di_col, *sel_perf_cols)
                                                            and pd.api.types.is_numeric_dtype(cdf[c])]
                                            out_df = cdf[[da_col, di_col] + feature_cols + [pc]].copy()
                                            out_df[feature_cols] = out_df[feature_cols].fillna(0.0)
                                            out_df = out_df.dropna(subset=[pc]).reset_index(drop=True)
                                            if out_df.empty:
                                                continue
                                            fname = f"monomer_sum_{src}_{pc}.csv"
                                            for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                                                fname = fname.replace(ch, '_')
                                            csv_bytes = out_df.to_csv(index=False).encode("utf-8")
                                            zf.writestr(fname, csv_bytes)
                                            generated.append({"文件名": fname, "描述符源": src,
                                                              "性能列": pc, "特征数": len(feature_cols),
                                                              "样本数": len(out_df)})

                                if generated:
                                    with zipfile.ZipFile(zip_buf) as zf:
                                        for g in generated:
                                            data = zf.read(g["文件名"])
                                            (merge_out_dir / g["文件名"]).write_bytes(data)
                                    pbar.empty()
                                    stext.empty()
                                    gen_df = pd.DataFrame(generated)
                                    st.success(f"✅ 已生成 {len(generated)} 个训练文件")
                                    st.dataframe(gen_df, use_container_width=True, hide_index=True)
                                    st.session_state.generated_training_files = generated
                                    zip_buf.seek(0)
                                    st.download_button("📥 ZIP 打包下载", zip_buf,
                                                       f"training_data_{len(generated)}files.zip",
                                                       "application/zip")
                                else:
                                    st.warning("合并后无有效数据，请检查 SMILES 匹配")
                            except Exception as e:
                                st.error(f"合并失败: {e}")
                                import traceback; traceback.print_exc()

                    if st.session_state.get("generated_training_files"):
                        st.markdown("**📁 已生成文件列表**")
                        gdf = pd.DataFrame(st.session_state.generated_training_files)
                        st.dataframe(gdf, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"读取性能表失败: {e}")

    # ===================== Step 2：模型训练 =====================
    st.markdown("---")
    st.markdown("### 🧠 Step 2：模型训练")
    st.caption("从文件夹批量导入训练文件，自动检测目标列，循环训练全部文件")

    input_source = st.radio(
        "选择训练数据来源",
        ["📁 从文件夹批量导入", "📄 上传多个 CSV"],
        horizontal=True, key="train_input_source2"
    )

    input_files = []
    if input_source == "📁 从文件夹批量导入":
        folder_path = st.text_input(
            "训练数据文件夹路径",
            value=str(merge_out_dir),
            key="train_folder_path2"
        )
        folder = Path(folder_path)
        if folder.exists() and folder.is_dir():
            csv_files = sorted(folder.glob("*.csv"))
            if csv_files:
                file_options = {f.name: f for f in csv_files}
                sel_files = st.multiselect(
                    "选择要训练的 CSV 文件",
                    list(file_options.keys()),
                    default=list(file_options.keys())[:5],
                    key="train_folder_files2"
                )
                for fn in sel_files:
                    input_files.append((file_options[fn], fn))
                if input_files:
                    st.info(f"✅ 已选择 {len(input_files)} 个文件")
            else:
                st.info("该文件夹中没有 CSV 文件")
        else:
            st.info("请输入有效的文件夹路径")
    else:
        uploaded = st.file_uploader("上传 CSV 训练数据", type=["csv"],
                                    key="train_csv_upload2", accept_multiple_files=True)
        if uploaded:
            for uf in uploaded:
                input_files.append((uf, uf.name))
            st.info(f"✅ 已上传 {len(input_files)} 个文件")

    if not input_files:
        return

    st.subheader("🔧 模型与优化设置")
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_models = st.multiselect(
            "选择要训练的模型（可选多个）",
            list(MODEL_MAP.keys()),
            default=["RF", "ET", "XGB"],
            key="train_models2"
        )
    with col2:
        n_trials = st.number_input("Optuna 优化次数", 10, 500, 100, step=10,
                                   key="optuna_trials2",
                                   help="每个模型的贝叶斯超参搜索次数")
    with col3:
        test_size = st.slider("测试集比例", 0.05, 0.4, 0.2, 0.05,
                              key="test_ratio2",
                              help="剩余 80% 中 7:2 划分训练/验证")

    with st.expander("⚙️ 高级参数", expanded=False):
        ac1, ac2, ac3 = st.columns(3)
        with ac1:
            early_stop = st.checkbox("启用早停", value=True, key="use_early_stop2")
            val_split = st.slider("验证集比例", 0.1, 0.4, 0.25, 0.05, key="val_ratio2")
        with ac2:
            do_feature_select = st.checkbox("特征选择", value=False, key="use_feat2")
            do_scaling = st.checkbox("特征标准化", value=True, key="use_scaling2")
        with ac3:
            cv_folds = st.number_input("K折CV", 2, 10, 5, key="cv_folds2",
                                       help="Optuna内部使用K折交叉验证评估")
            random_state = st.number_input("随机种子", 0, 9999, 42, key="rs2")

    if not sel_models:
        st.info("请至少选择一个模型")
        return

    if st.button("🚀 开始训练（Optuna 优化 + K折CV）", type="primary",
                 use_container_width=True, key="train_start_btn2"):

        total_file_tasks = len(input_files) * len(sel_models)
        file_task_done = 0
        pbar = st.progress(0.0)
        stext = st.empty()
        all_results = []
        best_models = {}

        for fp, fn in input_files:
            try:
                df = pd.read_csv(fp) if isinstance(fp, (str, Path)) else pd.read_csv(fp)
            except Exception as e:
                st.error(f"❌ {fn} 读取失败: {e}")
                continue

            num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            if not num_cols:
                st.warning(f"⚠️ {fn} 没有数字列，跳过")
                continue
            target_var = num_cols[-1]
            st.info(f"📄 {fn} → 目标: {target_var} ({len(df)} 样本)")

            # 排除所有 SMILES 列和目标列
            drop_cols = [c for c in df.columns if 'SMILES' in c.upper() or c == target_var]
            X_raw = df.drop(columns=drop_cols, errors='ignore')
            X_raw = X_raw.select_dtypes(include=[np.number]).fillna(0)
            y_raw = df[target_var].values

            X_rest, X_test, y_rest, y_test = train_test_split(
                X_raw, y_raw, test_size=test_size, random_state=random_state
            )
            val_ratio_adj = val_split / (1 - test_size)
            X_train, X_val, y_train, y_val = train_test_split(
                X_rest, y_rest, test_size=val_ratio_adj, random_state=random_state
            )
            st.info(f"📊 划分: 训练 {len(X_train)} | 验证 {len(X_val)} | 测试 {len(X_test)}")

            for model_key in sel_models:
                file_task_done += 1
                pbar.progress(file_task_done / total_file_tasks)
                stext.text(f"⏳ [{file_task_done}/{total_file_tasks}] {fn} → {MODEL_MAP[model_key]}...")

                # ---- Optuna 目标函数（K折CV）----
                def objective(trial):
                    mk = model_key
                    params = {}

                    if mk == "RF":
                        params['n_estimators'] = trial.suggest_int('n', 50, 800, step=50)
                        params['max_depth'] = trial.suggest_int('md', 3, 30)
                        params['min_samples_split'] = trial.suggest_int('mss', 2, 20)
                        params['min_samples_leaf'] = trial.suggest_int('msl', 1, 10)
                        from sklearn.ensemble import RandomForestRegressor
                        model_cls = lambda p: RandomForestRegressor(**p, random_state=random_state, n_jobs=-1)
                    elif mk == "ET":
                        params['n_estimators'] = trial.suggest_int('n', 50, 800, step=50)
                        params['max_depth'] = trial.suggest_int('md', 3, 30)
                        params['min_samples_split'] = trial.suggest_int('mss', 2, 20)
                        params['min_samples_leaf'] = trial.suggest_int('msl', 1, 10)
                        from sklearn.ensemble import ExtraTreesRegressor
                        model_cls = lambda p: ExtraTreesRegressor(**p, random_state=random_state, n_jobs=-1)
                    elif mk == "XGB":
                        params['n_estimators'] = trial.suggest_int('n', 50, 800, step=50)
                        params['max_depth'] = trial.suggest_int('md', 3, 15)
                        params['learning_rate'] = trial.suggest_float('lr', 0.01, 0.3, log=True)
                        params['subsample'] = trial.suggest_float('ss', 0.5, 1.0)
                        params['colsample_bytree'] = trial.suggest_float('cbt', 0.5, 1.0)
                        params['reg_alpha'] = trial.suggest_float('ra', 1e-8, 10.0, log=True)
                        params['reg_lambda'] = trial.suggest_float('rl', 1e-8, 10.0, log=True)
                        from xgboost import XGBRegressor
                        model_cls = lambda p: XGBRegressor(**p, random_state=random_state, n_jobs=-1, verbosity=0)
                    elif mk == "CatBoost":
                        params['iterations'] = trial.suggest_int('it', 100, 1000, step=50)
                        params['depth'] = trial.suggest_int('dp', 4, 10)
                        params['learning_rate'] = trial.suggest_float('lr', 0.01, 0.3, log=True)
                        params['l2_leaf_reg'] = trial.suggest_float('l2', 1e-3, 10.0, log=True)
                        from catboost import CatBoostRegressor
                        model_cls = lambda p: CatBoostRegressor(**p, random_seed=random_state, verbose=False)
                    elif mk == "LGBM":
                        params['n_estimators'] = trial.suggest_int('n', 50, 800, step=50)
                        params['max_depth'] = trial.suggest_int('md', 3, 15)
                        params['learning_rate'] = trial.suggest_float('lr', 0.01, 0.3, log=True)
                        params['num_leaves'] = trial.suggest_int('nl', 10, 200)
                        params['subsample'] = trial.suggest_float('ss', 0.5, 1.0)
                        params['reg_alpha'] = trial.suggest_float('ra', 1e-8, 10.0, log=True)
                        from lightgbm import LGBMRegressor
                        model_cls = lambda p: LGBMRegressor(**p, random_state=random_state, n_jobs=-1, verbosity=-1)
                    elif mk == "SVM":
                        params['C'] = trial.suggest_float('C', 0.01, 1000, log=True)
                        params['epsilon'] = trial.suggest_float('eps', 0.001, 1.0, log=True)
                        from sklearn.svm import SVR
                        model_cls = lambda p: SVR(**p)
                    elif mk == "KNN":
                        params['n_neighbors'] = trial.suggest_int('k', 3, 30)
                        params['weights'] = trial.suggest_categorical('w', ['uniform', 'distance'])
                        from sklearn.neighbors import KNeighborsRegressor
                        model_cls = lambda p: KNeighborsRegressor(**p, n_jobs=-1)
                    elif mk in ("ANN", "DNN"):
                        n_layers = trial.suggest_int('layers', 2 if mk == 'DNN' else 1, 4 if mk == 'DNN' else 2)
                        base = trial.suggest_int('base', 64, 256, step=32)
                        hidden = tuple(max(base // (2 ** min(i, 3)), 8) for i in range(n_layers))
                        params['hidden_layer_sizes'] = hidden
                        params['alpha'] = trial.suggest_float('alpha', 1e-7, 0.1, log=True)
                        params['learning_rate_init'] = trial.suggest_float('lr', 0.0001, 0.01, log=True)
                        from sklearn.neural_network import MLPRegressor
                        max_it = 1000 if mk == "DNN" else 500
                        n_iter = 30 if mk == "DNN" else 20
                        model_cls = lambda p: MLPRegressor(**p, activation="relu", max_iter=max_it,
                                                         random_state=random_state, early_stopping=True,
                                                         validation_fraction=0.1, n_iter_no_change=n_iter)
                    else:
                        return -1e10

                    X_tr = X_train.values
                    y_tr = y_train
                    if do_scaling:
                        scl = StandardScaler()
                        X_tr = scl.fit_transform(X_tr)

                    try:
                        kf = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
                        scores = []
                        for tr_idx, va_idx in kf.split(X_tr):
                            X_t, X_v = X_tr[tr_idx], X_tr[va_idx]
                            y_t, y_v = y_tr[tr_idx], y_tr[va_idx]
                            m = model_cls(params)
                            if mk in ("XGB", "CatBoost", "LGBM") and early_stop and len(X_v) > 1:
                                m.fit(X_t, y_t, eval_set=[(X_v, y_v)], verbose=False)
                            else:
                                m.fit(X_t, y_t)
                            scores.append(r2_score(y_v, m.predict(X_v)))
                        return float(np.mean(scores))
                    except Exception:
                        return -1e10

                # 执行 Optuna 优化
                study = optuna.create_study(direction="maximize",
                                            sampler=optuna.samplers.TPESampler(seed=random_state))
                study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

                best_params = study.best_params

                # 最终训练（全量训练 + 验证集）
                X_full = np.vstack([X_train.values, X_val.values])
                y_full = np.concatenate([y_train, y_val])
                if do_scaling:
                    scl = StandardScaler()
                    X_train_sc = scl.fit_transform(X_train.values)
                    X_val_sc = scl.transform(X_val.values)
                    X_test_sc = scl.transform(X_test.values)
                    X_full_sc = scl.fit_transform(X_full)
                else:
                    X_train_sc = X_train.values
                    X_val_sc = X_val.values
                    X_test_sc = X_test.values
                    X_full_sc = X_full

                # 创建最终模型
                final_model = None
                if model_key == "RF":
                    from sklearn.ensemble import RandomForestRegressor
                    final_model = RandomForestRegressor(**best_params, random_state=random_state, n_jobs=-1)
                elif model_key == "ET":
                    from sklearn.ensemble import ExtraTreesRegressor
                    final_model = ExtraTreesRegressor(**best_params, random_state=random_state, n_jobs=-1)
                elif model_key == "XGB":
                    from xgboost import XGBRegressor
                    final_model = XGBRegressor(**best_params, random_state=random_state, n_jobs=-1, verbosity=0)
                elif model_key == "CatBoost":
                    from catboost import CatBoostRegressor
                    final_model = CatBoostRegressor(**best_params, random_seed=random_state, verbose=False)
                elif model_key == "LGBM":
                    from lightgbm import LGBMRegressor
                    final_model = LGBMRegressor(**best_params, random_state=random_state, n_jobs=-1, verbosity=-1)
                elif model_key == "SVM":
                    from sklearn.svm import SVR
                    final_model = SVR(**best_params)
                elif model_key == "KNN":
                    from sklearn.neighbors import KNeighborsRegressor
                    final_model = KNeighborsRegressor(**best_params, n_jobs=-1)
                elif model_key in ("ANN", "DNN"):
                    from sklearn.neural_network import MLPRegressor
                    max_it = 1000 if model_key == "DNN" else 500
                    n_iter = 30 if model_key == "DNN" else 20
                    final_model = MLPRegressor(**best_params, activation="relu", max_iter=max_it,
                                              random_state=random_state, early_stopping=True,
                                              validation_fraction=0.1, n_iter_no_change=n_iter)

                final_model.fit(X_full_sc, y_full)

                y_train_pred = final_model.predict(X_train_sc)
                y_val_pred = final_model.predict(X_val_sc)
                y_test_pred = final_model.predict(X_test_sc)

                r2_train = r2_score(y_train, y_train_pred)
                r2_val = r2_score(y_val, y_val_pred)
                r2_test = r2_score(y_test, y_test_pred)
                rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
                mae_test = mean_absolute_error(y_test, y_test_pred)

                # 保存模型
                safe_name = target_var
                for ch in ['/', '\\', ' ', '*', ':', '?', '"', '<', '>', '|']:
                    safe_name = safe_name.replace(ch, '_')
                model_file = Config.MODEL_DIR / f"{safe_name}_{model_key}.pkl"
                pipeline = {"model": final_model, "scaler": scl if do_scaling else None,
                            "target": target_var, "model_key": model_key,
                            "best_params": best_params, "feature_names": list(X_raw.columns)}
                joblib.dump(pipeline, model_file)

                summary = {"model": model_key, "target": target_var,
                           "R2_train": round(r2_train, 4), "R2_val": round(r2_val, 4),
                           "R2_test": round(r2_test, 4), "RMSE_test": round(rmse_test, 4),
                           "MAE_test": round(mae_test, 4),
                           "train_samples": len(y_train), "val_samples": len(y_val),
                           "test_samples": len(y_test), "features": X_train.shape[1]}
                all_results.append(summary)
                best_models[model_key] = {"model": final_model,
                    "y_train": y_train, "y_train_pred": y_train_pred,
                    "y_val": y_val, "y_val_pred": y_val_pred,
                    "y_test": y_test, "y_test_pred": y_test_pred,
                    "target": target_var}

                st.success(f"✅ {MODEL_MAP[model_key]} | R²(训练)={r2_train:.4f}  R²(验证)={r2_val:.4f}  R²(测试)={r2_test:.4f}")

        # ---- 全部完成 ----
        pbar.empty()
        stext.empty()
        if all_results:
            summary_df = pd.DataFrame(all_results)
            summary_csv = Config.MODEL_DIR / "optuna_all_summary.csv"
            summary_df.to_csv(summary_csv, index=False)

            hist = st.session_state.get("training_history2", [])
            for rec in all_results:
                hist = [r for r in hist if not (r["model"] == rec["model"] and r["target"] == rec["target"])]
                hist.append(rec)
            st.session_state.training_history2 = hist

            st.balloons()
            st.success(f"✅ 全部 {len(all_results)} 个模型训练完成！")
            st.download_button("📥 下载训练摘要 CSV",
                               summary_df.to_csv(index=False).encode("utf-8"),
                               "optuna_all_summary.csv", "text/csv")

            # 散点图
            last_mk = list(best_models.keys())[-1]
            last_m = best_models[last_mk]
            _show_training_comparison(
                hist,
                y_train=last_m["y_train"], y_train_pred=last_m["y_train_pred"],
                y_val=last_m["y_val"], y_val_pred=last_m["y_val_pred"],
                y_test=last_m["y_test"], y_test_pred=last_m["y_test_pred"],
                target_var=last_m["target"],
            )

    # ---- 页面重开时显示历史 ----
    hist = st.session_state.get("training_history2", [])
    if hist:
        _show_training_comparison(hist)

def create_hts_page():
    """高通量筛选页面"""
    st.title("🔍 高通量筛选")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>预测所有二酐-二胺组合的物理化学性能</p>", unsafe_allow_html=True)
    
    # 数据库展示
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(79, 70, 229, 0.3);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.3rem; font-weight: 700;">🧪 分子数据库</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0 0; font-size: 0.9rem;">二酐与二胺分子结构库</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card" style="margin: 0;">
            <h3 style="margin: 0 0 16px 0; color: #4F46E5;">🧪 二酐数据库</h3>
        </div>
        """, unsafe_allow_html=True)
        
        da_df = pd.DataFrame([
            {"名称": k, "SMILES": v[:30] + "..." if len(v) > 30 else v} 
            for k, v in Config.DIANHYDRIDES.items()
        ])
        st.dataframe(da_df, hide_index=True, use_container_width=True)
        
    with col2:
        st.markdown("""
        <div class="card" style="margin: 0;">
            <h3 style="margin: 0 0 16px 0; color: #7C3AED;">🧬 二胺数据库</h3>
        </div>
        """, unsafe_allow_html=True)
        
        di_df = pd.DataFrame([
            {"名称": k, "SMILES": v[:30] + "..." if len(v) > 30 else v} 
            for k, v in Config.DIAMINES.items()
        ])
        st.dataframe(di_df, hide_index=True, use_container_width=True)
    
    total = len(Config.DIANHYDRIDES) * len(Config.DIAMINES)
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border: 1px solid #C7D2FE;
        border-radius: 16px;
        padding: 20px 28px;
        margin: 24px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    ">
        <div>
            <div style="font-size: 1.1rem; font-weight: 600; color: #4F46E5;">组合总数</div>
            <div style="color: #64748B; font-size: 0.85rem;">二酐 × 二胺</div>
        </div>
        <div style="
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        ">{total}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 输出配置
    col1, col2 = st.columns(2)
    
    with col1:
        output_folder = st.text_input("结果保存文件夹", value=str(Config.OUTPUT_DIR))
        
    with col2:
        output_format = st.selectbox("输出格式", ["CSV", "Excel"])
    
    # 开始筛选
    if st.button("🚀 开始高通量筛选", type="primary", use_container_width=True):
        with st.spinner("高通量筛选进行中..."):
            try:
                import random
                
                results = []
                
                for da_name, da_smiles in Config.DIANHYDRIDES.items():
                    for di_name, di_smiles in Config.DIAMINES.items():
                        row = {
                            '二酐': da_name,
                            '二胺': di_name,
                            '二酐SMILES': da_smiles,
                            '二胺SMILES': di_smiles,
                            'Ig(°C)': random.randint(200, 400),
                            '介电常数': round(random.uniform(2.5, 3.5), 2),
                            '透过率(%)': random.randint(60, 90),
                            '拉伸强度(MPa)': random.randint(50, 200),
                        }
                        results.append(row)
                
                df = pd.DataFrame(results)
                
                if output_format == "CSV":
                    output_file = Path(output_folder) / "hts_results.csv"
                    df.to_csv(output_file, index=False)
                else:
                    output_file = Path(output_folder) / "hts_results.xlsx"
                    df.to_excel(output_file, index=False)
                
                st.success(f"筛选完成！共 {len(results)} 种组合")
                st.success(f"结果已保存到: {output_file}")
                
                st.dataframe(df, use_container_width=True)
                st.session_state.hts_results = df
                
            except Exception as e:
                st.error(f"筛选失败: {str(e)}")
    
    # 显示历史结果
    if st.session_state.hts_results is not None:
        st.markdown("---")
        st.subheader("📋 筛选结果")
        
        col1, col2 = st.columns(2)
        
        with col1:
            filter_tg = st.slider("Ig筛选", 150, 450, (200, 400))
            
        with col2:
            filter_dielectric = st.slider("介电常数筛选", 2.0, 4.0, (2.5, 3.5))
        
        filtered_df = st.session_state.hts_results.copy()
        filtered_df = filtered_df[
            (filtered_df['Ig(°C)'] >= filter_tg[0]) & 
            (filtered_df['Ig(°C)'] <= filter_tg[1]) &
            (filtered_df['介电常数'] >= filter_dielectric[0]) & 
            (filtered_df['介电常数'] <= filter_dielectric[1])
        ]
        
        st.dataframe(filtered_df, use_container_width=True)
        
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 下载筛选结果",
            csv,
            "hts_filtered_results.csv",
            "text/csv"
        )


# ==================== 系统设置 ====================
def create_settings_page():
    """系统设置页面"""
    st.title("⚙️ 系统设置")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>配置API和系统参数</p>", unsafe_allow_html=True)
    
    # API配置
    st.markdown("""
    <div class="card">
        <h3 style="margin: 0 0 20px 0;">🔗 API配置</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input("API地址", value=Config.MINIMAX_API)
        
    with col2:
        api_key = st.text_input("API密钥", value=Config.DEFAULT_API_KEY, type="password")
    
    model_name = st.text_input("模型名称", value=Config.MINIMAX_MODEL)
    
    col_test, col_space = st.columns([1, 3])
    with col_test:
        if st.button("🔍 测试连接"):
            try:
                import requests
                resp = requests.get(f"{api_url}/models", 
                                  headers={"Authorization": f"Bearer {api_key}"}, 
                                  timeout=10)
                if resp.status_code == 200:
                    st.success("✅ API连接成功！")
                else:
                    st.warning(f"⚠️ 连接异常: {resp.status_code}")
            except Exception as e:
                st.error(f"❌ 连接失败: {str(e)}")
    
    st.markdown("---")
    
    # 默认参数
    st.markdown("""
    <div class="card">
        <h3 style="margin: 0 0 20px 0;">⚙️ 默认参数</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        expert_count = st.number_input("专家数量", min_value=1, max_value=20, 
                                       value=Config.DEFAULT_EXPERT_COUNT)
        iterations = st.number_input("迭代次数", min_value=100, max_value=20000,
                                    value=Config.DEFAULT_ITERATIONS, step=100)
        
    with col2:
        score_threshold = st.number_input("评分阈值", min_value=0.1, max_value=1.0,
                                         value=Config.DEFAULT_SCORE_THRESHOLD, step=0.1)
        parallel_workers = st.number_input("并行核心数", min_value=1, max_value=16,
                                           value=Config.DEFAULT_PARALLEL_WORKERS)
    
    st.markdown("---")
    
    # 项目路径
    st.markdown("""
    <div class="card">
        <h3 style="margin: 0 0 20px 0;">📁 项目路径</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.text_input("项目根目录", value=str(Config.BASE_DIR), disabled=True)
        
    with col2:
        st.text_input("数据目录", value=str(Config.DATA_DIR), disabled=True)
        
    with col3:
        st.text_input("模型目录", value=str(Config.MODEL_DIR), disabled=True)
    
    st.markdown("---")
    
    # 保存按钮
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 保存配置", type="primary", use_container_width=True):
            config = {
                'api_url': api_url,
                'api_key': api_key,
                'model_name': model_name,
                'expert_count': expert_count,
                'score_threshold': score_threshold,
                'iterations': iterations,
                'parallel_workers': parallel_workers
            }
            
            config_file = Config.BASE_DIR / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            st.success(f"配置已保存到: {config_file}")
    
    with col2:
        if st.button("🔄 重置默认", use_container_width=True):
            st.success("配置已重置为默认值")


# ==================== 使用说明 ====================
def create_help_page():
    """使用说明页面 - 中英双语"""
    lang = st.session_state.get('lang', 'zh')
    
    st.title(t('help_title', lang))
    st.markdown(f"<p style='color: #64748B; margin-bottom: 24px;'>{t('help_subtitle', lang)}</p>", unsafe_allow_html=True)
    
    # 系统概述
    st.markdown(f"## {t('help_overview_title', lang)}")
    st.markdown(t('help_overview', lang))
    
    st.markdown("---")
    
    # 工作流程
    st.markdown(f"## {t('help_workflow_title', lang)}")
    st.markdown(t('help_workflow', lang))
    
    st.markdown("---")
    
    # 模块详细说明
    st.markdown(f"## {t('help_modules_title', lang)}")
    
    tabs_keys = [
        ('help_m_scoring', 'nav_scoring'),
        ('help_m_download', 'nav_download'),
        ('help_m_extraction', 'nav_extraction'),
        ('help_m_smiles', 'nav_smiles'),
        ('help_m_descriptors', 'nav_descriptors'),
        ('help_m_training', 'nav_training'),
        ('help_m_hts', 'nav_hts'),
    ]
    
    tab_labels = [t(k[1], lang) for k in tabs_keys]
    tabs = st.tabs(tab_labels)
    
    for i, (content_key, _) in enumerate(tabs_keys):
        with tabs[i]:
            st.markdown(t(content_key, lang))
    
    st.markdown("---")
    
    # 使用技巧
    st.markdown(f"## {t('help_tips_title', lang)}")
    st.markdown(t('help_tips', lang))
    
    st.markdown("---")
    
    # FAQ
    st.markdown(f"## {t('help_faq_title', lang)}")
    st.markdown(t('help_faq', lang))


# ==================== 主函数 ====================
def main():
    """主函数"""
    init_session_state()
    page = create_sidebar()
    lang = st.session_state.get('lang', 'zh')
    
    # 同步session_state与侧边栏选择
    st.session_state.page = page
    
    # 添加右上角控制栏（语言切换 + 使用说明）
    create_top_right_controls()
    
    # 使用 i18n key 进行路由
    page_key = get_page_key(page, lang)
    
    if page_key == "nav_home":
        create_home_page()
    elif page_key == "nav_scoring":
        create_scoring_page()
    elif page_key == "nav_download":
        create_download_page()
    elif page_key == "nav_extraction":
        create_extraction_page()
    elif page_key == "nav_smiles":
        create_smiles_page()
    elif page_key == "nav_descriptors":
        create_descriptors_page()
    elif page_key == "nav_training":
        create_training_page()
    elif page_key == "nav_hts":
        create_hts_page()
    elif page_key == "nav_settings":
        create_settings_page()
    elif page_key == "nav_help":
        create_help_page()


if __name__ == "__main__":
    main()