import copy
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


def reveal_cell(mines_list, rows, cols, state, row, col):
    i_top = row - 1 if row > 0 else row
    j_left = col - 1 if col > 0 else col
    i_bottom = row + 1 if row < rows - 1 else row
    j_right = col + 1 if col < cols - 1 else col

    neighbor_mines = 0
    neighbors_list = []

    for i in range(i_top, i_bottom + 1):
        for j in range(j_left, j_right + 1):
            if i == row and j == col:
                continue
            if isinstance(state[i][j], int):
                continue
            neighbors_list.append((i, j))

    for i, j in neighbors_list:
        if [i, j] in mines_list:
            neighbor_mines += 1

    state[row][col] = neighbor_mines

    if neighbor_mines == 0:
        for i, j in neighbors_list:
            state = reveal_cell(mines_list, rows, cols, state, i, j)

    return state


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
    resume_date = sa.Column(sa.DateTime, nullable=True, default=None)
    elapsed_time = sa.Column(sa.Interval, nullable=True, default=None)
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

    def check_active_status(self, archived_message='This board is archived. Game is over',
                            paused_message='This board is paused. Resume it in order to continue playing'):
        if self.status == 'archived':
            return False, archived_message
        elif self.status == 'paused':
            return False, paused_message
        return True, None

    def pause(self):
        active, message = self.check_active_status(paused_message='This board is already paused')
        if active:
            self.calculate_elapsed_time()
            self.status = 'paused'
            return True, None
        return False, message

    def resume(self):
        if self.status == 'paused':
            self.status = 'active'
            self.resume_date = datetime.utcnow()
            return True, None
        elif self.status == 'active':
            return False, "Can't resume an {} board".format(self.status)

    def flag(self, i, j):
        active, message = self.check_active_status()
        if active:
            if self.state[i][j] == '-':
                self.update_state(i, j, 'f')
                return True, message
            elif self.state[i][j] == 'f':
                self.update_state(i, j, '-')
                return True, message
            else:
                return False, "Cell in row {} and col {} can't be flagged because is already revealed".format(i, j)
        return False, message

    def calculate_elapsed_time(self):
        if not self.elapsed_time:
            self.elapsed_time = datetime.utcnow() - self.created_date
        else:
            last_elapsed_time = datetime.utcnow() - self.resume_date
            self.elapsed_time = self.elapsed_time + last_elapsed_time

    def reveal(self, i, j):
        active, message = self.check_active_status()
        if active:
            if self.state[i][j] == '-':
                if [i, j] in self.mines_list:
                    self.status = 'archived'
                    self.result = 'lost'
                    self.ended_date = datetime.utcnow()
                    self.calculate_elapsed_time()
                    self.update_state(i, j, 'x')
                    self.check_mines_and_wrong_flags()
                else:
                    self.state = reveal_cell(self.mines_list, self.rows, self.columns, self.state, i, j)
                    end, new_state = self.check_end_game()
                    if end:
                        self.status = 'archived'
                        self.result = 'win'
                        self.ended_date = datetime.utcnow()
                        self.calculate_elapsed_time()
                        self.state = new_state
                return True, message
            elif self.state[i][j] == 'f':
                return False, "Cell in row {} and col {} can't be revealed because is flagged".format(i, j)
            else:
                return False, "Cell in row {} and col {} is already revealed"
        return False, message

    def check_end_game(self):
        state = copy.deepcopy(self.state)
        for row in range(self.rows):
            for col in range(self.columns):
                if self.state[row][col] in ('-', 'f') and [row, col] not in self.mines_list:
                    return False, None
                elif self.state[row][col] not in ('x', 'f') and [row, col] in self.mines_list:
                    state[row][col] = '@'
        return True, state

    def check_mines_and_wrong_flags(self):
        for row in range(self.rows):
            for col in range(self.columns):
                if self.state[row][col] == '-' and [row, col] in self.mines_list:
                    self.update_state(row, col, '@')
                elif self.state[row][col] == 'f' and [row, col] not in self.mines_list:
                    self.update_state(row, col, 'w')

    def __repr__(self):
        return '<Board id={} size={}x{} status={}>'.format(self.id, self.rows, self.columns, self.status)
