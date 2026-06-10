# ASR-Hotword

音素级热词纠错库，用于语音识别结果的后处理。基于音素编辑距离进行热词替换，5000条热词处理一条句子也仅需20ms，另可通过「别名」实现难拼词的替换。

从 [CapsWriter-Offline](https://github.com/HaujetZhao/CapsWriter-Offline) 抽离的独立组件，支持中英文混合纠错。


语音识别对一些**非常见词**（如人名、品牌名、专业术语）经常识别不准。例如 `CapsWriter` 可能被识别成 `Caps rider`，`Claude` 可能被识别成 `cloud`，欲输入 `Qwen` 但读音是 `千问`。热词功能就是用来修正这类错误。

工作原理：

1. 将热词和识别文本都转为音素序列
2. 通过 FastRAG + AccuRAG 两层检索找到相似片段
3. 相似度超过阈值则替换

中文以拼音的声母、韵母、音调作为音素单元，支持相似音素匹配（前后鼻音、平翘舌等）。英文以字母作为音素单元，支持 LCS 模糊匹配。架构上也支持扩展其他语言。

热词的语法为每行一个的 `目标词 | 别名1 | 别名2 | 别名N ~~~ 黑名单1 | 黑名单2 | 黑名单N ` ，只要目标词或任一别名的音素与句中的部分匹配了，就会强制替换为目标词，当替换目标周围有黑名单词语时，则不替换。例如 `傅平 ~~~ 工作 | 精准 | 脱贫` 可以防止把 `扶贫办工作人员` 错误地替换为 `傅平办工作人员`。

热词的第一个词不一定是 `纠正目标`，也可以是**希望输入的内容**，后面跟触发别名。这样就可以用作 `自定义短语` 用语音快速输入长文本：

```text
18200006666 | 我的手机号 | input my phone
上海市浦东新区张江高科技园区 | input my address
hello@example.com | 我的邮箱 | input my email
```

说 `我的手机号` 或 `input my phone`，都会自动替换为 `18200006666`。`|` 分隔的多个写法只要音素相似均可触发，实际替换为第一个词。

## 安装依赖

```bash
pip install pypinyin rapidfuzz
```

## 快速上手

```python
from hotword import PhonemeCorrector

hotwords = """
CapsWriter | Caps Rider | Caps Right
CapsWriter-Offline | Caps Right Offline
Claude | 克劳德 | 克劳得 | cloud
Claude Code | cloud cold | cloud code
PyTorch
如臂使指
"""

# 音素纠错
pc = PhonemeCorrector(threshold=0.85)  # 以85%的相似度作为替换阈值
pc.update_hotwords(hotwords)

result = pc.correct("用 caps riter offline 来打字")
print(result.text)      # 用 CapsWriter-Offline 来打字
print(result.matches)    # [('caps riter offline', 'CapsWriter-Offline', 0.9411764705882353)] 

```

## 实例测试

本 repo 提供了预置热词文件 [hot.txt](./hot.txt) 与测试用例 [test_cases.txt](./test_cases.txt) ，可以直接运行 [demo.py](./demo.py) 查看效果

```bash
python demo.py
python demo.py test_cases.txt   # 指定自定义测试用例
```


```text
热词 44 个

  原始: cloud cold 是一个编程工具
  结果: Claude Code 是一个编程工具  ✓
        替换  cloud cold → Claude Code  (1.00)
        候选  cloud → Claude  (1.00)
        耗时  1.5ms

  原始: 你可以用 Cloud 改一下
  结果: 你可以用 Claude 改一下  ✓
        替换  Cloud → Claude  (1.00)
        耗时  0.8ms

  原始: 克劳得最近的估值特别牛逼
  结果: Claude最近的估值特别牛逼  ✓
        替换  克劳得 → Claude  (1.00)
        耗时  0.8ms

  原始: 用 caps riter offline 是一个 windows 上面的语音输入工具
  结果: 用 CapsWriter-Offline 是一个 windows 上面的语音输入工具  ✓
        替换  caps riter offline → CapsWriter-Offline  (0.94)
        候选  caps riter → CapsWriter  (0.90)
        候选  音输 → 音素  (0.83)
        耗时  1.9ms

  原始: 我想下载 py torch 来训练模型
  结果: 我想下载 PyTorch 来训练模型  ✓
        替换  py torch → PyTorch  (1.00)
        耗时  0.7ms

  原始: 如壁使指般流畅
  结果: 如臂使指般流畅  ✓
        替换  如壁使指 → 如臂使指  (1.00)
        耗时  0.6ms

  原始: 用 kuda 来加速训练
  结果: 用 CUDA 来加速训练  ✓
        替换  kuda → CUDA  (1.00)
        耗时  0.5ms

  原始: 拉马点 CPP 部署模型
  结果: Llama.cpp 部署模型  ✓
        替换  拉马点 CPP → Llama.cpp  (1.00)
        耗时  0.6ms

  原始: 我家哥哥真可爱，小黑子走开
  结果: 我家鸽鸽真可爱，小黑子走开  ✓
        替换  我家哥哥 → 我家鸽鸽  (1.00)
        耗时  0.7ms

  原始: 我的手机号
  结果: 185xxxxxxxx  ✓
        替换  我的手机号 → 185xxxxxxxx  (1.00)
        候选  我的手机 → 129xxxxxxxx@qq.com  (0.71)
        耗时  0.6ms

  原始: 我的邮箱
  结果: 129xxxxxxxx@qq.com  ✓
        替换  我的邮箱 → 129xxxxxxxx@qq.com  (1.00)
        耗时  0.7ms

  原始: 把 config client  发给我
  结果: 把 config_client.py  发给我  ✓
        替换  config client → config_client.py  (1.00)
        耗时  1.7ms

  原始: 说明文件点 md
  结果: 说明文件.md  ✓
        替换  点 md → .md  (1.00)
        候选  md → .md  (1.00)
        耗时  0.5ms

  原始: 这是一句没有命中的话
  结果: 这是一句没有命中的话  （无变化）
        候选  一句 → 音素  (0.67)
        耗时  0.6ms
```

## API

### PhonemeCorrector

```python
pc = PhonemeCorrector(threshold=0.85, similar_threshold=None)
```

- **threshold**: 替换阈值，相似度高于此值才执行替换，默认 0.85
- **similar_threshold**: 相似候选阈值，低于 threshold 但高于此值只记录不替换，默认 `threshold - 0.2`

```python
pc.update_hotwords(text)       # 从字符串加载热词
result = pc.correct(text, k=10, blacklist_window=5)  # 执行纠错，k=候选数量，blacklist_window=邻近黑名单检测语义词数窗口（中文字符、英文单词或数字）
```

`CorrectionResult` 包含：
- `.text` — 纠错后的文本
- `.matches` — `[(原始片段, 热词, 分数), ...]` 实际被替换的项
- `.similars` — `[(原始片段, 热词, 分数), ...]` 相似候选

## 热词文件格式

每行一个热词，`|` 分隔别名，第一个词是替换目标，后面的词是触发写法。

### 1. 基础别名格式

```text
# 注释：CapsWriter 的几种常见误识别
CapsWriter | Caps Rider | Caps Right
Claude | 克劳德 | 克劳得 | cloud
config_client.py | config_client 点 py
```

- `#` 开头的行为注释
- 热词具备强制性，相似度高于阈值一定会被替换

### 2. 邻近黑名单拦截格式（防误杀）

支持使用 `~~~` 分隔后声明邻近黑名单词（也用 `|` 分隔）。当要替换的区间左右邻近一定词数内（通过 `correct(text, blacklist_window=5)` 指定，默认5个词）出现了黑名单词语时，拦截不替换（中文字符算作1词，英文单词算作1词，连续数字算作1词，忽略空格和标点）：

```text
# 只有在周围 5 个语义词内没有出现 "扶贫"、"精准" 或 "脱贫" 的时候，才允许将 fuping 替换为 傅平
傅平  ~~~ 扶贫 | 精准 | 脱贫
```
