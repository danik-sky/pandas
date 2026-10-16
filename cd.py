import csv
import pickle

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
            return s

class Table:
    def save_table(self, name, max_rows=1):
        if max_rows > 1:
            kol = len(list(self.tabl.values())[0])//max_rows
            last = len(list(self.tabl.values())[0])%max_rows
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
                ct = self.get_rows_by_number(len(list(self.tabl.values())[0])-last, len(list(self.tabl.values())[0]), copy_table=True)
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
                for nm, val in self.tabl.items():
                    maxl = len(str(nm))
                    for i in val:
                        if len(str(i)) > maxl:
                            maxl = len(str(i))
                    wid[nm] = maxl + 2
                sr = ""
                for col in self.tabl.keys():
                    sr += "{:<{width}}".format(str(col), width=wid[col])
                sr+='\n'
                for i in range(len(list(self.tabl.values())[0])):
                    for col, lin in self.tabl.items():
                        sr += "{:<{width}}".format(str(lin[i]), width=wid[col])
                    sr+='\n'
                with open(name, 'w') as fw:
                    fw.write(sr)
            elif name[-3:] == 'csv':
                col = list(self.tabl.keys())
                lin = list(zip(*self.tabl.values()))
                with open(name, mode = "w", newline='') as fw:
                    writer = csv.writer(fw)
                    writer.writerow(col)
                    writer.writerows(lin)
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'wb') as fw:
                    pickle.dump(self.tabl, fw)
            else:
                print("Сохранение невозмонжо(Формат неизвестный)")
                raise SystemExit(0)
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
                                if val!=None:
                                    val = converter(val)
                                    tct[col].append(val)
                elif file[-3:] == 'pkl' or file[-3:] == 'kle':
                    tct={}
                    with open(file, 'rb') as fw:
                        tct = pickle.load(fw)
                else:
                    print("Загрузка невозмонжа(Формат неизвестный)")
                    raise SystemExit(0)  
                if not ct:
                    for k in tct.keys():
                        ct[k] = []
                for k in tct.keys():
                    try:
                        ct[k].extend(tct[k])
                    except:
                        print("Несопоставимые значения таблиц")
                        raise SystemExit(0)
            self.tabl = ct
        else:
            name = name[0]
            if name[-3:]=='csv':
                self.tabl={}
                with open(name, mode='r') as fw:
                    reader = csv.DictReader(fw)
                    for col in reader.fieldnames:
                        self.tabl[col] = []
                    for lin in reader:
                        for col in reader.fieldnames:
                            val = lin[col]
                            if val!=None:
                                val = converter(val)
                                self.tabl[col].append(val)
                for k, vals in self.tabl.items():
                    f = True
                    for v in vals:
                        if type(self.tabl[k][0]) != type(v):
                            f = False
                    if f == False:
                        self.tabl[k] = [str(v) for v in vals]
            elif name[-3:] == 'pkl' or name[-3:] == 'kle':
                with open(name, 'rb') as fw:
                    self.tabl = pickle.load(fw)
            else:
                print("Загрузка невозмонжа(Формат неизвестный)")
                raise SystemExit(0)
        print("Загружено в таблицу tabl")
    def get_rows_by_number(self, start, stop=0, copy_table=False):
        if stop == 0:
            stop = start + 1
        if stop < start:  
            print("Неверно указаны индексы для того, чтобы сохранить таблицу.")
            raise SystemExit(0)   
        ct = {}
        for k in self.tabl.keys():
            ct[k]=[]
        for i in range(start, stop):
            for k, val in self.tabl.items():
                ct[k].append(val[i])
        if copy_table == True:
            print("Копия таблицы сохранена")
            return ct
        else:
            self.tabl = ct
            print("Сохранено в исходную таблицу")
            return self.tabl
    def get_rows_by_index(self, *vals, copy_table=False):
        ct={}
        for k in self.tabl.keys():
            ct[k]=[]
        f = 0
        for v in vals:
            val = list(self.tabl.values())
            for i in range(len(val[0])):
                if val[0][i] == v:
                    for k, elem in self.tabl.items():
                        ct[k].append(elem[i])
                        f = 1
        if f == 0:
            print('Введены неверные значения элементов.')
            raise SystemExit(0)
        if copy_table == True:
            print("Копия таблицы сохранена")
            return ct
        else:
            self.tabl = ct
            print("Сохранено в исходную таблицу")
            return self.tabl
    def get_column_types(self, by_number=True):
        ct = {}
        for k, vals in self.tabl.items():
            if not vals:
                raise ValueError(f"Невозможно определить тип данных: колонка '{k}' пуста.")
            ct[k]=type(vals[0]).__name__
        columns = {}
        if by_number == True:
            keys_index = list(self.tabl.keys())
            for k in self.tabl.keys():
                columns[keys_index.index(k)] = ct[k]
        else:
            for i in self.tabl.keys():
                columns[i] = ct[i]
        return columns
    def set_column_types(self, types_dict, by_number=True):
        if by_number == True:
            ct = {}
            keys_index = list(self.tabl.keys())
            for k, v in types_dict.items():
                ct[keys_index[k]] = v
            types_dict = ct
        for k, v in types_dict.items():
            vals = self.tabl[k]
            match v:
                case 'str':
                    vals = [str(x) for x in vals]
                case 'int':
                    try:
                        vals = [int(x) for x in vals]
                    except:
                        print("Ошибка: невозможно привести элементы таблицы к типу int")
                        raise SystemExit(0)
                case 'float':
                    try:
                        vals = [float(x) for x in vals]
                    except:
                        print("Ошибка: невозможно привести элементы таблицы к типу float")
                        raise SystemExit(0)
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
                                    print("Ошибка: невозможно привести элементы таблицы к типу bool")
                                    raise SystemExit(0)
                            else:
                                new_vals.append(bool(x))
                        vals = new_vals
                    except:
                        print("Ошибка: невозможно привести элементы таблицы к типу bool")
                        raise SystemExit(0)
            self.tabl[k]=vals
        print("Типы элементов таблицы изменены")
    def get_values(self, column=0):
        if isinstance(column, str):
            if not self.tabl[column]:
                print("Указана пустая строка")
                raise SystemExit(0)
            return self.tabl[column]
        else:
            keys_index = list(self.tabl.keys())
            if  not self.tabl[keys_index[column]]:
                print("Указана пустая строка")
                raise SystemExit(0)
            return self.tabl[keys_index[column]]
    def get_value(self, column=0):
        if isinstance(column, str):
            if not self.tabl[column]:
                print("Указана пустая строка")
                raise SystemExit(0)
            return self.tabl[column][0]
        else:
            keys_index = list(self.tabl.keys())
            if not self.tabl[keys_index[column]]:
                print("Указана пустая строка")
                raise SystemExit(0)
            return self.tabl[keys_index[column]][0]
    def set_values(self, values, column=0):
        if isinstance(column, str):
            identifier = eval(self.get_column_types(by_number=False)[column])
            try:
                self.tabl[column] = [identifier(x) for x in values]
            except:
                print("Невозможно преобразовать данные к исходному типу")
                raise SystemExit(0)
        else:
            identifier = eval(self.get_column_types(by_number=True)[column])
            keys_index = list(self.tabl.keys())
            try:
                self.tabl[keys_index[column]] = [identifier(x) for x in values]
            except:
                print("Невозможно преобразовать данные к исходному типу")
                raise SystemExit(0)
    def set_value(self, value, column=0):
        if isinstance(column, str):
            identifier = eval(self.get_column_types(by_number=False)[column])
            try:
                self.tabl[column] = [identifier(value)]
            except:
                print("Невозможно преобразовать данные к исходному типу")
                raise SystemExit(0)
        else:
            identifier = eval(self.get_column_types(by_number=True)[column])
            keys_index = list(self.tabl.keys())
            try:
                self.tabl[keys_index[column]] = [identifier(value)]
            except:
                print("Невозможно преобразовать данные к исходному типу") 
                raise SystemExit(0)   
    def print_table(self):
        wid = {}
        for nm, val in self.tabl.items():
            maxl = len(str(nm))
            for i in val:
                if len(str(i)) > maxl:
                    maxl = len(str(i))
            wid[nm] = maxl + 2
        sr = "\n"
        for col in self.tabl.keys():
            sr += "{:<{width}}".format(str(col), width=wid[col])
        sr+='\n'
        for i in range(len(list(self.tabl.values())[0])):
            for col, lin in self.tabl.items():
                sr += "{:<{width}}".format(str(lin[i]), width=wid[col])
            sr+='\n'
        print(sr)

example = Table()
example.load_table('TXT.csv', '2TXT.pickle')
example.save_table('table.pickle', 4)
example.load_table('last_table.pickle', '1table.pickle')
example.print_table()