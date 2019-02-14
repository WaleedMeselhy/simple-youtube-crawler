# YouTube crawler.

**SQLAlchemy** as Object Relational Mapper
**Alembic** for databse migration
**Selenium** for scrapping youtube
**Parsel** for extract data from XML/HTML
**Celery**  for task management
**Flask-RESTPlus** for building REST APIs
**Schematics** for validating models
### Example

YouTube crawler requires [Docker Compose](https://docs.docker.com/compose/) to run.

### Run example.

```sh
$ cd youtube_crawler
$ example/run.sh
```

navigate to [http://localhost:5000/](http://localhost:5000/) to see the swagger and try endpoints.

### Terminate example.
```sh
$ example/stop.sh
$ sudo rm -rf db_data
$ sudo rm -rf downloads
```
