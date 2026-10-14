import csv
import pickle

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
                            if val.isdigit():
                                val = int(val)
                            self.tabl[col].append(val)
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
            self.copy_tabl = ct
            print("Сохранено в таблицу copy_tabl")
        else:
            self.tabl = ct
            print("Сохранено в исходную таблицу")
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
            self.copy_tabl = ct
            print("Сохранено в таблицу copy_tabl")
        else:
            self.tabl = ct
            print("Сохранено в исходную таблицу")

example = Table()
example.tabl = {'Namrfrfrrfrrfrfes': ['Tipok', 'Tipok2', 'Tip3', 'Tip4', 'Tip5'], 'Ages': [89, 67, 87, 9, 76]}
example.save_table('Lol1.csv')
example.load_table('Lol.pickle')
print(example.tabl)
example.load_table('Lol1.csv')
print(example.tabl)
example.get_rows_by_number(1, 3, True)
print(example.copy_tabl)
example.get_rows_by_index('Tipok', 'Tip4', copy_table=True)
print(example.copy_tabl)
example.get_rows_by_index('Tip3', 'Tip4', 'Tipok')
print(example.tabl)
