# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

音素级热词纠错库，从 CapsWriter-Offline 抽离为独立包。通过音素模糊匹配实现语音识别结果的热词替换和纠错，支持中文（前后鼻音、平翘舌等相似音素）和英文（字符级 LCS 相似度）。

## 架构

两层检索架构：

1. **FastRAG**（粗筛）— 倒排索引 + 锚点扫描 + 编辑距离，快速过滤候选
2. **AccuRAG**（精筛）— 模糊音权重编辑距离 + 字边界约束，精确匹配

### 模块职责

| 模块 | 职责 |
|---|---|
| `algo_phoneme.py` | 文本→音素序列转换，`Phoneme` 数据模型，pypinyin 封装 |
| `algo_calc.py` | 相似度算法：LCS、音素编辑距离、相似音素集 |
| `rag_fast.py` | 倒排索引 `PhonemeIndex` + 纯 Python DP 检索 |
| `rag_fast_rf.py` | 与 `rag_fast.py` 同接口，用 rapidfuzz C++ 后端加速 |
| `rag_accu.py` | `AccuRAG` — 含模糊音权重的精确匹配 |
| `hot_phoneme.py` | `PhonemeCorrector` — 编排 FastRAG+AccuRAG 的主纠错器 |

### 音素模型

`Phoneme` 是核心数据模型，属性：`value`（音素值）、`lang`（zh/en/num/other）、`is_word_start/end`（字边界）、`char_start/end`（原文位置）。中文音素拆为 `[声母, 韵母, 声调]` 三元组。

相似音素编码了中文常见语音混淆（前后鼻音、平翘舌、鼻边音、唇齿音等）。

### 热词文件格式

- `hot.txt`：每行一个热词，支持 `|` 分隔别名（如 `Claude | Cloud`）

## 依赖

- **必须**: `pypinyin` — 中文音素转换
- **加速**: `rapidfuzz` — FastRAG-rf 变体需要

## 开发命令

```bash
# 安装依赖
pip install pypinyin rapidfuzz

# 运行模块测试（各模块自带 __main__）
python -m hotword.algo_phoneme
python -m hotword.algo_calc
python -m hotword.rag_fast
python -m hotword.rag_fast_rf
python -m hotword.rag_accu
python -m hotword.hot_phoneme

# 快速使用
python -c "from hotword import PhonemeCorrector; c = PhonemeCorrector(); c.update_hotwords('CapsWriter'); print(c.correct('use caps riter to type'))"
```
