from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, AliasPath
from pydantic.alias_generators import to_camel


class Property(BaseModel):
    name: str
    description: str
    type: str
    properties: list["Property"]
    required: list[str]


class CrdVersion(BaseModel):
    version: str = Field(validation_alias="name")
    description: str = Field(validation_alias=AliasPath("schema", "openAPIV3Schema", "description"))
#    properties: list[Property] = Field(validation_alias=AliasPath("schema", "openAPIV3Schema", "properties"))


class Crd(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
    )

    group: str
    kind: str = Field(validation_alias=AliasPath("names", "kind"))
    plural: str = Field(validation_alias=AliasPath("names", "plural"))
    short_names: Optional[list[str]] = Field(validation_alias=AliasPath("names", "shortNames"))
    #versions: list[CrdVersion]

    def name(self):
        return f"{self.plural}.{self.group}"