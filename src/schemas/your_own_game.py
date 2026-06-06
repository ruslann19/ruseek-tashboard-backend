from datetime import date

from pydantic import BaseModel, ConfigDict


class YourOwnGameMetadata(BaseModel):
    source_url: str
    published_date: date

    model_config = ConfigDict(from_attributes=True)
