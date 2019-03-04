# rmatics-back

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