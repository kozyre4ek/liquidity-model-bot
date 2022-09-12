# liquidity-model-bot

## Запуск

1. Создать файл с кредами
```bash
$ echo 'TELEGRAM_TOKEN=<your-telegram-token>' > .env_docker
```
2. Собрать образ
```bash
$ docker build -t <docker-image-name>:<docker-image-tag> .
```
3. Запустить образ
```bash
$ docker run --rm -d \
    --env-file .env_docker \
    <docker-image-name>:<docker-image-tag>
```