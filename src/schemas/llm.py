from pydantic import BaseModel, ConfigDict, Field


class LLMCreateSchema(BaseModel):
    model_name: str

    model_config = ConfigDict(from_attributes=True)


class LLMReadSchema(LLMCreateSchema):
    id: int


class LLMUpdateSchema(BaseModel):
    id: int
    model_name: str | None = Field(default=None, examples=[None])
