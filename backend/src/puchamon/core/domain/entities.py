"""core domain entities for the Puchamon application."""

from beanie import Document
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseEntity(Document):
    id: str | None = Field(default=None, alias="_id")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class BaseEmbeddedModel(BaseModel):
    """Base model for nested payloads to handle camelCase translation."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
