# TLISP
Диалект LISP'а на Python.

Написанный где-то в 260 строк кода.
# Туториал
Здесь есть команд (нет) и функций (тоже нет)

Вот они все:
* if (кондиция) (если) (иначе)
* quote всё что хочешь
* begin куча выражений
* lambda аргументы выражение
* def имя выражение
* with имя-модуля (ещё наверно не стабильно)
* dict (имя значения) (имя значение)...
* list значение значение...
* cons элемент список
* append список элемент
* remove список элемент
* car список
* cdr список
* t (истина)
* nil (ложь или пустота)
* py выражение_пайтона
* nth список индекс
* princ куча_выражений
* getk словарь имя_ключа (сооветую использовать "(quote имя_ключа)")

Долго их объяснять, но можете подсмотреть примеры.

# Заключение
А что тут должно быть? Ну много он умеет.

В том числе и достаточно нормальный REPL.

Так же можете попытаться разобрать исходники и понять чё к чему.
