from pydantic import BaseModel, ConfigDict, Field


class LLMCreateSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class LLMReadSchema(LLMCreateSchema):
    id: int


class LLMUpdateSchema(BaseModel):
    id: int
    name: str | None = Field(default=None, examples=[None])
