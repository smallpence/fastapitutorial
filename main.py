"all api endpoints description"

from enum import Enum
from typing import Optional

from fastapi import FastAPI

app = FastAPI()


class ModelName(str, Enum):
    "an example enum"
    OPTION1 = "1"
    OPTION2 = "2"
    OPTION3 = "3"


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
# arg with =      -> optional with default
# optional = None -> optional with no default
# optional = val  -> optional with default

# required with default -> ig doesnt make sense since just use default

@app.get("/param")
async def param(num: int, num2:int = 1, num3: Optional[int] = None, num4: Optional[int] = 5):
    "testing params with no default"
    return {'num': num, 'num2': num2, 'num3': num3, 'num4': num4}
