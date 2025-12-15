import re
import csv
from typing import Optional, List


def csv_to_list(file_path: str) -> Optional[List[List[str]]]:
    """
    Читает CSV файл и возвращает список строк, исключая первую строку.

    Returns:
        Список строк (каждая строка представлена как список),
        или None в случае ошибки.
    """
    try:
        with open(file_path, mode="r", encoding="utf-16") as file:
            reader = csv.reader(file, delimiter=';')
            next(reader)  # Пропускаем первую строку
            return [row for row in reader]
    except Exception as e:
        print(f"Ошибка при чтении CSV файла: {str(e)}.")
        return None


def is_valid_row(pattern: dict, row: List[str]) -> bool:
    """
    Проверяет строку на соответствие регулярным выражениям.

    Returns:
        bool: True, если строка соответствует всем шаблонам, иначе False.
    """
    return all(re.match(pattern[key], data) for key, data in zip(pattern.keys(), row))


def get_invalid_indices(pattern: dict, data: List[List[str]]) -> Optional[List[int]]:
    """
    Проверяет все строки и возвращает список индексов некорректных строк.

    Returns:
        Список индексов некорректных строк, или None в случае ошибки.
    """
    invalid_indices = [i for i, row in enumerate(data) if not is_valid_row(pattern, row)]
    return invalid_indices