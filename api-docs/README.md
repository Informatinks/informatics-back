# Api-docs
Документация public api для Education service.

## Документирование
Все ссылки разделены по тегам. Документация дописывается в файлах, лежащих в
`./components/paths`.
При добавлении нового тега, добавляется новый файл.

Часто используемые компоненты описываются в файлах в папке `./components` и
используются с помощью `$ref`.
Компоненты можно дополнять, изменять при помощи `allOf:` (см. [документацию](
https://swagger.io/docs/specification/data-models/inheritance-and-polymorphism/
))

## Сборка
При сборке докер образа все компоненты из `./components` и `./components/paths`
мержатся в файл `api.yaml`. Если необходимо изменить основную информацию по
документации, можно сделать это в заготовке файла `api.yaml`

### Сборка файла

``` bash
npm run build
```

### Docker
Пример сборки docker image

``` bash
docker build --tag api-docs --no-cache .
```
и запуска контейнера

``` bash
docker run --publish 5006:8080 api-docs
```

Swagger UI будет доступен по ссылке `http://localhost:5006`

### Режим разработки

1. Запустить вотчер

``` bash
npm run watch
```

2. Запустить контейнер со сваггером

``` bash
docker run --rm --env SWAGGER_JSON=/etc/api.yaml --volume `pwd`/result.yaml:/etc/api.yaml --publish 5006:8080 swaggerapi/swagger-ui:latest
```

### Swagger UI
Внутри интерфейса основной файл доступен по ссылке `./api.yaml`,
а файлы из папки `./components/paths` доступны по ссылкам `./paths/<file_name>`