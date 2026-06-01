# coding: utf-8
"""
热词纠错测试脚本

用法：
    python demo.py
    python demo.py test_cases.txt   # 指定测试用例文件
"""

import sys
import time
from pathlib import Path
from hotword import PhonemeCorrector

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_text(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"[错误] 文件不存在: {path}")
        sys.exit(1)
    return p.read_text(encoding='utf-8')


def load_test_cases(path: str) -> list[str]:
    cases = []
    for line in load_text(path).splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            cases.append(line)
    return cases


def test():
    hot_content = load_text('hot.txt')

    # 初始化
    pc = PhonemeCorrector(threshold=0.85)
    n_hw = pc.update_hotwords(hot_content)

    print(f"热词 {n_hw} 个")
    print()

    # 读取测试用例
    test_file = sys.argv[1] if len(sys.argv) > 1 else 'test_cases.txt'
    cases = load_test_cases(test_file)

    for text in cases:
        t0 = time.perf_counter()
        result = pc.correct(text)
        t_ms = (time.perf_counter() - t0) * 1000

        print(f"  原始: {text}")
        print(f"  结果: {result.text}", end="")

        has_change = result.text != text

        if has_change:
            print("  ✓")
        else:
            print("  （无变化）")

        for wrong, right, score in result.matches:
            print(f"        替换  {wrong} → {right}  ({score:.2f})")

        for origin, hw, score in result.similars:
            if (origin, hw, score) not in result.matches:
                print(f"        候选  {origin} → {hw}  ({score:.2f})")

        print(f"        耗时  {t_ms:.1f}ms")
        print()


if __name__ == '__main__':
    test()
