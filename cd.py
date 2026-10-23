import csv
import pickle
from datetime import datetime

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

def converter(s):
    sbool = s.strip().lower()
    if sbool in ('true', 'false'):
        res = sbool == 'true'
        return res
    try:
        res = int(s)
        return res
    except ValueError:
        try:
            res = float(s)
            return res
        except:
            res = try_to_datetime(s)
            if res == None:
                return s
            return res

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
    def save_table(self, name, max_rows=1):
        if max_rows > 0:
            full_chunks = len(list(self._data.values())[0])//max_rows
            remainder_rows = len(list(self._data.values())[0])%max_rows
            for i in range(full_chunks):
                file_name = str(i+1) + name
                chunk_data = self.get_rows_by_number(i*max_rows, (i*max_rows) + max_rows, copy_table=True)
                if file_name[-3:] == 'csv':
                    column_names = list(chunk_data.keys())
                    rows = list(zip(*chunk_data.values()))
                    with open(file_name, mode = "w", newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(column_names)
                        writer.writerows(rows)
                elif file_name[-3:] == 'pkl' or file_name[-3:] == 'kle':
                    with open(file_name, 'wb') as output_file:
                        pickle.dump(chunk_data, output_file)
            if remainder_rows!=0:
                file_name = 'last_'+name
                remainder_data = self.get_rows_by_number(len(list(self._data.values())[0])-remainder_rows, len(list(self._data.values())[0]), copy_table=True)
                if file_name[-3:] == 'csv':
                    column_names = list(remainder_data.keys())
                    rows = list(zip(*remainder_data.values()))
                    with open(file_name, mode = "w", newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(column_names)
                        writer.writerows(rows)
                elif file_name[-3:] == 'pkl' or file_name[-3:] == 'kle':
                    with open(file_name, 'wb') as output_file:
                        pickle.dump(remainder_data, output_file)
        else:
            if name[-3:] == 'txt':
                column_widths = {}
                for column_name, column_values in self._data.items():
                    max_width = len(str(column_name))
                    for i in column_values:
                        if len(str(i)) > max_width:
                            max_width = len(str(i))
                    column_widths[column_name] = max_width + 2
                output = ""
                for column_names in self._data.keys():
                    output += "{:<{width}}".format(str(column_names), width=column_widths[column_names])
                output+='\n'
                for i in range(len(list(self._data.values())[0])):
                    for column_names, rows in self._data.items():
                        output += "{:<{width}}".format(str(rows[i]), width=column_widths[column_names])
                    output+='\n'
                with open(name, 'w') as output_file:
                    output_file.write(output)
            elif name[-3:] == 'csv':
                column_names = list(self._data.keys())
                rows = list(zip(*self._data.values()))
                with open(name, mode = "w", newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(column_names)
                    writer.writerows(rows)
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'wb') as output_file:
                    pickle.dump(self._data, output_file)
            else:
                raise ValueError("Неизвестный формат файла. Поддерживаются только .txt, .csv, .pkl")
            print(f"Сохранено в файл {name}")
    def load_table(self, *name):
        if len(name) > 1:
            file_names = list(name)
            merged_data = {}
            for file_name in file_names:
                if file_name[-3:] == 'csv':
                    file_data = {}
                    with open(file_name, mode='r') as csv_file:
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
                elif file_name[-3:] == 'pkl' or file_name[-3:] == 'kle':
                    file_data = {}
                    with open(file_name, 'rb') as input_file:
                        file_data = pickle.load(input_file)
                else:
                    raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl")
                if not merged_data:
                    for column_name in file_data.keys():
                        merged_data[column_name] = []
                for column_name in file_data.keys():
                    try:
                        merged_data[column_name].extend(file_data[column_name])
                    except:
                        raise ValueError("Таблицы не могут быть объединены: различаются наборы столбцов")
            self._data = merged_data
        else:
            name = name[0]
            if name[-3:] == 'csv':
                self._data = {}
                with open(name, mode='r') as csv_file:
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
                for column_name, column_values in self._data.items():
                    is_homogeneous = True
                    for value in column_values:
                        if type(self._data[column_name][0]) != type(value):
                            is_homogeneous = False
                    if is_homogeneous == False:
                        self._data[column_name] = [str(value) for value in column_values]
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'rb') as input_file:
                    self._data = pickle.load(input_file)
            else:
                raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl")
        print("Загружено в таблицу _data")
    def get_rows_by_number(self, start, stop=0, copy_table=False):
        if stop == 0:
            stop = start + 1
        if stop < start:
            raise IndexError("Неверный диапазон: конечный индекс не может быть меньше начального")
        result = {}
        for column_name in self._data.keys():
            result[column_name] = []
        for row_index in range(start, stop):
            for column_name, column_values in self._data.items():
                result[column_name].append(column_values[row_index])
        if copy_table == True:
            print("Копия таблицы сохранена")
            return result
        else:
            self._data = result
            print("Сохранено в исходную таблицу")
            return self._data
    def get_rows_by_index(self, *vals, copy_table=False):
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
        if copy_table == True:
            print("Копия таблицы сохранена")
            return result
        else:
            self._data = result
            print("Сохранено в исходную таблицу")
            return self._data
    def get_column_types(self, by_number=True):
        column_types = {}
        for column_name, column_values in self._data.items():
            if not column_values:
                raise ValueError(f"Невозможно определить тип данных: колонка '{column_name}' пуста.")
            column_types[column_name] = type(column_values[0]).__name__
        columns = {}
        if by_number == True:
            column_names = list(self._data.keys())
            for column_name in self._data.keys():
                columns[column_names.index(column_name)] = column_types[column_name]
        else:
            for column_name in self._data.keys():
                columns[column_name] = column_types[column_name]
        return columns
    def set_column_types(self, types_dict, by_number=True):
        if by_number == True:
            column_types = {}
            column_names = list(self._data.keys())
            for column_index, column_type in types_dict.items():
                column_types[column_names[column_index]] = column_type
            types_dict = column_types
        for column_name, column_type in types_dict.items():
            column_values = self._data[column_name]
            match column_type:
                case 'str':
                    column_values = [str(value) for value in column_values]
                case 'int':
                    try:
                        column_values = [int(value) for value in column_values]
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'float':
                    try:
                        column_values = [float(value) for value in column_values]
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'bool':
                    try:
                        new_values = []
                        for value in column_values:
                            if isinstance(value, str):
                                bool_value = value.strip().lower()
                                if bool_value in ('true', '1'):
                                    new_values.append(True)
                                elif bool_value in ('false', '0'):
                                    new_values.append(False)
                                else:
                                    raise TypeError("Невозможно привести данные столбца к указанному типу")
                            else:
                                new_values.append(bool(value))
                        column_values = new_values
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'datetime':
                    column_values = [try_to_datetime(value) for value in column_values]
                    if None in column_values:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
            self._data[column_name] = column_values
        print("Типы элементов таблицы изменены")
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
        if isinstance(column, str):
            value_type = eval(self.get_column_types(by_number=False)[column])
            try:
                self._data[column] = [value_type(value) for value in values]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
        else:
            value_type = eval(self.get_column_types(by_number=True)[column])
            column_names = list(self._data.keys())
            try:
                self._data[column_names[column]] = [value_type(value) for value in values]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
    def set_value(self, value, column=0):
        if isinstance(column, str):
            value_type = eval(self.get_column_types(by_number=False)[column])
            try:
                self._data[column] = [value_type(value)]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
        else:
            value_type = eval(self.get_column_types(by_number=True)[column])
            column_names = list(self._data.keys())
            try:
                self._data[column_names[column]] = [value_type(value)]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
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
    def add(self, *keys):
        if len(keys)>1:
            result = [0] * len(list(self._data.values())[0])
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value = self._data[column_name][row_index]
                    try:
                        result[row_index] += value
                    except:
                        raise TypeError(f"Операция не применима к нечисловым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")    
    def sub(self, *keys):
        if len(keys)>1:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] -= value
                        except:
                            raise TypeError(f"Операция не применима к нечисловым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def mul(self, *keys):
        if len(keys)>1:
            result = [1] * len(list(self._data.values())[0])
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    try:
                        result[row_index] *= value
                    except:
                        raise TypeError(f"Операция не применима к нечисловым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def div(self, *keys):
        if len(keys)>1:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] /= value
                        except ZeroDivisionError:
                            raise ZeroDivisionError(f"Деление на ноль в строке {row_index} на значение из столбца '{column_name}'")
                        except TypeError:
                            raise TypeError(f"Невозможно выполнить деление для нечислового типа данных в столбце '{column_name}'")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def eq(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        result[row_index] = result[row_index] == value
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def gr(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] = result[row_index] > value
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ls(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] = result[row_index] < value
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ge(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] = result[row_index] >= value
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def le(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        try:
                            result[row_index] = result[row_index] <= value
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {row_index}")
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ne(self, *keys):
        if len(keys)==2:
            result = []
            for column_name in keys:
                for row_index in range(len(self._data[column_name])):
                    value=self._data[column_name][row_index]
                    if keys[0] == column_name:
                        result.append(value)
                    else:
                        result[row_index] = result[row_index] != value
            return result
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
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
            print("Копия таблицы сохранена")
            return result
        else:
            self._data = result
            print("Сохранено в исходную таблицу")
            return self._data
    def merge_tables(self, table, by_number=True):
        if by_number == True:
            common_columns = set(self._data.keys()) & set(table.keys())
            if len(common_columns) > 0:
                raise ValueError("Таблицы не должны иметь одинаковых столбцов")
            if len(list(self._data.values())[0])!=len(list(table.values())[0]):
                raise ValueError("Таблицы различной длины")
            self._data.update(table)
        else:
            common_columns = set(self._data.keys()) & set(table.keys())
            if len(common_columns) > 1:
                raise ValueError("Таблицы не должны иметь одинаковых столбцов(Кроме первого, который отвечает за индексы)")
            self_index_values = list(self._data.values())[0]
            table_index_values = list(table.values())[0]
            if len(set(table_index_values))!=len(table_index_values) or len(set(self_index_values))!=len(self_index_values):
                raise ValueError("Первый столбец содержит неуникальные значения (дубликаты)")
            for column_name in table.keys():
                self._data[column_name] = []
            for self_index_value in self_index_values:
                for table_index_value in table_index_values:
                    if self_index_value == table_index_value:
                        row_index = table_index_values.index(table_index_value)
                        for column_name, column_values in table.items():
                            self._data[column_name].append(column_values[row_index])
    def print_table(self):
        column_widths = {}
        for column_name, column_values in self._data.items():
            max_width = len(str(column_name))
            for value in column_values:
                if len(str(value)) > max_width:
                    max_width = len(str(value))
            column_widths[column_name] = max_width + 2
        output = "\n"
        for column_name in self._data.keys():
            output += "{:<{width}}".format(str(column_name), width=column_widths[column_name])
        output+='\n'
        for row_index in range(len(list(self._data.values())[0])):
            for column_name, column_values in self._data.items():
                output += "{:<{width}}".format(str(column_values[row_index]), width=column_widths[column_name])
            output+='\n'
        print(output)

t = Table([['a','b'], ['Вася', 17], ['Петя', 18]])
t.print_table()