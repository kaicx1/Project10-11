STATIC = 'static'
FIELD  = 'this'
ARG    = 'argument'
VAR    = 'local'


class SymbolTable:
    def __init__(self):
        self.classTable = {}
        self.subTabel = {}
        self.counts = {STATIC: 0, FIELD: 0, ARG: 0, VAR: 0}

    # reset class 
    def startClass(self):
        self.classTable.clear()
        self.counts[STATIC] = 0
        self.counts[FIELD]  = 0

    # reset subroutine
    def startSub(self):
        self.classTable.clear()
        self.counts[ARG] = 0
        self.counts[VAR] = 0

    # add variable to a table
    def define(self, name, type, kind):
        if kind in (STATIC, FIELD):
            Tabel = self.classTable
        else:
            Tabel = self.subTabel
        Tabel[name] = (type, kind, self.counts[kind])
        self.counts[kind] += 1

    # look up subroutine table first, then class table
    def lookup(self, name):
        if name in self.subTabel:
            return self.subTabel[name]
        if name in self.classTable:
            return self.classTable[name]
        return None

    #return (static, this, argument, local)
    def kindOf(self, name):
        r = self.lookup(name)
        if r:
            return r[1]
        return None

    #return (int, char, boolean, or class name)
    def typeOf(self, name):
        r = self.lookup(name)
        if r:
            return r[0]
        return None

    #return index
    def indexOf(self, name):
        r = self.lookup(name)
        if r:
            return r[2]
        return None

    def inTabel(self, name):
        return self.lookup(name) is not None

    def numVars(self, kind):
        return self.counts[kind]