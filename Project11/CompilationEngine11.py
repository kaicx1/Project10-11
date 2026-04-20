from SymbolTable11 import SymbolTable, STATIC, FIELD, ARG, VAR
from VMWriter11    import VMWriter

OPS = {'+': 'add', '-': 'sub', '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}

class CompilationEngine:
    def __init__(self, tokenizer, className):
        self.tok        = tokenizer
        self.symbols    = SymbolTable()
        self.writer     = VMWriter()
        self.curClass   = className
        self.curFunc    = ""
        self.labelCount = 0

    def val(self):
        return self.tok.val()

    def type(self):
        return self.tok.type()
    # looks at next token 
    def peek(self):
        return self.tok.peek()
    #consumes next token
    def eat(self, expected=None):
        return self.tok.eat(expected) 

    # create new variable names
    def newLabel(self, tag):
        l = self.curClass + '_' + tag + '_' + str(self.labelCount)
        self.labelCount += 1
        return l

    # push and pop variables from stack 
    def pushVar(self, name):
        self.writer.push(self.symbols.kindOf(name), self.symbols.indexOf(name))

    def popVar(self, name): 
        self.writer.pop(self.symbols.kindOf(name), self.symbols.indexOf(name))

    def getOutput(self):
        return self.writer.getOutput()

    #handles static and field 
    def compileClass(self):
        self.eat('class')
        self.eat()
        self.eat('{')
        while self.val() in ('static', 'field'):
            self.compileClassVar() 
        while self.val() in ('constructor', 'function', 'method'):
            self.compileSub()
        self.eat('}')

    #handles constructor function and methods
    def compileClassVar(self):
        raw = self.val()
        if raw == 'static':
            kind = STATIC
        else:
            kind = FIELD 
        self.eat()
        t = self.val()
        self.eat()
        name = self.val()
        self.eat()
        self.symbols.define(name, t, kind)
        while self.val() == ',':
            self.eat(',')
            name = self.val()
            self.eat()
            self.symbols.define(name, t, kind) 
        self.eat(';')

    # handles one sub routine
    def compileSub(self):
        self.symbols.startSub()
        subKind = self.val()
        self.eat()
        self.eat()                          # return type
        subName = self.val()
        self.eat() 
        self.curFunc = self.curClass + '.' + subName

        if subKind == 'method':
            self.symbols.define('this', self.curClass, ARG)

        self.eat('(')
        self.compileParams()
        self.eat(')')
        self.eat('{')
        while self.val() == 'var':
            self.compileVar()

        nLocals = self.symbols.numVars(VAR)
        self.writer.func(self.curClass + '.' + subName, nLocals)

        if subKind == 'constructor':
            self.writer.push('constant', self.symbols.numVars(FIELD))
            self.writer.call('Memory.alloc', 1)
            self.writer.pop('pointer', 0) 
        elif subKind == 'method':
            self.writer.push('argument', 0)
            self.writer.pop('pointer', 0)

        self.compileStatements()
        self.eat('}')

    #handles parameters 
    def compileParams(self):
        if self.val() != ')':
            t = self.val()
            self.eat()
            name = self.val()
            self.eat() 
            self.symbols.define(name, t, ARG)
            while self.val() == ',':
                self.eat(',')
                t = self.val()
                self.eat()
                name = self.val()
                self.eat()
                self.symbols.define(name, t, ARG)

    #handles local variables
    def compileVar(self):
        self.eat('var')
        t = self.val()
        self.eat() 
        name = self.val()
        self.eat()
        self.symbols.define(name, t, VAR)
        while self.val() == ',':
            self.eat(',')
            name = self.val()
            self.eat()
            self.symbols.define(name, t, VAR) 
        self.eat(';')

    #handles statments / looking for keywords
    def compileStatements(self):
        while self.val() in ('let', 'if', 'while', 'do', 'return'):
            v = self.val()
            if v == 'let':
                self.compileLet()
            elif v == 'if':
                self.compileIf()
            elif v == 'while': 
                self.compileWhile()
            elif v == 'do':
                self.compileDo()
            elif v == 'return':
                self.compileReturn()

    #handles let
    def compileLet(self):
        self.eat('let')
        name = self.val()
        self.eat() 
        isArr = self.val() == '['
        if isArr:
            self.pushVar(name)
            self.eat('[')
            self.compileExp()
            self.eat(']')
            self.writer.arithmetic('add')
        self.eat('=')
        self.compileExp() 
        self.eat(';')
        if isArr:
            self.writer.pop('temp', 0)
            self.writer.pop('pointer', 1)
            self.writer.push('temp', 0)
            self.writer.pop('that', 0)
        else:
            self.popVar(name) 

    #handles if
    def compileIf(self):
        fl = self.newLabel('IF_FALSE')
        el = self.newLabel('IF_END')
        self.eat('if')
        self.eat('(')
        self.compileExp()
        self.eat(')')
        self.writer.arithmetic('not') 
        self.writer.ifGoto(fl)
        self.eat('{')
        self.compileStatements()
        self.eat('}')
        self.writer.goto(el)
        self.writer.label(fl)
        if self.val() == 'else':
            self.eat('else')
            self.eat('{') 
            self.compileStatements()
            self.eat('}')
        self.writer.label(el)

    #handle while
    def compileWhile(self):
        tl = self.newLabel('WHILE_TOP')
        xl = self.newLabel('WHILE_EXIT')
        self.writer.label(tl)
        self.eat('while')
        self.eat('(')
        self.compileExp() 
        self.eat(')')
        self.writer.arithmetic('not')
        self.writer.ifGoto(xl)
        self.eat('{')
        self.compileStatements()
        self.eat('}')
        self.writer.goto(tl)
        self.writer.label(xl)
    #handle do 
    def compileDo(self):
        self.eat('do')
        self.compileCall()
        self.eat(';')
        self.writer.pop('temp', 0)

    #handle return
    def compileReturn(self):
        self.eat('return')
        if self.val() != ';':
            self.compileExp()
        else:
            self.writer.push('constant', 0)
        self.eat(';')
        self.writer.ret()

    #handles expression 
    def compileExp(self):
        self.compileTerm()
        while self.val() in OPS or self.val() in ('*', '/'):
            op = self.val()
            self.eat()
            self.compileTerm()
            if op == '*':  
                self.writer.call('Math.multiply', 2)
            elif op == '/':
                self.writer.call('Math.divide', 2)
            else:
                self.writer.arithmetic(OPS[op])
                
    #handles term types 
    def compileTerm(self): 
        t = self.type()
        v = self.val()

        if t == 'integerConstant':
            self.writer.push('constant', int(v))
            self.eat()

        elif t == 'stringConstant': 
            self.writer.push('constant', len(v))
            self.writer.call('String.new', 1)
            for ch in v:
                self.writer.push('constant', ord(ch))
                self.writer.call('String.appendChar', 2)
            self.eat()

        elif t == 'keyword':
            if v == 'true': 
                self.writer.push('constant', 0)
                self.writer.arithmetic('not')
            elif v in ('false', 'null'):
                self.writer.push('constant', 0)
            elif v == 'this':
                self.writer.push('pointer', 0)
            self.eat() 

        elif v == '(':
            self.eat('(')
            self.compileExp()
            self.eat(')')

        elif v in ('-', '~'):
            op = v
            self.eat()
            self.compileTerm()
            if op == '-':
                self.writer.arithmetic('neg') 
            else:
                self.writer.arithmetic('not')

        elif t == 'identifier':
            pk = self.peek()
            if pk == '[':
                self.pushVar(v)
                self.eat()
                self.eat('[') 
                self.compileExp()
                self.eat(']')
                self.writer.arithmetic('add')
                self.writer.pop('pointer', 1) 
                self.writer.push('that', 0)
            elif pk in ('.', '('):
                self.compileCall()
            else:
                self.pushVar(v)
                self.eat()


    #handles subroutine calls
    def compileCall(self):
        name = self.val()
        self.eat()
        nArgs = 0 
        if self.val() == '.':
            self.eat('.')
            method = self.val()
            self.eat()
            if self.symbols.inTabel(name):
                self.pushVar(name)
                callee = self.symbols.typeOf(name) + '.' + method
                nArgs  = 1
            else:
                callee = name + '.' + method
        else:
            self.writer.push('pointer', 0)
            callee = self.curClass + '.' + name
            nArgs  = 1
        self.eat('(')
        nArgs += self.compileArgs()
        self.eat(')')
        self.writer.call(callee, nArgs)

    #handles expressions
    def compileArgs(self):
        count = 0
        if self.val() != ')':
            self.compileExp()
            count = 1
            while self.val() == ',':
                self.eat(',')
                self.compileExp() 
                count += 1
        return count 
