"""
Day 54 课后作业 1（基础巩固）：基础巩固：生成 Ollama Modelfile 封装微调后的 GGUF 模型
工单：STARMIND-054
"""

def render_ollama_modelfile(gguf_path: str, system_prompt: str, temperature: float = 0.3) -> str:
    return (
        f"FROM {gguf_path}\n"
        f"PARAMETER temperature {temperature}\n"
        f"PARAMETER num_ctx 4096\n"
        f'SYSTEM """{system_prompt}"""\n'
    )


print(render_ollama_modelfile("./starmind-7b-q4_k_m.gguf", "你是杭州星辰数科官方客服助手。"))

