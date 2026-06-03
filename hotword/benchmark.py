# coding: utf-8
import time
from pathlib import Path
from hotword.algo_phoneme import get_phoneme_info
from hotword.rag_fast_rf import FastRAG as FastRAG_rf
from hotword.rag_fast_batch import FastRAG as FastRAG_batch
import logging

# 屏蔽 debug 级别的日志，防止 benchmark 输出被日志淹没
logging.basicConfig(level=logging.WARNING)

def load_data():
    current_dir = Path(__file__).parent
    hotword_file = current_dir / "hot.txt"
    test_case_file = current_dir / "test_case.txt"
    
    with open(hotword_file, "r", encoding="utf-8") as f:
        hotwords_raw = [line.strip() for line in f if line.strip()]
        
    with open(test_case_file, "r", encoding="utf-8") as f:
        test_cases = [line.strip() for line in f if line.strip()]
        
    hotwords_dict = {}
    for hw in hotwords_raw:
        phons = get_phoneme_info(hw)
        if phons:
            hotwords_dict[hw] = [phons]
            
    return hotwords_dict, test_cases

def run_test(rag_class, name, hotwords_dict, test_cases):
    print(f"\n[{name}] 初始化并构建索引...")
    start_build = time.perf_counter()
    rag = rag_class(threshold=0.6)
    rag.add_hotwords(hotwords_dict)
    build_time = (time.perf_counter() - start_build) * 1000
    print(f"[{name}] 索引构建耗时: {build_time:.2f}ms")
    
    # 预先将测试句子的音素提取好，避免音素转换耗时影响结果
    test_phonemes_list = []
    for tc in test_cases:
        test_phonemes_list.append(get_phoneme_info(tc))
    
    print(f"[{name}] 开始运行 {len(test_cases)} 个测试用例...")
    start_search = time.perf_counter()
    all_results = []
    for phons in test_phonemes_list:
        res = rag.search(phons, top_k=10)
        all_results.append(res)
    search_time = (time.perf_counter() - start_search) * 1000
    
    avg_time = search_time / len(test_cases)
    print(f"[{name}] 检索总耗时: {search_time:.2f}ms, 平均每条: {avg_time:.2f}ms")
    
    return all_results, build_time, avg_time

def main():
    hotwords_dict, test_cases = load_data()
    print(f"加载热词数: {len(hotwords_dict)}, 测试句子数: {len(test_cases)}")
    
    results_rf, build_rf, avg_rf = run_test(FastRAG_rf, "rag_fast_rf (方案一)", hotwords_dict, test_cases)
    
    try:
        results_v2, build_v2, avg_v2 = run_test(FastRAG_batch, "rag_fast_batch (批量全局版)", hotwords_dict, test_cases)
    except Exception as e:
        print(f"\n[Error] rag_fast_batch 运行出错: {e}")
        import traceback
        traceback.print_exc()
        return

    # 比对结果一致性
    diff_count = 0
    for idx, (res_rf, res_v2) in enumerate(zip(results_rf, results_v2)):
        if res_rf != res_v2:
            diff_count += 1
            if diff_count <= 5:
                print(f"\n差异用例 {diff_count} (第 {idx} 条句子): '{test_cases[idx]}'")
                print(f"  rf 的结果: {res_rf}")
                print(f"  batch 的结果: {res_v2}")
                
    if diff_count == 0:
        print("\n[OK] 方案一与方案二检索结果完全一致！")
    else:
        print(f"\n[Warning] 存在 {diff_count} / {len(test_cases)} 个句子的检索结果不一致！")

if __name__ == "__main__":
    main()
