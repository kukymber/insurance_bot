from functools import cached_property
from math import ceil
from typing import List


class PaginatorException(Exception):
    """Ошибки связанные с пагинацией"""
    ...


class EmptyPage(PaginatorException):
    """Пустая страница"""
    ...

__all__ = (
    "Paginator",
    "Page"
)


class Paginator:
    default_error_messages = {
        "invalid_page": "Страница не является цело численным значением",
        "min_page": "Значение меньше 1",
        "no_results": "Страница пустая",
    }

    def __init__(self, object_list: List, per_page: int) -> None:
        self.object_list = object_list
        self.per_page = per_page

    def validate_number(self, number: int) -> int:
        """Валидация переданного значения."""
        if number < 1:
            raise EmptyPage(self.default_error_messages["min_page"])
        if number > self.num_pages:
            raise EmptyPage(self.default_error_messages["no_results"])
        return number

    def page(self, number) -> 'Page':
        """Метод возвращает объект страницы."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top >= self.count:
            top = self.count
        return self._get_page(self.object_list[bottom:top], number, self)

    @staticmethod
    def _get_page(object_list: List, number: int, paginator) -> 'Page':
        """Метод генерирует объект страницы"""
        return Page(object_list, number, paginator)

    @cached_property
    def count(self) -> int:
        """Метод возвращает количество элементов в массиве"""
        return len(self.object_list)

    @cached_property
    def num_pages(self) -> int:
        """Метод возвращает сколько всего возможно страниц."""
        return ceil(self.count / self.per_page)


class Page:

    def __init__(self, object_list: List, number: int, paginator: Paginator) -> None:
        self.object_list = object_list
        self.number = number
        self.paginator = paginator

    def __repr__(self) -> str:
        return f"<Page. {self.number} из {self.paginator.num_pages}>"

    def __len__(self) -> int:
        return len(self.object_list)

    def has_next(self) -> bool:
        return self.number < self.paginator.num_pages

    def has_previous(self) -> bool:
        return self.number > 1

    def has_other_pages(self) -> bool:
        return self.has_previous() or self.has_next()

    def next_page_number(self) -> int:
        return self.paginator.validate_number(self.number + 1)

    def previous_page_number(self) -> int:
        return self.paginator.validate_number(self.number - 1)

    def start_index(self) -> int:
        """Возвращает индекс начала"""
        if self.paginator.count == 0:
            return 0
        return (self.paginator.per_page * (self.number - 1)) + 1

    def end_index(self) -> int:
        """Возвращает последний индекс"""
        if self.number == self.paginator.num_pages:
            return self.paginator.count
        return self.number * self.paginator.per_page
