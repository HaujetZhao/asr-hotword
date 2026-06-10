# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

音素级热词纠错库，从 CapsWriter-Offline 抽离为独立包。通过音素模糊匹配实现语音识别结果的热词替换和纠错，支持中文（前后鼻音、平翘舌等相似音素）和英文（字符级 LCS 相似度）。

## 架构

两层检索架构：

1. **FastRAG**（粗筛）— rapidfuzz C++ 批量匹配 + 掩码剥离多位置召回，快速过滤候选
2. **AccuRAG**（精筛）— 模糊音权重编辑距离 + 字边界约束，精确匹配

### 模块职责

| 模块 | 职责 |
|---|---|
| `algo_phoneme.py` | 文本→音素序列转换，`Phoneme` 数据模型，pypinyin 封装 |
| `algo_calc.py` | 相似度算法：LCS、音素编辑距离、相似音素集 |
| `rag_fast.py` | `PhonemeEncoder` 编码器 + 纯 Python 倒排索引基线实现 |
| `rag_fast_rf.py` | 与 `rag_fast.py` 同接口，用 rapidfuzz C++ 后端加速 |
| `rag_fast_batch.py` | 全局批量版 FastRAG，用 `rapidfuzz.process.extract` 一次性粗筛 + 掩码剥离多处匹配 |
| `rag_accu.py` | `AccuRAG` — 含模糊音权重的精确匹配 |
| `hot_phoneme.py` | `PhonemeCorrector` — 编排 FastRAG+AccuRAG 的主纠错器（当前默认使用 `rag_fast_batch`） |
| `benchmark.py` | 对比 `rag_fast_rf` 与 `rag_fast_batch` 的性能和结果一致性 |
| `gen_test_data.py` | 生成随机热词和测试用例数据 |

### 音素模型

`Phoneme` 是核心数据模型，属性：`value`（音素值）、`lang`（zh/en/num/other）、`is_word_start/end`（字边界）、`char_start/end`（原文位置）。中文音素拆为 `[声母, 韵母, 声调]` 三元组。

相似音素编码了中文常见语音混淆（前后鼻音、平翘舌、鼻边音、唇齿音等）。

### 热词文件格式

- `hot.txt`：每行一个热词，支持 `|` 分隔别名（如 `Claude | Cloud`）。
- **黑名单支持**：支持使用 `~~~` 声明邻近黑名单，例如 `傅平 ~~~ 工作 | 精准 | 脱贫`。在 `correct(text, blacklist_window=5)` 替换时，如果在被替换原词周围 `blacklist_window`（默认5个语义词，包含每个CJK汉字、英文单词或数字）内出现了黑名单中的词，则拦截该替换。

## 依赖

- **必须**: `pypinyin` — 中文音素转换
- **必须**: `rapidfuzz` — FastRAG 默认后端（`rag_fast_batch`），C++ 加速

## 开发命令

```bash
# 安装依赖
pip install pypinyin rapidfuzz

# 运行模块测试（各模块自带 __main__）
python -m hotword.algo_phoneme
python -m hotword.algo_calc
python -m hotword.rag_fast
python -m hotword.rag_fast_rf
python -m hotword.rag_fast_batch
python -m hotword.rag_accu
python -m hotword.hot_phoneme

# 性能对比（rag_fast_rf vs rag_fast_batch）
python -m hotword.benchmark

# 快速使用
python -c "from hotword import PhonemeCorrector; c = PhonemeCorrector(); c.update_hotwords('CapsWriter'); print(c.correct('use caps riter to type'))"
```
