def count_gpt_tokens(text: str) -> int:
    """Return how many tokens `text` uses under the GPT-3.5 (or GPT-4) tokenizer."""
    return len(encoding.encode(text))

def query_gpt(prompt: str, model: str = MODEL_NAME, temperature: float = 0.0) -> str:
    """
    Calls OpenAI's ChatCompletion API with the given prompt,
    returns the assistant's message content.
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Respond with only the correct answer on each line."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature
    )
    return response["choices"][0]["message"]["content"].strip()