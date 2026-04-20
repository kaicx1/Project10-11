import sys
import os

from JackTokenizer11    import JackTokenizer
from CompilationEngine11 import CompilationEngine


def compileFile(path):
    stem   = os.path.splitext(os.path.basename(path))[0]
    outDir = os.path.dirname(path)

    srcFile = open(path).read()

    tokenizer = JackTokenizer(srcFile)
    engine    = CompilationEngine(tokenizer, stem)
    engine.compileClass()

    outPath = os.path.join(outDir, stem + '.vm')
    open(outPath, 'w').write(engine.getOutput())


if __name__ == "__main__":
    path = sys.argv[1]
    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.endswith('.jack'))
        for f in files:
            compileFile(os.path.join(path, f))
    else:
        compileFile(path)
