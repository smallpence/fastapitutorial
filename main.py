"all api endpoints description"
from datetime import timedelta, datetime
from enum import Enum
from typing import Optional, List

import jwt
from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict
from jose import JWTError
from passlib.context import CryptContext
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


class User(BaseModel): #pylint: disable=too-few-public-methods
    "a user in the field"
    username: str
    disabled: bool = False


class DBUser(User): #pylint: disable=too-few-public-methods
    "when storing in db, stored a hashed password as well"
    password: str


class TokenData(BaseModel): #pylint: disable=too-few-public-methods
    "container for data stored in a token"
    username: Optional[str] = None


users_db = {
    "johndoe": {
        "username": "johndoe",
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "password": "fakehashedsecret2",
        "disabled": True,
    },
}
SECRET_KEY = "b8d31b67e7430cdcd94f3c18beb11c2cfefbfd5a5e844b0e2e0a32bae41a7bec"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def are_equal(plain_password, hashed_password):
    "checks if a plain password and a hashed one are equal"
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    "hash a password in accordance to the current scheme"
    return pwd_context.hash(password)


def get_user(database, username: str):
    "check if a username is in the database"
    if username in database:
        user = database[username]
        return DBUser(**user)
    return None


def authenticate_user(database, username: str, password: str):
    """
    verifies that a given username & plaintext password are correct
    this means a plaintext password is sent to server,
    but https should make this fine
    """
    user = get_user(database, username)
    if not user:
        return None
    if not are_equal(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    "create a new access token for given data to expire at a certain time"
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    when getting a token from oauth, decode it using the secret key to recover payload
    secret key is only stored on the server in this way
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload["sub"]
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception from JWTError
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    "ensure user is not deactivated"
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="This user is deactivated")
    return current_user

@app.get("/myuser")
async def read_me(user: User = Depends(get_current_active_user)):
    "protected endpoint"
    return user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestFormStrict = Depends()):
    "endpoint for receiving a new access token, which oauth will store"
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({'sub': user.username}, expires_delta=access_token_expires)
    return {
        'access_token': access_token,
        'token_type': "bearer"
    }
