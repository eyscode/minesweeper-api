from sqlalchemy.ext.declarative import declarative_base
import uuid
import base64

Base = declarative_base()


def generate_id():
    u = uuid.uuid4()
    b = base64.b32encode(u.bytes)
    return b[0:18].decode('utf-8')


