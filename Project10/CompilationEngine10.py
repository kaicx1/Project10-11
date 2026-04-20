class CompilationEngine:
    def __init__(self, tokenizer):
        self.tok    = tokenizer
        self.out    = []
        self.indent = 0

    def val(self):
        return self.tok.val()

    def type(self):
        return self.tok.type()

    def peek(self):
        return self.tok.peek()

    # write current token as XML terminal then advance
    def eat(self, expected=None):
        t = self.type()
        v = self.val()
        if v == '<':
            v = '&lt;'
        elif v == '>':
            v = '&gt;'
        elif v == '"':
            v = '&quot;'
        elif v == '&':
            v = '&amp;'
        self.write('<' + t + '> ' + v + ' </' + t + '>')
        self.tok.eat(expected)
        return v

    def write(self, line):
        self.out.append('  ' * self.indent + line)

    def open(self, tag):
        self.write('<' + tag + '>')
        self.indent += 1

    def close(self, tag):
        self.indent -= 1
        self.write('</' + tag + '>')

    def getOutput(self):
        return '\n'.join(self.out) + '\n'

    #

    #handles static and field 
    def compileClass(self):
        self.open('class')
        self.eat('class')
        self.eat()
        self.eat('{')
        while self.val() in ('static', 'field'):
            self.compileClassVar()
        while self.val() in ('constructor', 'function', 'method'):
            self.compileSub()
        self.eat('}')
        self.close('class')

    #handles constructor function and methods
    def compileClassVar(self):
        self.open('classVarDec')
        self.eat()
        self.eat()
        self.eat()
        while self.val() == ',':
            self.eat(',')
            self.eat()
        self.eat(';')
        self.close('classVarDec')

    # handles one sub routine
    def compileSub(self):
        self.open('subroutineDec')
        self.eat()
        self.eat()
        self.eat()
        self.eat('(')
        self.compileParams()
        self.eat(')')
        self.compileSubBody()
        self.close('subroutineDec')

    #handles parameters 
    def compileParams(self):
        self.open('parameterList')
        if self.val() != ')':
            self.eat()
            self.eat()
            while self.val() == ',':
                self.eat(',')
                self.eat()
                self.eat()
        self.close('parameterList')

    #handles block of a subroutine
    def compileSubBody(self):
        self.open('subroutineBody')
        self.eat('{')
        while self.val() == 'var':
            self.compileVar()
        self.compileStatements()
        self.eat('}')
        self.close('subroutineBody')

    #handles local variables
    def compileVar(self):
        self.open('varDec')
        self.eat('var')
        self.eat()
        self.eat()
        while self.val() == ',':
            self.eat(',')
            self.eat()
        self.eat(';')
        self.close('varDec')

    #handles statments / looking for keywords
    def compileStatements(self):
        self.open('statements')
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
        self.close('statements')

    #handles let
    def compileLet(self):
        self.open('letStatement')
        self.eat('let')
        self.eat()
        if self.val() == '[':
            self.eat('[')
            self.compileExp()
            self.eat(']')
        self.eat('=')
        self.compileExp()
        self.eat(';')
        self.close('letStatement')

    #handles if
    def compileIf(self):
        self.open('ifStatement')
        self.eat('if')
        self.eat('(')
        self.compileExp()
        self.eat(')')
        self.eat('{')
        self.compileStatements()
        self.eat('}')
        if self.val() == 'else':
            self.eat('else')
            self.eat('{')
            self.compileStatements()
            self.eat('}')
        self.close('ifStatement')

    #handle while
    def compileWhile(self):
        self.open('whileStatement')
        self.eat('while')
        self.eat('(')
        self.compileExp()
        self.eat(')')
        self.eat('{')
        self.compileStatements()
        self.eat('}')
        self.close('whileStatement')

    #handle do 
    def compileDo(self):
        self.open('doStatement')
        self.eat('do')
        self.compileCall()
        self.eat(';')
        self.close('doStatement')

    #handle return
    def compileReturn(self):
        self.open('returnStatement')
        self.eat('return')
        if self.val() != ';':
            self.compileExp()
        self.eat(';')
        self.close('returnStatement')



    OPS = set('+-*/&|<>=')
    #handles expression 
    def compileExp(self):
        self.open('expression')
        self.compileTerm()
        while self.val() in self.OPS:
            self.eat()
            self.compileTerm()
        self.close('expression')

    #
    def compileTerm(self):
        self.open('term')
        t = self.type()
        v = self.val()

        if t in ('integerConstant', 'stringConstant'):
            self.eat()
        elif t == 'keyword':
            self.eat()
        elif v == '(':
            self.eat('(')
            self.compileExp()
            self.eat(')')
        elif v in ('-', '~'):
            self.eat()
            self.compileTerm()
        elif t == 'identifier':
            pk = self.peek()
            if pk == '[':
                self.eat()
                self.eat('[')
                self.compileExp()
                self.eat(']')
            elif pk in ('(', '.'):
                self.compileCall()
            else:
                self.eat()
        self.close('term')

    #handles subroutine calls
    def compileCall(self):
        self.eat()
        if self.val() == '.':
            self.eat('.')
            self.eat()                      
        self.eat('(')
        self.compileArgs()
        self.eat(')')

    #handles expressions
    def compileArgs(self):
        self.open('expressionList')
        if self.val() != ')':
            self.compileExp()
            while self.val() == ',':
                self.eat(',')
                self.compileExp()
        self.close('expressionList')