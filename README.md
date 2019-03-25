# rmatics-back

## Configuring app

### Settings

1. `FLASK_ENV` variable should point to `development`, `testing` or `production`;
2. `FLASK_APP` (target) should point to app constructor with specified config class (e.g `FLASK_APP=informatics_front:create_app('informatics_front.config.DevConfig')`);
2. App-specific settings should be provided as env vars. A complete list of supported ones can be found in `informatics_front/config.py`.

#### Flask 

### Database population 

Create databases as described in `docker/create-databases.sql`. This DB schema is valid for all environments.

## Running tests

### Docker

Build a tests container with provided docker-compose file:

```
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.test.yml build pytest
```

Run test container:

```
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.test.yml up pytest
```

Or this can be done simultaneously.

If all tests are passed, the Docker process will exit with code 0.