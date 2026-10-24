import operator
import csv
from pathlib import Path
import os
import pickle
from datetime import datetime, date as datetime_date, time as datetime_time

def get_file_format(name):
    suffix = Path(name).suffix.lower()
    if suffix == ".txt":
        return "txt"
    elif suffix == ".csv":
        return "csv"
    elif suffix in {".pkl", ".pickle"}:
        return "pkl"
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {suffix}")

def try_to_datetime(data):
    full_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d.%m.%Y %H:%M:%S",
        "%d.%m.%Y %H:%M",
    ]
    for fmt in full_formats:
        try:
            return datetime.strptime(data, fmt)
        except ValueError:
            continue
    time_formats = ["%H:%M:%S", "%H:%M"]
    for fmt in time_formats:
        try:
            return datetime.strptime(data, fmt).time()
        except ValueError:
            continue
    date_formats = ["%Y-%m-%d", "%d.%m.%Y"]
    for fmt in date_formats:
        try:
            return datetime.strptime(data, fmt).date()
        except ValueError:
            continue
    return None


def convert_datetime(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, datetime_date):
        return datetime.combine(value, datetime_time())
    if isinstance(value, datetime_time):
        return datetime.combine(datetime_date.today(), value)
    if not isinstance(value, str):
        raise TypeError("Невозможно привести значение к дате или времени")
    result = try_to_datetime(value)
    if result is None:
        raise ValueError("Неверный формат даты или времени")
    return result

def convert_date(value):
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, datetime_date):
        return value
    if not isinstance(value, str):
        raise TypeError("Невозможно привести значение к date")
    result = try_to_datetime(value)
    if isinstance(result, datetime):
        return result.date()
    if isinstance(result, datetime_date):
        return result
    raise ValueError("Неверный формат даты")

def convert_time(value):
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, datetime_time):
        return value
    if not isinstance(value, str):
        raise TypeError("Невозможно привести значение к time")
    result = try_to_datetime(value)
    if isinstance(result, datetime):
        return result.time()
    if isinstance(result, datetime_time):
        return result
    raise ValueError("Неверный формат времени")


def converter(string):
    is_bool = string.strip().lower()
    if is_bool in ('true', 'false'):
        res = is_bool == 'true'
        return res
    try:
        res = int(string)
        return res
    except ValueError:
        try:
            res = float(string)
            return res
        except:
            res = try_to_datetime(string)
            if res == None:
                return string
            return res

def convert_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ('true', '1'):
            return True
        if value in ('false', '0'):
            return False
        raise ValueError("Невозможно привести данные к bool")
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    raise ValueError("Невозможно привести данные к bool")

TYPE_CONVERTERS = {
    'int': int,
    'float': float,
    'str': str,
    'bool': convert_bool,
    'datetime': convert_datetime,
    'date': convert_date,
    'time': convert_time,
}

