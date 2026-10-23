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
            kol = len(list(self._data.values())[0])//max_rows
            last = len(list(self._data.values())[0])%max_rows
            for i in range(kol):
                file = str(i+1) + name
                ct = self.get_rows_by_number(i*max_rows, (i*max_rows) + max_rows, copy_table=True)
                if file[-3:] == 'csv':
                    col = list(ct.keys())
                    lin = list(zip(*ct.values()))
                    with open(file, mode = "w", newline='') as fw:
                        writer = csv.writer(fw)
                        writer.writerow(col)
                        writer.writerows(lin)
                elif file[-3:] == 'pkl' or file[-3:] == 'kle':
                    with open(file, 'wb') as fw:
                        pickle.dump(ct, fw)
            if last!=0:
                file = 'last_'+name
                ct = self.get_rows_by_number(len(list(self._data.values())[0])-last, len(list(self._data.values())[0]), copy_table=True)
                if file[-3:] == 'csv':
                    col = list(ct.keys())
                    lin = list(zip(*ct.values()))
                    with open(file, mode = "w", newline='') as fw:
                        writer = csv.writer(fw)
                        writer.writerow(col)
                        writer.writerows(lin)
                elif file[-3:] == 'pkl' or file[-3:] == 'kle':
                    with open(file, 'wb') as fw:
                        pickle.dump(ct, fw)
        else:
            if name[-3:] == 'txt':
                wid = {}
                for nm, val in self._data.items():
                    maxl = len(str(nm))
                    for i in val:
                        if len(str(i)) > maxl:
                            maxl = len(str(i))
                    wid[nm] = maxl + 2
                sr = ""
                for col in self._data.keys():
                    sr += "{:<{width}}".format(str(col), width=wid[col])
                sr+='\n'
                for i in range(len(list(self._data.values())[0])):
                    for col, lin in self._data.items():
                        sr += "{:<{width}}".format(str(lin[i]), width=wid[col])
                    sr+='\n'
                with open(name, 'w') as fw:
                    fw.write(sr)
            elif name[-3:] == 'csv':
                col = list(self._data.keys())
                lin = list(zip(*self._data.values()))
                with open(name, mode = "w", newline='') as fw:
                    writer = csv.writer(fw)
                    writer.writerow(col)
                    writer.writerows(lin)
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'wb') as fw:
                    pickle.dump(self._data, fw)
            else:
                raise ValueError("Неизвестный формат файла. Поддерживаются только .txt, .csv, .pkl")
            print(f"Сохранено в файл {name}")
    def load_table(self,*name):
        if len(list(name)) > 1:
            files = list(name)
            ct={}
            for file in files:
                if file[-3:]=='csv':
                    tct={}
                    with open(file, mode='r') as fw:
                        reader = csv.DictReader(fw)
                        for col in reader.fieldnames:
                            tct[col] = []
                        for lin in reader:
                            for col in reader.fieldnames:
                                val = lin[col]
                                if val!=None and val!='':
                                    val = converter(val)
                                    tct[col].append(val)
                                else:
                                    tct[col].append(None)
                elif file[-3:] == 'pkl' or file[-3:] == 'kle':
                    tct={}
                    with open(file, 'rb') as fw:
                        tct = pickle.load(fw)
                else:
                    raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl") 
                if not ct:
                    for k in tct.keys():
                        ct[k] = []
                for k in tct.keys():
                    try:
                        ct[k].extend(tct[k])
                    except:
                        raise ValueError("Таблицы не могут быть объединены: различаются наборы столбцов")
            self._data = ct
        else:
            name = name[0]
            if name[-3:]=='csv':
                self._data={}
                with open(name, mode='r') as fw:
                    reader = csv.DictReader(fw)
                    for col in reader.fieldnames:
                        self._data[col] = []
                    for lin in reader:
                        for col in reader.fieldnames:
                            val = lin[col]
                            if val!=None and val!='':
                                val = converter(val)
                                self._data[col].append(val)
                            else:
                                self._data[col].append(None)
                for k, vals in self._data.items():
                    f = True
                    for v in vals:
                        if type(self._data[k][0]) != type(v):
                            f = False
                    if f == False:
                        self._data[k] = [str(v) for v in vals]
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'rb') as fw:
                    self._data = pickle.load(fw)
            else:
                raise ValueError("Неизвестный формат файла. Поддерживаются только .csv, .pkl") 
        print("Загружено в таблицу _data")
    def get_rows_by_number(self, start, stop=0, copy_table=False):
        if stop == 0:
            stop = start + 1
        if stop < start:  
            raise IndexError("Неверный диапазон: конечный индекс не может быть меньше начального") 
        ct = {}
        for k in self._data.keys():
            ct[k]=[]
        for i in range(start, stop):
            for k, val in self._data.items():
                ct[k].append(val[i])
        if copy_table == True:
            print("Копия таблицы сохранена")
            return ct
        else:
            self._data = ct
            print("Сохранено в исходную таблицу")
            return self._data
    def get_rows_by_index(self, *vals, copy_table=False):
        ct={}
        for k in self._data.keys():
            ct[k]=[]
        f = 0
        for v in vals:
            val = list(self._data.values())
            for i in range(len(val[0])):
                if val[0][i] == v:
                    for k, elem in self._data.items():
                        ct[k].append(elem[i])
                        f = 1
        if f == 0:
            raise ValueError("Указанные значения не найдены в первом столбце таблицы")
        if copy_table == True:
            print("Копия таблицы сохранена")
            return ct
        else:
            self._data = ct
            print("Сохранено в исходную таблицу")
            return self._data
    def get_column_types(self, by_number=True):
        ct = {}
        for k, vals in self._data.items():
            if not vals:
                raise ValueError(f"Невозможно определить тип данных: колонка '{k}' пуста.")
            ct[k]=type(vals[0]).__name__
        columns = {}
        if by_number == True:
            keys_index = list(self._data.keys())
            for k in self._data.keys():
                columns[keys_index.index(k)] = ct[k]
        else:
            for i in self._data.keys():
                columns[i] = ct[i]
        return columns
    def set_column_types(self, types_dict, by_number=True):
        if by_number == True:
            ct = {}
            keys_index = list(self._data.keys())
            for k, v in types_dict.items():
                ct[keys_index[k]] = v
            types_dict = ct
        for k, v in types_dict.items():
            vals = self._data[k]
            match v:
                case 'str':
                    vals = [str(x) for x in vals]
                case 'int':
                    try:
                        vals = [int(x) for x in vals]
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'float':
                    try:
                        vals = [float(x) for x in vals]
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'bool':
                    try:
                        new_vals = []
                        for x in vals:
                            if isinstance(x, str):
                                xbool = x.strip().lower()
                                if xbool in ('true', '1'):
                                    new_vals.append(True)
                                elif xbool in ('false', '0'):
                                    new_vals.append(False)
                                else:
                                    raise TypeError("Невозможно привести данные столбца к указанному типу")
                            else:
                                new_vals.append(bool(x))
                        vals = new_vals
                    except:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
                case 'datetime':
                    vals = [try_to_datetime(x) for x in vals]
                    if None in vals:
                        raise TypeError("Невозможно привести данные столбца к указанному типу")
            self._data[k]=vals
        print("Типы элементов таблицы изменены")
    def get_values(self, column=0):
        if isinstance(column, str):
            if not self._data[column]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column]
        else:
            keys_index = list(self._data.keys())
            if  not self._data[keys_index[column]]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[keys_index[column]]
    def get_value(self, column=0):
        if isinstance(column, str):
            if not self._data[column]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[column][0]
        else:
            keys_index = list(self._data.keys())
            if not self._data[keys_index[column]]:
                raise ValueError("Столбец пуст, невозможно получить значение")
            return self._data[keys_index[column]][0]
    def set_values(self, values, column=0):
        if isinstance(column, str):
            identifier = eval(self.get_column_types(by_number=False)[column])
            try:
                self._data[column] = [identifier(x) for x in values]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
        else:
            identifier = eval(self.get_column_types(by_number=True)[column])
            keys_index = list(self._data.keys())
            try:
                self._data[keys_index[column]] = [identifier(x) for x in values]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
    def set_value(self, value, column=0):
        if isinstance(column, str):
            identifier = eval(self.get_column_types(by_number=False)[column])
            try:
                self._data[column] = [identifier(value)]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу")
        else:
            identifier = eval(self.get_column_types(by_number=True)[column])
            keys_index = list(self._data.keys())
            try:
                self._data[keys_index[column]] = [identifier(value)]
            except:
                raise TypeError("Невозможно привести данные столбца к указанному типу") 
    def concat(self, table):
        if self._data.keys() == table.keys():
            for k in self._data.keys():
                self._data[k].extend(table[k])
        else:
            raise ValueError("Невозможно объединить таблицы: не совпадают имена колонок")
        return self._data
    def split(self, row_number):
        ct1 = {}
        ct2 = {}
        for k, v in self._data.items():
            ct1[k] = v[:row_number]
            ct2[k] = v[row_number:]
        return ct1, ct2
    def add(self, *keys):
        if len(keys)>1:
            res = [0] * len(list(self._data.values())[0])
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    try:
                        res[i] += v
                    except:
                        raise TypeError(f"Операция не применима к нечисловым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def sub(self, *keys):
        if len(keys)>1:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] -= v
                        except:
                            raise TypeError(f"Операция не применима к нечисловым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def mul(self, *keys):
        if len(keys)>1:
            res = [1] * len(list(self._data.values())[0])
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    try:
                        res[i] *= v
                    except:
                        raise TypeError(f"Операция не применима к нечисловым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def div(self, *keys):
        if len(keys)>1:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] /= v
                        except ZeroDivisionError:
                            raise ZeroDivisionError(f"Деление на ноль в строке {i} на значение из столбца '{k}'")
                        except TypeError:
                            raise TypeError(f"Невозможно выполнить деление для нечислового типа данных в столбце '{k}'")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать как минимум два столбца")
    def eq(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        res[i] = res[i] == v
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def gr(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] = res[i] > v
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ls(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] = res[i] < v
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ge(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] = res[i] >= v
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def le(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        try:
                            res[i] = res[i] <= v
                        except:
                            raise TypeError(f"Операция не применима к несовместимым данным в строке {i}")
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def ne(self, *keys):
        if len(keys)==2:
            res = []
            for k in keys:
                for i in range(len(self._data[k])):
                    v=self._data[k][i]
                    if keys[0] == k:
                        res.append(v)
                    else:
                        res[i] = res[i] != v
            return res
        else:
            raise ValueError("Для выполнения операции необходимо передать два столбца")
    def filter_rows(self, bool_list, copy_table=False):
        total_rows = len(list(self._data.values())[0]) if self._data else 0
        if len(bool_list) != total_rows:
            raise ValueError("Длина bool_list не совпадает с количеством строк таблицы")
        ct = {}
        for k in self._data.keys():
            ct[k] = []
        for i in range(len(bool_list)):
            if bool_list[i] == True:
                for k, v in self._data.items():
                    ct[k].append(v[i])
        if copy_table == True:
            print("Копия таблицы сохранена")
            return ct
        else:
            self._data = ct
            print("Сохранено в исходную таблицу")
            return self._data
    def merge_tables(self, table, by_number=True):
        if by_number == True:
            common_cols = set(self._data.keys()) & set(table.keys())
            if len(common_cols) > 0:
                raise ValueError("Таблицы не должны иметь одинаковых столбцов")
            if len(list(self._data.values())[0])!=len(list(table.values())[0]):
                raise ValueError("Таблицы различной длины")
            self._data.update(table)
        else:
            common_cols = set(self._data.keys()) & set(table.keys())
            if len(common_cols) > 1:
                raise ValueError("Таблицы не должны иметь одинаковых столбцов(Кроме первого, который отвечает за индексы)")
            id_index_self = list(self._data.values())[0]
            id_index_table = list(table.values())[0]
            if len(set(id_index_table))!=len(id_index_table) or len(set(id_index_self))!=len(id_index_self):
                raise ValueError("Первый столбец содержит неуникальные значения (дубликаты)")
            for k in table.keys():
                self._data[k] = []
            for i in id_index_self:
                for j in id_index_table:
                    if i == j:
                        id = id_index_table.index(j)
                        for k, v in table.items():
                            self._data[k].append(v[id])
    def print_table(self):
        wid = {}
        for nm, val in self._data.items():
            maxl = len(str(nm))
            for i in val:
                if len(str(i)) > maxl:
                    maxl = len(str(i))
            wid[nm] = maxl + 2
        sr = "\n"
        for col in self._data.keys():
            sr += "{:<{width}}".format(str(col), width=wid[col])
        sr+='\n'
        for i in range(len(list(self._data.values())[0])):
            for col, lin in self._data.items():
                sr += "{:<{width}}".format(str(lin[i]), width=wid[col])
            sr+='\n'
        print(sr)

t = Table([['a','b'], ['Вася', 17], ['Петя', 18]])
t.print_table()