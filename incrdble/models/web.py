from typing import Optional, Any

from pydantic import BaseModel, Field, ConfigDict, ValidatorFunctionWrapHandler
from pydantic.functional_validators import field_validator, model_validator

from incrdble.models import k8s


class Type(BaseModel):
    name: str
    properties: list["Property"] = Field(default_factory=list)


class Property(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    name: str
    description: Optional[str] = None
    type: str | Type = None

    @model_validator(mode='wrap')
    @classmethod
    def validate_property(cls, value: Any, handler: ValidatorFunctionWrapHandler):
        new = handler(value)
        if isinstance(new.type, str):
            if new.type == "object":
                if isinstance(value.properties, list):
                    new.type = Type.model_validate({"name": value.name, "properties": value.properties})
                elif isinstance(value.properties, k8s.Properties):
                    new.type = Type.model_validate({"name": value.name, "properties": value.properties.root})
                else:
                    new.type = Type(name=new.type)
            else:
                new.type = Type(name=new.type)
        return new


class CrdVersion(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    version: str
    description: Optional[str] = None
    properties: list[Property] = Field(default_factory=list)

    @field_validator("properties", mode="before")
    @classmethod
    def validate_properties(cls, value):
        if not value:
            return []
        properties = []
        for prop in value.root:
            properties.append(Property.model_validate(prop))
        return properties



class Crd(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    group: str
    kind: str
    plural: str
    short_names: Optional[list[str]] = Field(default_factory=list)
    versions: list[CrdVersion] = Field(default_factory=list)

    def name(self):
        return f"{self.plural}.{self.group}"
