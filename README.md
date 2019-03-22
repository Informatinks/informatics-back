# rmatics-back

## Configuring app

### Settings

1. Copy `informatics_front/settings.sample.cfg` to `informatics_front/settings.cfg`.
2. Edit `informatics_front/settings.cfg` with actual environment settings. 

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