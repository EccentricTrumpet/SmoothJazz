## 升级 - Sheng Ji

This is a hobbyist implementation of the Chinese card game Sheng Ji. [See Wikipedia article](https://en.wikipedia.org/wiki/Sheng_ji) for details and game rules.

## Architecture

The new architecture will include the following components:

- **webapp**: The frontend will be a web application that will serve as the main UI for the game. The frontend will be built using React.js.
- **server**: The backend will be a Python server that will process the game logic and serve the webapp. The server will be built using Flask and Socket.IO.

## To run the app

### For development

Run the server with the command:

```cmd
> cd ./server
> pipenv shell
> (server) python start.py
```

In another terminal, run the webapp with the commands:

```cmd
> cd ./webapp
> npm start
```

### For deployment

Build the React webapp:

```cmd
> cd ./webapp
> npm run build
```

Build the Docker image

```cmd
> cd ./server
> docker build .
```

Run the docker image

```cmd
> docker run -it <image>
```

## Glossary

Here are some helpful contractions and conventions used in the code.

1. PID - shorthand for player id. These are unique IDs associated with a player
2. Type_ - shorthand for `Type | None` in python
3. events - websocket messages sent from webapp to web server
4. updates - websocket messages sent from web server to webapp