from run_experiments import run_experiments

# # 1 — OpenAI
# run_experiments("llm_providers.openai_llm.OpenAIProvider",
#                 facts_list_sizes=[3, 6], token_sizes=[2, 3],trials=1,output_root="results/openai")

# 2 — DeepSeek
# run_experiments("llm_providers.deepseek_llm.DeepSeekProvider",
#                 facts_list_sizes=[3, 6], token_sizes=[2, 3],trials=1,output_root="results/deepseek")

# # 3 — local llama3.2 via Ollama
# run_experiments("llm_providers.ollama_llm.OllamaProvider",
#                 facts_list_sizes=[3, 6], token_sizes=[2, 3],trials=1,output_root="results/llama3")