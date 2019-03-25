# rmatics-back

## Configuring app

### Settings

1. `FLASK_ENV` variable should be set (`development`, `testing`, `production`).
2. Settings should be provided as env vars. A complete list of supported ones can be found in `informatics_front/config.py`. 

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