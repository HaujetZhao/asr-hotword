# coding: utf-8
import os
import random
from pathlib import Path

def main():
    current_dir = Path(__file__).parent
    chars_file = current_dir / "500字.txt"
    hotword_file = current_dir / "hot.txt"
    test_case_file = current_dir / "test_case.txt"
    
    if not chars_file.exists():
        print(f"找不到 500字.txt: {chars_file}")
        return
        
    with open(chars_file, "r", encoding="utf-8") as f:
        chars = f.read().strip()
        
    if not chars:
        print("500字.txt 为空")
        return
        
    print(f"读取了 {len(chars)} 个常用字")
    
    # 使用固定种子保证可复现
    random.seed(42)
    
    # 1. 生成 10000 个热词 (2-4个字)
    hotwords = set()
    attempts = 0
    while len(hotwords) < 10000 and attempts < 100000:
        attempts += 1
        length = random.randint(2, 4)
        word = "".join(random.choice(chars) for _ in range(length))
        hotwords.add(word)
        
    hotwords_list = sorted(list(hotwords))
    with open(hotword_file, "w", encoding="utf-8") as f:
        for hw in hotwords_list:
            f.write(hw + "\n")
            
    print(f"生成了 {len(hotwords_list)} 个热词，写入到 {hotword_file}")
    
    # 2. 生成 2 条测试句子 (约100字，完全由常用字随机组成，不刻意插入热词)
    test_cases = []
    for _ in range(2):
        sentence = "".join(random.choice(chars) for _ in range(100))
        test_cases.append(sentence)
        
    with open(test_case_file, "w", encoding="utf-8") as f:
        for tc in test_cases:
            f.write(tc + "\n")
            
    print(f"生成了 {len(test_cases)} 条测试句子，写入到 {test_case_file}")

if __name__ == "__main__":
    main()
