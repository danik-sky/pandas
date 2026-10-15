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
    def save_table(self, name):
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
            for i in range(len(self.tabl.values())):
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
        else:
            with open(name, 'wb') as fw:
                pickle.dump(self.tabl, fw)
        print(f"Сохранено в файл {name}")
    def load_table(self,name):
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
        else:
            with open(name, 'rb') as fw:
                self.tabl = pickle.load(fw)
        print("Загружено в таблицу tabl")
    def get_rows_by_number(self, start, stop=0, copy_table=False):
        if stop == 0:
            stop = start + 1
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
        for v in vals:
            val = list(self.tabl.values())
            for i in range(len(val[0])):
                if val[0][i] == v:
                    for k, elem in self.tabl.items():
                        ct[k].append(elem[i])
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
                case 'float':
                    try:
                        vals = [float(x) for x in vals]
                    except:
                        print("Ошибка: невозможно привести элементы таблицы к типу float")
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
                                    raise ValueError("Ошибка: невозможно привести элементы таблицы к типу float")
                            else:
                                new_vals.append(bool(x))
                        vals = new_vals
                    except:
                        print("Ошибка: невозможно привести элементы таблицы к типу bool")
            self.tabl[k]=vals
        print("Типы элементов таблицы изменены")
    def get_values(self, column=0):
        if isinstance(column, str):
            return self.tabl[column]
        else:
            keys_index = list(self.tabl.keys())
            return self.tabl[keys_index[column]]
    def get_value(self, column=0):
        if isinstance(column, str):
            return self.tabl[column][0]
        else:
            keys_index = list(self.tabl.keys())
            return self.tabl[keys_index[column]][0]

example = Table()
example.tabl = {'Namrfrfrrfrrfrfes': [False], 'Ages': ['89']}
columns = example.get_column_types(by_number=True)
gval = example.get_value()
print(columns, gval)