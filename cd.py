class Table:
    def save_table(self, name):
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
            
example = Table()
example.tabl = {'Namrfrfrrfrrfrfes': ['Tipok', 'Tipok2'], 'Ages': [89, 67]}
example.save_table('Lol.txt')
