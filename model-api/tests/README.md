# Тестирование Model API

Этот документ описывает процесс запуска и интерпретации тестов для Model API.

## Подготовка к тестированию

1. Убедитесь, что вы находитесь в виртуальном окружении:
```bash
# Проверьте наличие префикса (venv) в начале строки командной строки
# Если нет, активируйте виртуальное окружение:
.\venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

2. Установите все зависимости:
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Запуск всех тестов
```bash
pytest tests/test_endpoints.py -v
```

### Запуск конкретного теста
```bash
pytest tests/test_endpoints.py::test_transcribe_endpoint -v
```

### Запуск тестов с подробным выводом
```bash
pytest tests/test_endpoints.py -v -s
```

## Интерпретация результатов тестов

### Статусы тестов

- `PASSED` (зеленый) - тест успешно пройден
- `FAILED` (красный) - тест не пройден
- `ERROR` (красный) - произошла ошибка при выполнении теста
- `SKIPPED` (желтый) - тест пропущен
- `XFAIL` (желтый) - тест не прошел, но это ожидаемое поведение

### Пример вывода тестов

```
============================= test session starts ==============================
platform win32 -- Python 3.8.10, pytest-7.1.1, pluggy-0.13.1
rootdir: C:\Users\artem\Projects\System-for-automatic-transcription-and-recording-of-meetings\model-api
plugins: hypothesis-6.54.4, asyncio-0.18.0
collected 7 items

tests/test_endpoints.py::test_transcribe_endpoint PASSED               [ 14%]
tests/test_endpoints.py::test_summary_endpoint PASSED                 [ 28%]
tests/test_endpoints.py::test_speakers_endpoint PASSED               [ 42%]
tests/test_endpoints.py::test_speaker_transcript_endpoint PASSED     [ 57%]
tests/test_endpoints.py::test_protocol_endpoint PASSED               [ 71%]
tests/test_endpoints.py::test_chat_answer_endpoint PASSED            [ 85%]
tests/test_endpoints.py::test_get_meeting_info_endpoint PASSED       [100%]

============================== 7 passed in 2.34s ==============================
```

## Описание тестов

### 1. test_transcribe_endpoint
- Проверяет эндпоинт транскрибации аудио
- Создает временный аудиофайл
- Отправляет его на сервер
- Проверяет успешность ответа и наличие поля "transcription"

### 2. test_summary_endpoint
- Проверяет эндпоинт генерации сводки
- Создает временный текстовый файл
- Отправляет его на сервер
- Проверяет успешность ответа и наличие поля "summary"

### 3. test_speakers_endpoint
- Проверяет эндпоинт определения спикеров
- Создает временный аудиофайл
- Отправляет его на сервер
- Проверяет успешность ответа и наличие поля "segments"

### 4. test_speaker_transcript_endpoint
- Проверяет эндпоинт транскрипции с определением спикеров
- Создает временный аудиофайл
- Отправляет его на сервер
- Проверяет успешность ответа и наличие поля "segments"

### 5. test_protocol_endpoint
- Проверяет эндпоинт генерации протокола
- Отправляет тестовые данные транскрипции
- Проверяет успешность ответа и формат возвращаемых данных

### 6. test_chat_answer_endpoint
- Проверяет эндпоинт ответов чат-бота
- Использует моковые данные встречи
- Отправляет тестовый вопрос
- Проверяет успешность ответа и наличие поля "answer"

### 7. test_get_meeting_info_endpoint
- Проверяет эндпоинт получения информации о встрече
- Использует моковые данные встречи
- Проверяет успешность ответа и корректность возвращаемых данных

### 8. test_error_handling
- Проверяет обработку некорректных запросов
- Тестирует различные сценарии ошибок
- Проверяет корректность кодов ответа

## Отладка тестов

### Просмотр подробного вывода
```bash
pytest tests/test_endpoints.py -v -s
```

### Остановка на первой ошибке
```bash
pytest tests/test_endpoints.py -x
```

### Запуск с отладчиком
```bash
pytest tests/test_endpoints.py --pdb
```

## Добавление новых тестов

1. Создайте новую функцию в файле `test_endpoints.py`
2. Используйте декоратор `@pytest.mark` для маркировки теста
3. Следуйте существующему паттерну тестирования
4. Добавьте документацию к тесту

Пример:
```python
@pytest.mark.new_feature
def test_new_feature():
    """
    Test description
    """
    # Test implementation
    assert True
```

## Советы по тестированию

1. Всегда очищайте временные файлы после тестов
2. Используйте фикстуры для общих данных
3. Тестируйте как успешные сценарии, так и обработку ошибок
4. Документируйте тесты
5. Следите за изоляцией тестов 