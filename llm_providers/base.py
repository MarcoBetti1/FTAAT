from abc import ABC, abstractmethod
from typing import Callable

class LLMProvider(ABC):
    """
    Common interface every backend must expose.
    """

    #: Human-readable name shown in result-file paths
    provider_id: str
    #: Model identifier you want the backend to use (e.g. 'gpt-3.5-turbo')
    model_name: str

    # -------- runtime behaviour --------
    @abstractmethod
    def query(self, 
    prompt: str,
    *, 
    temperature: float = 0.0,
    max_tokens: int | None = None,   
    timeout:    int | None = None   
    ) -> str:
        ...

    # -------- tokenisation helpers --------
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        ...

    #: Path of the single-token JSON file that *matches the tokenizer above*
    token_set_path: str
