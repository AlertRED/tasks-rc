from math import isnan
from typing import Dict, List
from pydantic import BaseModel, validator


class Price(BaseModel):
    year: int
    price: float

    @validator('price')
    def disallow_nan(cls, v: float) -> float:
        if isnan(v):
            raise ValueError("NaN values are not allowed")
        return v


class Project(BaseModel):
    name: str
    sub_projects: List['Project'] = []
    prices: Dict[str, List[Price]] = {}


class ProjectFromDB(Project):
    sub_projects: List['ProjectFromDB'] = []
    total_price: int = 0


class Data(BaseModel):
    version: int | None = None
    projects: List[Project] = []


class DataFromDB(Data):
    projects: List[ProjectFromDB] = []
