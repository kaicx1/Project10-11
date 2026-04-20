
class VMWriter:
    def __init__(self):
        self.vm = []
 
    def push(self, seg, i):
        self.vm.append('push ' + seg + ' ' + str(i))
 
    def pop(self, seg, i):
        self.vm.append('pop ' + seg + ' ' + str(i))
 
    def arithmetic(self, cmd):
        self.vm.append(cmd)
 
    def label(self, l):
        self.vm.append('label ' + l)
 
    def goto(self, l):
        self.vm.append('goto ' + l)
 
    def ifGoto(self, l):
        self.vm.append('if-goto ' + l)
 
    def call(self, n, a):
        self.vm.append('call ' + n + ' ' + str(a))
 
    def func(self, n, v):
        self.vm.append('function ' + n + ' ' + str(v))
 
    def ret(self):
        self.vm.append('return')

    def getOutput(self):
        return '\n'.join(self.vm) + '\n'
