from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AliasPath, RootModel, model_validator
from pydantic.alias_generators import to_camel


def validate_required_properties(model):
    if model.required_properties:
        for prop in model.properties:
            prop._required = prop.name in model.required_properties
    return model


class Property(BaseModel):
    name: str
    description: Optional[str] = ""
    type: Optional[str] = ""
    properties: Optional["Properties"] = Field(default_factory=list)
    required_properties: Optional[list[str]] = Field(
        alias="required",
        default_factory=list,
    )

    _required: bool = False

    @property
    def required(self):
        return self._required

    _validate_required_properties = model_validator(mode="after")(validate_required_properties)


class Properties(RootModel):
    root: list[Property] = Field(default_factory=list)

    def __iter__(self):
        return iter(self.root)

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
    required_properties: Optional[list[str]] = Field(
        validation_alias=AliasPath("schema", "openAPIV3Schema", "required"),
        default_factory=list,
    )

    _validate_required_properties = model_validator(mode="after")(validate_required_properties)


class BasicCrd(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )

    group: str
    kind: str = Field(validation_alias=AliasPath("names", "kind"))
    plural: str = Field(validation_alias=AliasPath("names", "plural"))

    def name(self):
        return f"{self.plural}.{self.group}"


class Crd(BasicCrd):
    short_names: Optional[list[str]] = Field(
        validation_alias=AliasPath("names", "shortNames"),
        default_factory=list,
    )
    versions: list[CrdVersion]
