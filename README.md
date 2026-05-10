# Описание

Домашнее задание по ИПР.  
Студент: Кичигин Артём  
Группа: 241(ИУП)

## Запуск тестов

В корне проекта выполнить:

```bash
coverage erase
coverage run -m pytest tests
```

## Просмотр coverage

После запуска тестов выполнить:

```bash
coverage html
open htmlcov/index.html
```