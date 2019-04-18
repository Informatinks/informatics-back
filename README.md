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

### Database migration

1. Ensure DB connection string points to primary migration DB:
    ```
    SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:@localhost/pynformatics
    ```
    Note `/pynformatics` at the end.
2. Refrenced tables should be the same engine type (InnoDB) as parent;
3. FKey types should be the same type as PKeys e.g. (`bigint(10) unsigned`);
4. Any previously manually created tables should be deleted.

To switch to migration-based workdlow:

1. Convert `moodle.mdl_statements` to InnoDB (refrenced by `contest_instance`):
    ```
    ALTER TABLE moodle.mdl_statements ENGINE = InnoDB;
    ```
2. Ensure all FKey refs are described with correspnding types in migrations:
    ```
    from sqlalchemy.dialects.mysql import BIGINT
    ...
    sa.Column('contest_id', BIGINT(display_width=10, unsigned=True), nullable=True), # <-> for
    ```
    or similar.
3. Remove any pre-existing tables:
   ```
   drop database refresh_token;
   ```
   
Then update to current schema:

```
flask db upgrade
```

After modifying models:

```
# generate new migrations
flask db migrate


# ensure corresponing pkeys and migrate
flask db upgrade
```

## Running tests

### Docker

Build and run tests container with provided docker-compose file:

```jk
docker-compose --file docker/docker-compose.yml up --force-recreate --abort-on-container-exit --build
```

If all tests are passed, the Docker process will exit with code 0.jkkkk