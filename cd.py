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

example = Table()
example.tabl = {'Namrfrfrrfrrfrfes': ['Tipok', 'Tipok2'], 'Ages': [89, 67]}
example.load_table('Lol.csv')
print(example.tabl)
