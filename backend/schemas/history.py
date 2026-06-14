from pydantic import BaseModel


class BatchDeleteRequest(BaseModel):
    ids: list[int]
