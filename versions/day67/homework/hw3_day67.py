"""
Day 67 课后作业 3（架构进阶）：架构进阶：计算 7B 模型单请求 KV Cache 显存占用（MB）
工单：STARMIND-067
"""

def calc_kv_cache_mb(layers: int = 28, kv_heads: int = 4, head_dim: int = 128, seq_len: int = 4096, dtype_bytes: int = 2) -> float:
    total_bytes = 2 * layers * kv_heads * head_dim * seq_len * dtype_bytes
    return round(total_bytes / (1024 ** 2), 2)


mb = calc_kv_cache_mb()
assert mb == 224.0
print(f"Qwen2.5-7B (GQA 4 KV-heads) 4K 上下文单请求 KV Cache = {mb} MB")

