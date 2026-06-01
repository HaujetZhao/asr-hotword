# hotword

音素级热词纠错库，用于语音识别结果的后处理，基于音素编辑距离进行热词替换，5000条热词处理一条句子也仅需20ms。

从 [CapsWriter-Offline](https://github.com/HaujetZhao/CapsWriter-Offline) 抽离的独立组件，支持中英文混合纠错。

目前只实现了中文和英文热词，中文用拼音（声母、韵母、音调）作为音素，英文用字母作为音素，架构上也可以扩展其它语言的实现，但我还不了解其它语言如日文、韩文、俄文、泰语等如何转为音素。

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
print(result.matchs)    # [('caps riter offline', 'CapsWriter-Offline', 0.9411764705882353)] 

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
result = pc.correct(text, k=10)  # 执行纠错，k=候选数量
```

`CorrectionResult` 包含：
- `.text` — 纠错后的文本
- `.matchs` — `[(原始片段, 热词, 分数), ...]` 实际被替换的项
- `.similars` — `[(原始片段, 热词, 分数), ...]` 相似候选

## 热词文件格式

`hot.txt`，每行一个热词，`|` 分隔别名（用于匹配不同读法）：

```
CapsWriter | Caps Rider
Claude | 克劳德 | 克劳得 | cloud
config_client.py | config_client 点 py
```

- `#` 开头的行为注释
- 热词具备强制性，相似度高于阈值一定会被替换
