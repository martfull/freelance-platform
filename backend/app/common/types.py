from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
TaskId = NewType("TaskId", UUID)
ContractId = NewType("ContractId", UUID)
FileId = NewType("FileId", UUID)
