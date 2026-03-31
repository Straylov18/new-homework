# Получения и отправка файлов 

Очень часто возникает необходимость загружать и выгружать файлы 
при помощи backend приложения.
Для этого в fastapi есть встроенные механизмы, которые мы рассмотрим в этом уроке.

## Получение файлов

Напишем простое backend приложение на fastapi 
и добавим в него ручки получения файлов от пользователя.

Чтобы получать на вход ручки файлы, 
необходимо всего лишь добавить в обрабатываемый роутером метод параметр типа **UploadFile**.
В этот параметр нам и придет файл.
Для начала сохраним его в специальную папку на диске (папка **files** в корне проекта):
```python
from fastapi import UploadFile

@router.post('/upload_file')
async def upload_file(upload_file: UploadFile):
    file = upload_file.file
    filename = upload_file.filename
    with open(f"files/{filename}", "wb") as f:
        f.write(file.read())
    return "File uploaded"
```
Здесь:
- объявляется асинхронный метод, который принимает на вход файл (```async def upload_file(upload_file: UploadFile):```)
- из объекта входящего файла получаются имя файла и сам файл
```python
file = upload_file.file
filename = upload_file.filename
```
- файл побитово (параметр "wb" - write byte) записывается на диск (в папку **f"files/{filename}"**)
```python
with open(f"files/{filename}", "wb") as f:
    f.write(file.read())
```

Теперь на страничке openapi документации приложения 
можно отправить файл на это ручку (перетащив или выбрав из папки) и убедиться, 
что файл запишется в указанное место (или перезапишет файл с таким же названием).

### Получение множества файлов

Чтобы получать сразу несколько фалов от пользователя, 
необходимо всего лишь указать что входной параметр будет принимать лист объектов UploadFile.
Напишем ручку, в которой мы будем пробегаться по всем полученным файлам 
и сохранять их в папку **files**:
```python
@router.post('/upload_multiple_file')
async def upload_multiple_file(upload_files_list: list[UploadFile]):
    for upload_file in upload_files_list:
        file = upload_file.file
        filename = upload_file.filename
        with open(f"files/{filename}", "wb") as f:
            f.write(file.read())
        return "File uploaded"
```

Теперь на страничке openapi документации можно будет за один раз передать сразу несколько файлов.

## Отправка файлов

Примерно так же просто можно и получать файлы средствами fastapi.

Создадим ручку, выдающую файлы из папки **files**:
```python
from fastapi.responses import FileResponse

@router.get('/file/{filename}')
async def get_file(filename: str) -> FileResponse:
    return FileResponse(f"files/{filename}")
```
Здесь:
- объявляется асинхронный метод, который будет выдавать файл (```async def get_file(filename: str) -> FileResponse:```)
- выдается файл, лежащий на диске по указанному пути (```return FileResponse(f"files/{filename}")```)

Если дернуть за ручку получения файла, 
напрямую из адресной строки браузера, 
она будет воспринята как запрос на получения статического контента.

Те. если в адресной строке браузера получать от бэка видео, 
оно будет воспроизводиться как видео, музыка - как музыка итд.

Например, в этом уроке закреплен пример html странички, 
которую можно выдавать как мини фронтенд для используемого приложения.
Чтобы открыть ее, нужно просто запросить необходимый файл у бэкенда через адресную строку браузера: 
http://127.0.0.1:8000/api/v1/file/index.html.

Вообще у крупных приложений лучше выдачу статического контента для фронтенда 
делать не через ручки бэкенда, чтобы не нагружать его 
(лучше делать это через внешний веб сервер, например через nginx).
Но для ситуации, когда необходимо быстро написать простое веб приложение вместе с фронтом, 
такой способ выдачи страниц фронта может оказаться весьма удобным.

## Потоковая передача больших файлов

Большие файлы лучше передавать кусками по частям (потоковая передача или стриминг), 
чтобы соединение не отваливалось в процессе передачи, 
и файл успешно передался с большей вероятностью.
Плюс, при потоковой передаче файлов 
они не обязаны перед отправкой полностью сохраняться в оперативной памяти, 
что сильно оптимизирует весь процесс передачи.

### Создадим большой файл

Для начала создадим большой файл 
(это может быть как видео, так и картинка, так и текстовый файл).

