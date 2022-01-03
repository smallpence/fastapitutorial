"all api endpoints description"

from enum import Enum
from typing import Optional, List

from fastapi import FastAPI, Query
from pydantic import BaseModel #pylint: disable=no-name-in-module

app = FastAPI()


class ModelName(str, Enum):
    "an example enum"
    OPTION1 = "1"
    OPTION2 = "2"
    OPTION3 = "3"


class Item(BaseModel): #pylint: disable=too-few-public-methods
    "testing pydantic model"
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = 0.0


@app.get("/")
async def root():
    "simple root api"
    return {'hello': "world"}

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    "demonstrating int checking"
    return {"item_id": item_id}


@app.get("/enum/{model}")
async def get_enum(model: ModelName):
    "testing enums"
    return model.name

# arg with no =   -> required with no default
# arg with =      -> optional with default, but limited on position in arg list
# optional = None -> optional with no default
# optional = val  -> optional with default

# required with default -> ig doesnt make sense since just use default

@app.get("/param")
async def param(num: int, num2:int = 1, num3: Optional[int] = None, num4: Optional[int] = 5):
    "testing params with no default"
    return {'num': num, 'num2': num2, 'num3': num3, 'num4': num4}

@app.get("/body")
async def body(item: Item):
    "testing a pydantic model"
    item.description = "wowie"
    return item

@app.get("/optional")
async def optional(string: Optional[str] = Query(..., max_length=10),
                   somelist: List[str] = Query([])):
    """
    testing max length string with no default value
    and list params
    """
    print(somelist)
    return string
