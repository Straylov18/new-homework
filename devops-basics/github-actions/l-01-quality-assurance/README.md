# Проверка качества кода backend приложения с помощью github actions

Допустим у нас уже есть репозиторий с fastapi приложением.

Создадим автоматическую проверку стилизации кода для этого приложения.
Для начала эта проверка будет состоять из запуска линтера 
при каждом новом коммите в любую ветку репозитория проекта.

Создадим для этого github workflow **.github/workflows/ci-push.yml** 
и укажем в нем условия его запуска:
```yaml
name: Flake8
on: [push]
```

Зададим операционную систему на которой будет запускать этот github action:
```yaml
name: Flake8
on: [push]
jobs:
  Flake8:
    runs-on: ubuntu-latest
```

Сейчас из описания данного файла будет создаваться пустая виртуальную машину с Ubuntu.
Чтобы производить в ней операции именно с текущим репозиторием, 
необходимо его туда выкачивать, когда виртуалка будет запускаться:
```yaml
name: Flake8
on: [push]
jobs:
  Flake8:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v5
```
Добавленный шаг использует сторонний github action при помощи свойства uses 
(actions/checkout@v5 - специальный github action для выкачивания репозиториев).
Данный github action глобальный и будет скачиваться из сети, 
однако подобным образом можно переиспользовать и workflow из текущего проекта 
(об этом в следующих уроках).

Если тебе необходимо делать какие-то часто встречающиеся в мире задачи, 
можно сначала погуглить существующие github action под эти задачи.

Подобным способом установим на виртуалку python и poetry нужных версий.
Потом отдельными шагами установим необходимые зависимости и запустим линтер.
Тогда workflow будет выглядеть следующим образом:
```yaml
name: Flake8
on: [push]
jobs:
  Flake8:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install and configure Poetry
        uses: snok/install-poetry@v1
        with:
          version: 2.1.3
          virtualenvs-create: true
          installer-parallel: true
      - name: Install requirements
        run: |
          poetry install --no-root
      - name: Run linter
        run: |
          poetry run flake8
```

Однако если ты вдруг потом добавишь еще дополнительные пакеты для проверок кода, 
их нужно каждый раз добавлять отдельным шагом в этот workflow.
Порой у тебя будет много workflow для разных условий 
(для принятия PR, для пуша в main, в test ветки, для деплоя на сервера итд.).

Чтобы не забывать добалвять новые проверки во все workflow, 
лучше обернуть их во что-то, что будет вызываться отовсюду (bash скрипт, make команда итд.). 

Рассмотрим запуск проверок через make команды.
Подробнее о создании простых Makefile конфигураций можно посмотреть в отдельном курсе.

Подробнее о приемах описания Makefile-ов в рамках создания инструментов для команды разработчиков можно прочитать тут:
[урок по созданию инструментов для команды разработчиков на основе Makefile](https://github.com/TheYeniseiTrireme/homework-materials/tree/main/devops-basics/creating-tools-for-developers/l-02-make).

В корне проекта создадим Makefile, 
в котором опишем команды запуска разных проверок, 
установки зависимостей, итд.
Все эти команды привяжем к команде QA:
```makefile
all: QA

.PHONY: requirements
requirements:
	poetry install --no-root

.PHONY: flake8
flake8: requirements
	poetry run flake8

.PHONY: isort
isort: requirements
	poetry run isort . --skip-gitignore --check-only

.PHONY: QA
QA: flake8 isort
```
Тогда при запуске команды QA у нас будут вызываться команды 
- isort (сортировка библиотек python приложения)
- flake8 и ее модули (проверка стилизации кода)
- requirements (установка зависимостей, которая вызывается при вызове вышеупомянутых команд)

Тогда пусть наш workflow просто вызывает "make QA":
```yaml
name: QA
on: [push]
jobs:
  QA:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository code
        uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install and configure Poetry
        uses: snok/install-poetry@v1
        with:
          version: 2.1.3
          virtualenvs-create: true
          installer-parallel: true
      - name: Run QA
        run: |
          make QA
```
Теперь при появлении новых проверок их можно просто добавить в Makefile, 
и они будут учитываться в описанном workflow.

Также порой делают так, чтобы разные части проверок кода выполнялись в разных github action, 
чтобы происходило распараллеливание на виртуалках, и чтобы они проходили быстрее.
