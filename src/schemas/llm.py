from pydantic import BaseModel, ConfigDict, Field


class LlmCreateSchema(BaseModel):
    llm_name: str

    model_config = ConfigDict(from_attributes=True)


class LlmReadSchema(LlmCreateSchema):
    id: int


class LlmUpdateSchema(BaseModel):
    id: int
    llm_name: str | None = Field(default=None, examples=[None])
