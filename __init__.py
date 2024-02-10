# callable
# getattr
import pydantic
from typing import Annotated

class Schema(pydantic.BaseModel):
    name: str

# print(Schema(name="Atharv", lastname = "Pande"))
a = list| str

# print(a)
import bcrypt

password = "password123".encode()
# print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())




