from enum import Enum
from typing import List


class ListedEnum(str, Enum):
    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.value, cls))
