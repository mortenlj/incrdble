from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AliasPath, RootModel, model_validator
from pydantic.alias_generators import to_camel


class Property(BaseModel):
    name: str
    description: Optional[str] = ""
    type: Optional[str] = ""
    properties: Optional["Properties"] = Field(default_factory=list)
    required: Optional[list[str]] = Field(default_factory=list)


class Properties(RootModel):
    root: list[Property] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def validate_root(cls, value):
        if not value:
            return
        properties = []
        for k, prop in value.items():
            prop["name"] = k
            properties.append(Property(**prop))
        return properties


class CrdVersion(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )

    version: str = Field(validation_alias="name")
    description: Optional[str] = Field(
        validation_alias=AliasPath("schema", "openAPIV3Schema", "description"),
        default="",
    )
    properties: Optional[Properties] = Field(
        validation_alias=AliasPath("schema", "openAPIV3Schema", "properties"),
        default_factory=list,
    )


class BasicCrd(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )

    group: str
    kind: str = Field(validation_alias=AliasPath("names", "kind"))
    plural: str = Field(validation_alias=AliasPath("names", "plural"))


class Crd(BasicCrd):
    short_names: Optional[list[str]] = Field(
        validation_alias=AliasPath("names", "shortNames"),
        default_factory=list,
    )
    versions: list[CrdVersion]
