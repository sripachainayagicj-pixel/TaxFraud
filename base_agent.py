from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        pass

