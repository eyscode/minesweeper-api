# Minesweeper API

REST api for playing minesweeper, with persistence and authentication. The [online api](https://minesweeper-eys.herokuapp.com) is deployed on a free tier of Heroku, so be aware that sometimes it won't be available.

This api could be consumed by any kind of clients, e.g here is an [online demo](https://eyscode.github.io/minesweeper-client/) available using this api, its source code can be found [here](https://github.com/eyscode/minesweeper-client).

## API documentation

A full [API documentation](https://minesweeper-eys.herokuapp.com/documentation.json) is available, just copy & paste in [Swagger Editor](https://editor.swagger.io) in order to visualize it. There is also an [alternative API documentation](DOCS.md) available in this repo. 

## Decisions taken

- Python and Flask were used to build the REST api because of their simplicity.
- PostgreSQL was used for the persistence layer because of its great relational features and also fields like JSON, which was used for storing mines array and matrix state of the board.
- For authentication I opted-in for JSON web tokens since this could be used on web or mobile.
- All resources that change something on db use POST http method. GET is discouraged for this, and it's only used for retrieve data.
- Minesweeper reveal algorithm uses recursion in order to find neighbors cells to reveal.

## Important notes

- Validation was key for reveal and flag resources.
- PostgreSQL does not detect JSON field changes, `flag_modified` was needed for this.
