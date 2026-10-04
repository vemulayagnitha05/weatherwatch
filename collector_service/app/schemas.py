from pydantic import BaseModel, Field

class CollectRequest(BaseModel):
    city_id: int | None = Field(default=None, ge=1)
