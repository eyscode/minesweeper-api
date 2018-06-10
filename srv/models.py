import random
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declarative_base
import uuid
import base64

Base = declarative_base()


def generate_id():
    u = uuid.uuid4()
    b = base64.b32encode(u.bytes)
    return b[0:18].decode('utf-8')


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.Unicode(25), primary_key=True, default=generate_id)
    username = sa.Column(sa.Unicode(50), nullable=False, unique=True)
    password = sa.Column(sa.Unicode(120))
    registered_on = sa.Column(sa.DateTime, default=datetime.utcnow)

    boards = relationship("Board")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User id={} username={}>'.format(self.id, self.username)


class Board(Base):
    __tablename__ = 'boards'

    id = sa.Column(sa.Unicode(25), primary_key=True, default=generate_id)
    created_date = sa.Column(sa.DateTime, nullable=False, default=datetime.utcnow)
    paused_date = sa.Column(sa.DateTime, nullable=True, default=None)
    ended_date = sa.Column(sa.DateTime, nullable=True, default=None)
    status = sa.Column(sa.Unicode(10), nullable=False, default='active')
    rows = sa.Column(sa.Integer(), nullable=False)
    columns = sa.Column(sa.Integer(), nullable=False)
    mines_list = sa.Column(postgresql.JSON)
    last_plays_state = sa.Column(postgresql.JSON)
    result = sa.Column(sa.Unicode, nullable=True, default=None)
    owner_id = sa.Column(sa.Unicode, sa.ForeignKey('users.id'), nullable=False)
    owner = relationship("User", back_populates="boards")

    @property
    def state(self):
        if not self.last_plays_state:
            return [
                ['-' for j in range(self.columns)] for i in range(self.rows)
            ]
        return self.last_plays_state

    @state.setter
    def state(self, state):
        self.last_plays_state = state

    def update_state(self, i, j, value):
        state = self.state
        state[i][j] = value
        self.state = state

    def generate_mines(self, mines):
        self.mines_list = []
        while mines > 0:
            rand_row = random.randint(0, self.rows - 1)
            rand_column = random.randint(0, self.columns - 1)
            if [rand_row, rand_column] not in self.mines_list:
                self.mines_list.append([rand_row, rand_column])
                mines -= 1