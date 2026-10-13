class Table:
    def save_table(self, name):
        sr = ""
        for col in self.tabl.keys():
            sr+=str(col)+'\t'
        sr+='\n'
        for i in range(len(self.tabl.values())):
            for lin in self.tabl.values():
                sr+=str(lin[i])+'\t'
            sr+='\n'
        with open(name, 'w') as fw:
            fw.write(sr)
            
example = Table()
example.tabl = {'Names': ['Tipok', 'Tipok2'], 'Ages': [89, 67]}
example.save_table('Lol.txt')