Чтобы получить большой текстовый файл 
можно воспользоваться следующей bash командой 
для генерации текстовых файлов:
```shell
# создаст файл из 10000 строк с одинаковым текстом
OUTPUT_LINES=100000; for i in $(seq 1 $OUTPUT_LINES); do echo "tarabara rastabara naprimer"; done > files/tarabara_rastabara_naprimer.txt
```

Если мы будем получать его старым методом
(http://127.0.0.1:8000/api/v1/file/tarabara_rastabara_naprimer.txt), 
то он сначала загрузиться в оперативную память, потом будет выдаваться.
Те такой способ будет более долгим, менее надежным и затратным в плане оперативной памяти.

### Потоковая передача данных с использованием генераторов

Для начала создадим функцию, 
читающую файл и генерирующую поток данных из этого файла:
```python
def iterate_file(filename: str):
    with open(get_file_path(filename), "rb") as f:
        while file_chunk := f.read(1024 * 1024):
            yield file_chunk
```
Здесь:
- происходит побитовое чтение файла при помощи параметра "rb" 
(```with open(get_file_path(filename), "rb") as f:```)
- чтение куска файла, размером 1024 * 1024 B = 1Mb
(```f.read(1024 * 1024)```)
- при помощи моржового оператора ":=" мы присваиваем значение переменной file_chunk 
и выдаем присвоенное значение в условие while 
(```while file_chunk := f.read(1024 * 1024)```)
- выдаем кусок данных при следующем запросе генератора 
(```yield file_chunk```)

В fastapi есть объект, принимающий на вход такого рода генераторы и выдающий файли постепенно
```python
from fastapi.responses import StreamingResponse

@router.get('/file-streaming/{filename}')
async def get_file_streaming(filename: str) -> StreamingResponse:
    return StreamingResponse(
        iterate_file(filename),
    )
```

Зададим также StreamingResponse объекту формат отправляемого файла.
Формат файла будем получать из имени запрашиваемого файла:

```python
def get_filename_media_type(filename: str) -> str:
    file_extension = filename.split('.')[-1]
    if file_extension == '.txt':
        return 'text/txt'
    elif file_extension == '.html':
        return 'text/html'
    elif file_extension == '.png':
        return 'image/mp4'
    elif file_extension == '.jpeg':
        return 'image/jpg'
    elif file_extension == '.gif':
        return 'image/gif'
    elif file_extension == '.mp4':
        return 'video/mp4'
    elif file_extension == '.mpeg':
        return 'video/mpeg'


@router.get('/file-streaming/{filename}')
async def get_file_streaming(filename: str) -> StreamingResponse:
    return StreamingResponse(
        iterate_file(filename),
        media_type=get_filename_media_type(filename)
    )
```

Достаточно часто подобный способ потокового скачивания реализуют для отправки видео, аудио 
(чтобы проигрыватель мог запустить их сразу, не дожидаясь полного скачивания).

### Передача файлов через multipart

Однако просто так нельзя передать и сам файл и набор текстовых полей.

multipart/form-data — специальный формат кодирования данных, 
который используется для отправки файлов и других форм данных через HTTP-запросы. 
Особенно актуален при работе с формами, 
где требуется передать одновременно текстовые данные и файлы.

При передаче через multipart данные разделяются на части (parts), 
каждая из которых может содержать данные разных типов и форматов.
Каждый такой блок имеет собственную метаинформацию, 
включая заголовки Content-Type и Content-Disposition, 
что позволяет серверу корректно интерпретировать содержимое.

Например, мы можем загрузить файл и сразу передать еще пару значений в том же запросе
(в данном примере передаются также названия, под которыми стоит записать файл на диск):
```python
from typing import Annotated
from fastapi import File, Form, UploadFile

@router.post('/upload_file_multipart')
async def upload_file(
        new_filename: Annotated[str, Form(description="Как записать файл на диск")],
        backup_filename: Annotated[str, Form(description="Дублирующийся файл на диске")],
        upload_file: Annotated[UploadFile, File(description="Сам файл")]
):
    file = upload_file.file
    with open(get_file_path(new_filename), "wb") as f:
        f.write(file.read())
    with open(get_file_path(backup_filename), "wb") as f:
        f.write(file.read())
    return "File uploaded"
```
