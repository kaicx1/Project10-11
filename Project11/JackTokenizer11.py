#part 1 
#from project 10
KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static','var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null','this', 'let', 'do', 'if', 'else', 'while', 'return'}
SYMBOLS = set('(){}[]<>.,;+-*/&|=~')

class JackTokenizer:
    def __init__(self, srcFile):
        self.toks = []
        self.pos  = 0
        self.cur  = None

        cleanedFile = self.stripComments(srcFile)
        self.tokenize(cleanedFile)
        self.advance()

    # remove comments
    def stripComments(self, srcFile):
        out = []
        i = 0
        while i < len(srcFile):
            #remove // comments 
            if srcFile[i:i+2] == '//':
                while i < len(srcFile) and srcFile[i] != '\n':
                    i += 1
            # remove /* */ comments
            elif srcFile[i:i+2] == '/*':
                while i < len(srcFile) and srcFile[i:i+2] != '*/':
                    i += 1
                i += 2
            else:
                out.append(srcFile[i])
                i += 1
        return ''.join(out)

    # tokenize a file
    def tokenize(self, srcFile):
        i = 0
        n = len(srcFile)
        while i < n:
            #skip white space
            if srcFile[i].isspace():
                i += 1
                continue
            #strings
            if srcFile[i] == '"':
                j = srcFile.index('"', i + 1)
                self.toks.append(('stringConstant', srcFile[i+1:j]))
                i = j + 1
                continue
            #strings
            if srcFile[i] in SYMBOLS:
                self.toks.append(('symbol', srcFile[i]))
                i += 1
                continue
            #integer constants
            if srcFile[i].isdigit():
                j = i
                while j < n and srcFile[j].isdigit():
                    j += 1
                self.toks.append(('integerConstant', srcFile[i:j]))
                i = j
                continue
            #keywords + identifiers 
            if srcFile[i].isalpha() or srcFile[i] == '_':
                j = i
                while j < n and (srcFile[j].isalnum() or srcFile[j] == '_'):
                    j += 1
                w = srcFile[i:j]
                if w in KEYWORDS:
                    self.toks.append(('keyword', w))
                else:
                    self.toks.append(('identifier', w))
                i = j
                continue
            i += 1

    #move to next token
    def advance(self):
        if self.pos < len(self.toks):
            self.cur = self.toks[self.pos]
            self.pos += 1

    #return current token value
    def val(self):
        return self.cur[1]

    #return current token type
    def type(self):
        return self.cur[0]

    #look into next token
    def peek(self):
        if self.pos < len(self.toks):
            return self.toks[self.pos][1]
        return None
    
    # consume next token
    def eat(self, expected=None):
        v = self.val()
        self.advance()
        return v

    # project 10 only for xml files
    def toXML(self):
        out = ['<tokens>']
        for t, v in self.toks:
            if v == '<':
                v = '&lt;'
            elif v == '>':
                v = '&gt;'
            elif v == '"':
                v = '&quot;'
            elif v == '&':
                v = '&amp;'
            out.append('<' + t + '> ' + v + ' </' + t + '>')
        out.append('</tokens>')
        return '\n'.join(out) + '\n'
