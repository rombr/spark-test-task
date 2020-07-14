Разрабатывал в 3.6.9. Покрытие тестами 94%

Заняло больше времени так кроме реализации функционала по ТЗ пришлось решать проблемы с каркасом. О них ниже. Если онм часть задания было бы хорошо сообщить заранее.

Для себя прогнал линтером `pylama` и исправил замечания

Многие версии пакетов устарели и с уязвимостями, как сообщаешт GitHub.
Ничего не обновлял, чтобы не ломать заявленную совместимость `2.6, 2.7, 3.3, 3.4, 3.5 and 3.6`.

Добавьте в ридми, что нужно сделать `python manage.py init_db`

Миграция с data частью не применяется:
```
python manage.py db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
```
Не стал разбираться, тратить время

А почему тут в параметрах Mutable dict `def create_app(extra_config_settings={}):`?

Для решения проблемы `AttributeError: 'Request' object has no attribute 'is_xhr'` пришлось фиксировать версию `werkzeug==0.16.1`

В:
```
@pytest.fixture(scope='function')
def session(db, request):
```
нужно чистить базу, иначе после теста мусор, поправил!

