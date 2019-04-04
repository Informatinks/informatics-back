# rmatics-back

## Configuring app

### Settings

Global environment should be passed in different ways depending on boot method:

1. **WSGI** via wsgi.py reads `FLASK_ENV` variable and selects appropriate config class.
2. **flask run** via console or PyCharm configuration reads `FLASK_APP` var, which should point to app with running config module e.g `informatics_front:create_app('informatics_front.config.DevConfig')`  
3. **pytest** automaticaly runs base `informatics_front.config.TestConfig`.

App-specific settings should be provided as env vars along with `FLASK_ENV` and `FLASK_APP`. A complete list of supported ones can be found in `informatics_front/config.py`. 

### Database population 

Create databases as described in `docker/create-databases.sql`. This DB schema is valid for all environments.

## Running tests

### Docker

Build and ru tests container with provided docker-compose file:

```
docker-compose --file docker/docker-compose.yml up --force-recreate --abort-on-container-exit --build
```

If all tests are passed, the Docker process will exit with code 0.