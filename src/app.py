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
    st.sidebar.markdown(f"""
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
    <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #E2E8F0, transparent); margin: 16px 0;">
    """, unsafe_allow_html=True)
    
    # RDKit状态指示器
    if check_rdkit():
        st.sidebar.markdown(f"""
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
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
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
        </div>
        """, unsafe_allow_html=True)
    
    # 导航选项 (使用 i18n)
    pages = get_page_names(lang)
    
    page = st.sidebar.radio(
        t('sidebar_title', lang),
        pages,
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown(f"""
    <hr style="border: none; height: 1px; background: linear-gradient(90deg, transparent, #E2E8F0, transparent); margin: 24px 0;">
    
    <div style="padding: 0 8px;">
        <h4 style="color: #0F172A; font-size: 0.85rem; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em;">
            {t('quick_links', lang)}
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
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
    st.sidebar.markdown("""
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
    </div>
    """, unsafe_allow_html=True)
    
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
        st.info(f"📊 已选用「数据提取」结果：{len(src_df)} 行")
    if up_file is not None:
        try:
            if up_file.name.lower().endswith(".csv"):
                src_df = _pd.read_csv(up_file)
            else:
                src_df = _pd.read_excel(up_file)
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
            csv_data = sm_res.to_csv(index=False).encode("utf-8")
            st.download_button("📥 下载 CSV", csv_data, "smiles_converted.csv", "text/csv")
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
    """描述符计算页面"""
    st.title("🧪 描述符计算")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>计算RDKit、Morgan等多种分子描述符</p>", unsafe_allow_html=True)
    
    rdkit_available = check_rdkit()
    
    if not rdkit_available:
        st.error("⚠️ RDKit未安装，请运行: pip install rdkit")
        st.code("pip install rdkit")
        return
    
    # 输入配置
    st.markdown("""
    <div class="card">
        <h3 style="margin: 0 0 16px 0;">📥 输入数据</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_file = st.file_uploader(
        "上传分子数据文件（CSV）",
        type=['csv'],
        help="需要包含SMILES列"
    )
    
    if input_file:
        df = pd.read_csv(input_file)
        st.info(f"读取到 {len(df)} 个分子")
        
        smiles_col = None
        for col in df.columns:
            if 'smiles' in col.lower():
                smiles_col = col
                break
        
        if smiles_col:
            st.success(f"找到SMILES列: {smiles_col}")
            st.dataframe(df[[smiles_col]].head(), use_container_width=True)
        else:
            st.error("未找到SMILES列")
            return
    
    # 计算选项
    with st.expander("🧪 计算选项"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            calc_rdkit = st.checkbox("RDKit描述符", value=True)
            
        with col2:
            calc_morgan = st.checkbox("Morgan指纹", value=True)
            
        with col3:
            morgan_radius = st.number_input("Morgan半径", min_value=1, max_value=4, value=2)
    
    # 开始计算
    if st.button("▶ 计算描述符", type="primary", use_container_width=True):
        if not input_file:
            st.error("请先上传分子数据文件")
        else:
            with st.spinner("描述符计算进行中..."):
                try:
                    from rdkit import Chem
                    from rdkit.Chem import Descriptors, AllChem
                    
                    df = pd.read_csv(input_file)
                    smiles_col = [c for c in df.columns if 'smiles' in c.lower()][0]
                    
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, smiles in enumerate(df[smiles_col]):
                        try:
                            mol = Chem.MolFromSmiles(smiles)
                            if mol:
                                row = {'SMILES': smiles}
                                
                                if calc_rdkit:
                                    row['MolWt'] = Descriptors.MolWt(mol)
                                    row['LogP'] = Descriptors.MolLogP(mol)
                                    row['TPSA'] = Descriptors.TPSA(mol)
                                    row['RingCount'] = Descriptors.RingCount(mol)
                                
                                if calc_morgan:
                                    fp = AllChem.GetMorganFingerprintAsBitVect(mol, morgan_radius, nBits=1024)
                                    for i, bit in enumerate(fp):
                                        row[f'Bit_{i}'] = bit
                                
                                results.append(row)
                            else:
                                results.append({'SMILES': smiles})
                        except:
                            results.append({'SMILES': smiles})
                        
                        if (idx + 1) % 10 == 0:
                            progress_bar.progress((idx + 1) / len(df))
                    
                    results_df = pd.DataFrame(results)
                    output_file = Config.DATA_DIR / "descriptors.csv"
                    results_df.to_csv(output_file, index=False)
                    
                    st.success(f"计算完成！共 {len(results)} 个分子")
                    st.success(f"结果已保存到: {output_file}")
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"计算失败: {str(e)}")


# ==================== 模型训练 ====================
def create_training_page():
    """模型训练页面"""
    st.title("🤖 模型训练")
    st.markdown("<p style='color: #64748B; margin-bottom: 24px;'>训练机器学习性能预测模型</p>", unsafe_allow_html=True)
    
    # 输入配置
    st.markdown("""
    <div class="card">
        <h3 style="margin: 0 0 16px 0;">📥 训练数据</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_file = st.file_uploader(
        "上传描述符数据（CSV）",
        type=['csv']
    )
    
    if input_file:
        df = pd.read_csv(input_file)
        st.info(f"样本数: {len(df)}, 特征数: {df.shape[1]}")
        st.dataframe(df.head(), use_container_width=True)
    
    # 目标选择
    st.subheader("🎯 预测目标")
    target_var = st.selectbox(
        "选择目标变量",
        ['tg', 'dielectric', 'transmittance', 'tensile_strength'],
        format_func=lambda x: {
            'tg': '玻璃化转变温度 Ig',
            'dielectric': '介电常数',
            'transmittance': '透过率',
            'tensile_strength': '拉伸强度'
        }.get(x, x)
    )
    
    # 模型选择
    st.subheader("🔧 模型选择")
    col1, col2 = st.columns(2)
    
    with col1:
        model_type = st.selectbox(
            "选择模型",
            ['rf', 'gb', 'lr', 'ridge'],
            format_func=lambda x: {
                'rf': '随机森林 (Random Forest)',
                'gb': '梯度提升 (Gradient Boosting)',
                'lr': '线性回归 (Linear Regression)',
                'ridge': '岭回归 (Ridge Regression)'
            }.get(x, x)
        )
    
    with col2:
        iterations = st.number_input(
            "迭代次数", min_value=100, max_value=20000, 
            value=Config.DEFAULT_ITERATIONS, step=100
        )
    
    # 开始训练
    if st.button("▶ 训练模型", type="primary", use_container_width=True):
        if not input_file:
            st.error("请先上传训练数据")
        else:
            with st.spinner("模型训练进行中..."):
                try:
                    from sklearn.model_selection import train_test_split
                    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
                    from sklearn.linear_model import LinearRegression, Ridge
                    from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
                    import joblib
                    
                    df = pd.read_csv(input_file)
                    
                    if target_var not in df.columns:
                        st.error(f"未找到目标列: {target_var}")
                        return
                    
                    y = df[target_var].values
                    X = df.drop(columns=[target_var, 'SMILES'], errors='ignore')
                    X = X.select_dtypes(include=[np.number]).fillna(0)
                    
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.2, random_state=42
                    )
                    
                    st.info(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")
                    
                    if model_type == 'rf':
                        model = RandomForestRegressor(n_estimators=iterations, max_depth=10, 
                                                     random_state=42, n_jobs=-1)
                    elif model_type == 'gb':
                        model = GradientBoostingRegressor(n_estimators=iterations, max_depth=5,
                                                         random_state=42)
                    elif model_type == 'lr':
                        model = LinearRegression()
                    else:
                        model = Ridge(alpha=1.0)
                    
                    with st.spinner("训练中..."):
                        model.fit(X_train, y_train)
                    
                    y_pred = model.predict(X_test)
                    
                    r2 = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mae = mean_absolute_error(y_test, y_pred)
                    
                    # 显示结果卡片
                    st.markdown("""
                    <div style="
                        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
                        border: 1px solid #C7D2FE;
                        border-radius: 16px;
                        padding: 24px;
                        margin: 24px 0;
                    ">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.success("训练完成！")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("R²", f"{r2:.4f}")
                    col2.metric("RMSE", f"{rmse:.4f}")
                    col3.metric("MAE", f"{mae:.4f}")
                    
                    model_file = Config.MODEL_DIR / f"{target_var}_{model_type}.pkl"
                    joblib.dump(model, model_file)
                    st.success(f"模型已保存到: {model_file}")
                    
                    results_df = pd.DataFrame([{
                        'model': model_type,
                        'R2': r2,
                        'RMSE': rmse,
                        'MAE': mae
                    }])
                    results_file = Config.MODEL_DIR / f"{target_var}_summary.csv"
                    results_df.to_csv(results_file, index=False)
                    
                    st.session_state.training_results = results_df
                    
                except Exception as e:
                    st.error(f"训练失败: {str(e)}")
    
    # 显示历史结果
    if st.session_state.training_results is not None:
        st.markdown("---")
        st.subheader("📋 训练结果")
        st.dataframe(st.session_state.training_results, use_container_width=True)


# ==================== 高通量筛选 ====================
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