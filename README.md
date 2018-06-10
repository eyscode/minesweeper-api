# minesweeper-api

REST api for playing minesweeper, with persistence and authentication.

## Authentication

### POST /register

Registers a new user.

+ Body params:
  + username: string
  + password: string

+ Response 201:
  + username: string
  + registered_on: string

### POST /auth

Gets a json web token.

+ Body params:
  + username: string
  + password: string

+ Response 200:
  + access_token: string

## Game

### POST /boards

Create a new board

+ Body params:
  + rows: integer
  + columns: integer
  + mines: integer

+ Response 201:
  + id: string (unique ID for the game)
  + created_date: string
  + status: string
    - `active` (game active)
    - `paused` (game paused)
    - `archived` (game over)

### GET /boards/{id}

Retrieve an already created board.

+ URL params:
  + id: string

+ Response 200:
  + id: string
  + created_date: string
  + elapsed_time: string (timedelta of elapsed time, available when game is paused or archived)
  + ended_date: string (timestamp, available when game is archived)
  + result: string (available when game is archived)
    - `win`
    - `lose`
  + resume_date: string (timestamp, available when game was resumed at least one time)
  + state: array (matrix of cells values)
    - `-` An unrevealed cell
    - `f` An unrevealed flagged cell
    - `@` An unflagged cell with a mine in it (only show after a game is won or lost)
    - `w` A wrong flagged cell with no mine in it (only show after a game is lost)
    - `x` Last revealed cell with a mine in it (only show after a game is lost)
    - `1`-`8` The number of neighboring cells that contain a mine.
  + status: string
    - `active` (game active)
    - `paused` (game paused)
    - `archived` (game over)
    
### GET /boards/{id}/pause

Pause an already created board.

+ URL params:
  + id: string

+ Response 200:
  + message: string (success message)
    
### GET /boards/{id}/resume

Resume an already created board.

+ URL params:
  + id: string

+ Response 200:
  + message: string (success message)
    

### POST /boards/{id}/reveal

Reveals a cell in board.

+ URL params:
  + id: string (unique ID for the game)

+ Body params:
  + row: integer (zero based index).
  + col: integer (zero based index).

+ Response 200:
  + id: string
  + created_date: string
  + elapsed_time: string (timedelta of elapsed time, available when game is paused or archived)
  + ended_date: string (timestamp, available when game is archived)
  + result: string (available when game is archived)
  + resume_date: string (timestamp, available when game was resumed at least one time)
  + state: array (matrix of cells values)
  + status: string

### POST /boards/{id}/flag

Flags/Unflags a cell in board.

+ URL params:
  + id: string (unique ID for the game)

+ Body params:
  + row: integer (zero based index).
  + col: integer (zero based index).

+ Response 200:
  + id: string
  + created_date: string
  + elapsed_time: string (timedelta of elapsed time, available when game is paused or archived)
  + ended_date: string (timestamp, available when game is archived)
  + result: string (available when game is archived)
  + resume_date: string (timestamp, available when game was resumed at least one time)
  + state: array (matrix of cells values)
  + status: string