class Table:
    def __init__(self, data=None, columns=None):
        if data==None and columns==None:
            self._data = {}
        elif isinstance(data, list) and columns==None:
            if not data:
                self._data = {}
                return
            if len(set([len(row) for row in data]))!=1:
                raise ValueError("Строки разной длины")
            if len(set(data[0]))!=len(data[0]):
                raise ValueError("Дубликаты имён столбцов")
            table={}
            for key in data[0]:
                table[key] = []
                index = data[0].index(key)
                for row in data[1:]:
                    table[key].append(row[index])
            self._data = table
        elif isinstance(data, dict) and columns==None:
            lengths = set()
            for cols in data.values():
                lengths.add(len(cols))
            if len(lengths)>1:
                raise ValueError("Во входном словаре списки разной длины")
            self._data = {key: values.copy() for key, values in data.items()}
        else:
            lengths = set([len(row) for row in data])
            lengths.add(len(columns))
            if len(lengths)>1:
                raise ValueError("Длина columns не совпадает с количеством значений в строке")
            if len(set(columns))!=len(columns):
                raise ValueError("Дубликаты имён столбцов")
            table={}
            for key in columns:
                table[key] = []
                index = columns.index(key)
                for row in data:
                    table[key].append(row[index])
            self._data = table
    def convert_column_types(self, data):
        for column_name, column_values in data.items():
            non_none_values = [value for value in column_values if value is not None]
            if not non_none_values:
                continue
            types = {type(value) for value in non_none_values}
            if types <= {int, float} and int in types and float in types:
                data[column_name] = [float(value) if value is not None else None for value in column_values]
            elif len(types) > 1:
                data[column_name] = [str(value) if value is not None else None for value in column_values]
        return data
    def format(self):
        if not self._data:
            return ""
        column_widths = {}
        for column_name, column_values in self._data.items():
            max_width = len(str(column_name))
            for value in column_values:
                max_width = max(max_width, len(str(value)))
            column_widths[column_name] = max_width + 2
        output = ""
        for column_name in self._data:
            output += "{:<{width}}".format(str(column_name),width=column_widths[column_name])
        output += "\n"
        row_count = len(next(iter(self._data.values())))
        for row_index in range(row_count):
            for column_name, column_values in self._data.items():
                output += "{:<{width}}".format(str(column_values[row_index]),width=column_widths[column_name])
            output += "\n"
        return output
    def write_file(self, path, data):
        file_format = get_file_format(path)
        if file_format == "txt":
            with open(path, "w", encoding="utf-8") as file:
                file.write(data)
        elif file_format == "csv":
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(data.keys())
                if data:
                    writer.writerows(zip(*data.values()))
        elif file_format == "pkl":
            with open(path, "wb") as file:
                pickle.dump(data, file)
    def save_table(self, name, max_rows=None):
        file_format = get_file_format(name)
        folders = {
            "txt": "txt",
            "csv": "csv",
            "pkl": "pkl"
        }
        folder = folders[file_format]
        os.makedirs(folder, exist_ok=True)
        filename = Path(name).name
        name = str(Path(folder) / filename)
        if max_rows is None:
            if file_format == "txt":
                self.write_file(name, self.format())
            else:
                self.write_file(name, self._data)
        else:
            if not isinstance(max_rows, int) or max_rows < 1:
                raise ValueError("max_rows должен быть положительным целым числом")
            if file_format == "txt":
                raise ValueError("Разбиение файлов формата .txt не поддерживается")
            if not self._data:
                raise ValueError("Нельзя разбить пустую таблицу на части")
            row_count = len(next(iter(self._data.values())))
            chunk_number = 1
            for start in range(0, row_count, max_rows):
                stop = min(start + max_rows, row_count)
                chunk_data = {column_name: values[start:stop] for column_name, values in self._data.items()}
                part_name = f"{chunk_number}_{filename}"
                part_path = str(Path(folder) / part_name)
                self.write_file(part_path, chunk_data)
                chunk_number += 1
    def load_table(self, *name):
        if len(name) > 1:
            file_names = list(name)
            merged_data = {}
            for file_name in file_names:
                if get_file_format(file_name) == 'csv':
                    file_data = {}
                    with open(file_name, mode='r', newline='', encoding='utf-8') as csv_file:
                        reader = csv.DictReader(csv_file)
                        for column_name in reader.fieldnames:
                            file_data[column_name] = []
                        for row in reader:
                            for column_name in reader.fieldnames:
                                value = row[column_name]
                                if value is not None and value != '':
                                    value = converter(value)
                                    file_data[column_name].append(value)
                                else:
                                    file_data[column_name].append(None)
                        file_data = self.convert_column_types(file_data)
                elif get_file_format(file_name) == 'pkl':
                    file_data = {}
                    with open(file_name, 'rb') as input_file:
                        file_data = pickle.load(input_file)
                else:
                    raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl")
                if not merged_data:
                    merged_data = {column_name: values.copy() for column_name, values in file_data.items()}
                else:
                    if set(file_data.keys()) != set(merged_data.keys()):
                        raise ValueError("Таблицы не могут быть объединены: различаются наборы столбцов")
                    for column_name in merged_data:
                        merged_data[column_name].extend(file_data[column_name])
            merged_data = self.convert_column_types(merged_data)
            self._data = merged_data
        else:
            name = name[0]
            if get_file_format(name) == 'csv':
                self._data = {}
                with open(name, mode='r', newline='', encoding='utf-8') as csv_file:
                    reader = csv.DictReader(csv_file)
                    for column_name in reader.fieldnames:
                        self._data[column_name] = []
                    for row in reader:
                        for column_name in reader.fieldnames:
                            value = row[column_name]
                            if value is not None and value != '':
                                value = converter(value)
                                self._data[column_name].append(value)
                            else:
                                self._data[column_name].append(None)
                self._data = self.convert_column_types(self._data)
            elif get_file_format(name) == 'pkl':
                with open(name, 'rb') as input_file:
                    self._data = pickle.load(input_file)
            else:
                raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl")
    def get_rows_by_number(self, start, stop=None, copy_table=True):
        row_count = len(next(iter(self._data.values()))) if self._data else 0
        if stop is None:
            stop = start + 1
        if not (0 <= start <= stop <= row_count):
            raise IndexError("Недопустимый диапазон строк")
        result = {}
        for column_name, column_values in self._data.items():
            result[column_name] = column_values[start:stop]
        if copy_table:
            return Table(result)   
        else:
            self._data = result
            return self._data
    def get_rows_by_index(self, *vals, copy_table=True):
        result = {}
        for column_name in self._data.keys():
            result[column_name] = []
        found = 0
        for search_value in vals:
            column_values = list(self._data.values())
            for row_index in range(len(column_values[0])):
                if column_values[0][row_index] == search_value:
                    for column_name, values in self._data.items():
                        result[column_name].append(values[row_index])
                        found = 1
        if found == 0:
            raise ValueError("Указанные значения не найдены в первом столбце таблицы")
        if copy_table:
            return Table(result)
        else:
            self._data = result
            return self._data
    def get_column_types(self, by_number=True):
        column_types = {}
        for column_name, column_values in self._data.items():
            values = [value for value in column_values if value is not None]
            column_types[column_name] = (type(values[0]).__name__ if values else 'NoneType')
        if by_number:
            return {i: column_types[name] for i, name in enumerate(self._data)}
        return column_types
    def set_column_types(self, types_dict, by_number=True):
        if by_number:
            column_names = list(self._data.keys())
            types_dict = {column_names[index]: column_type for index, column_type in types_dict.items()}
        for column_name, column_type in types_dict.items():
            if column_type not in TYPE_CONVERTERS:
                raise ValueError(f"Неподдерживаемый тип данных: {column_type}")
            try:
                self._data[column_name] = [None if value is None else TYPE_CONVERTERS[column_type](value) for value in self._data[column_name]]
            except (TypeError, ValueError, OverflowError) as error:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
    def get_values(self, column=0):
        if isinstance(column, str):
            if not self._data[column]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column]
        else:
            column_names = list(self._data.keys())
            if not self._data[column_names[column]]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column_names[column]]
    def get_value(self, column=0):
        if isinstance(column, str):
            if not self._data[column]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column][0]
        else:
            column_names = list(self._data.keys())
            if not self._data[column_names[column]]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column_names[column]][0]
    def set_values(self, values, column=0):
        column_name = list(self._data)[column] if isinstance(column, int) else column
        row_count = len(self._data[column_name])
        if len(values) != row_count:
            raise ValueError("Количество значений не совпадает с количеством строк таблицы")
        column_type = self.get_column_types(by_number=False)[column_name]
        converter_func = TYPE_CONVERTERS.get(column_type)
        if converter_func is None:
            raise ValueError(f"Неподдерживаемый тип данных: {column_type}")
        try:
            self._data[column_name] = [None if value is None else converter_func(value) for value in values]
        except (TypeError, ValueError):
            raise TypeError("Невозможно привести данные столбца к указанному типу")
    def set_value(self, value, column=0):
        self.set_values([value], column)
    def concat(self, table):
        if self._data.keys() == table.keys():
            for column_name in self._data.keys():
                self._data[column_name].extend(table[column_name])
        else:
            raise ValueError("Невозможно объединить таблицы: не совпадают имена колонок")
        return self._data
    def split(self, row_number):
        first_part = {}
        second_part = {}
        for column_name, column_values in self._data.items():
            first_part[column_name] = column_values[:row_number]
            second_part[column_name] = column_values[row_number:]
        return first_part, second_part
    def _binop(self, a, b, op):
        if a not in self._data or b not in self._data:
            raise KeyError("Столбец не найден")
        result = []
        for row_index, (x, y) in enumerate(zip(self._data[a], self._data[b])):
            try:
                result.append(op(x, y))
            except TypeError:
                raise TypeError(f"Операция не применима к данным в строке {row_index}")
        return result
    def add(self, a, b):
        return self._binop(a, b, operator.add)
    def sub(self, a, b):
        return self._binop(a, b, operator.sub)
    def mul(self, a, b):
        return self._binop(a, b, operator.mul)
    def div(self, a, b):
        return self._binop(a, b, operator.truediv)
    def eq(self, a, b):
        return self._binop(a, b, operator.eq)
    def ne(self, a, b):
        return self._binop(a, b, operator.ne)
    def gr(self, a, b):
        return self._binop(a, b, operator.gt)
    def ls(self, a, b):
        return self._binop(a, b, operator.lt)
    def ge(self, a, b):
        return self._binop(a, b, operator.ge)
    def le(self, a, b):
        return self._binop(a, b, operator.le)
    def filter_rows(self, bool_list, copy_table=False):
        total_rows = len(list(self._data.values())[0]) if self._data else 0
        if len(bool_list) != total_rows:
            raise ValueError("Длина bool_list не совпадает с количеством строк таблицы")
        result = {}
        for column_name in self._data.keys():
            result[column_name] = []
        for row_index in range(len(bool_list)):
            if bool_list[row_index] == True:
                for column_name, column_values in self._data.items():
                    result[column_name].append(column_values[row_index])
        if copy_table == True:
            return result
        else:
            self._data = result
            return self._data
    def merge_tables(self, table, by_number=True):
        if not isinstance(table, dict):
            raise TypeError("table должен быть словарём")
        if not self._data or not table:
            raise ValueError("Таблицы не должны быть пустыми")
        self_lengths = {len(values) for values in self._data.values()}
        table_lengths = {len(values) for values in table.values()}
        if len(self_lengths) > 1 or len(table_lengths) > 1:
            raise ValueError("Столбцы внутри таблицы имеют разную длину")
        if by_number:
            common_columns = set(self._data) & set(table)
            if common_columns:
                raise ValueError("Таблицы не должны иметь одинаковых столбцов")
            self_row_count = next(iter(self_lengths))
            table_row_count = next(iter(table_lengths))
            if self_row_count != table_row_count:
                raise ValueError("Таблицы различной длины")
            self._data.update({column_name: values.copy() for column_name, values in table.items()})
        else:
            self_key = next(iter(self._data))
            table_key = next(iter(table))
            if self_key != table_key:
                raise ValueError("Первый столбец обеих таблиц должен быть общим индексом")
            common_columns = set(self._data) & set(table)
            if common_columns != {self_key}:
                raise ValueError("Таблицы должны иметь только один общий столбец — первый индексный")
            self_index_values = self._data[self_key]
            table_index_values = table[table_key]
            if (len(set(self_index_values)) != len(self_index_values) or len(set(table_index_values)) != len(table_index_values)):
                raise ValueError("Первый столбец содержит неуникальные значения (дубликаты)")
            table_index = {value: row_index for row_index, value in enumerate(table_index_values)}
            matched_rows = [(self_row, table_index[value]) for self_row, value in enumerate(self_index_values) if value in table_index]
            merged_data = {}
            for column_name, values in self._data.items():
                merged_data[column_name] = [values[self_row] for self_row, _ in matched_rows]
            for column_name, values in table.items():
                if column_name == table_key:
                    continue
                merged_data[column_name] = [values[table_row] for _, table_row in matched_rows]
            self._data = merged_data
        return self._data
    def __str__(self):
        return self.format()