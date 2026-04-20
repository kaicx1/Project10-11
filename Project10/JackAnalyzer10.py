import sys
import os

from JackTokenizer10     import JackTokenizer
from CompilationEngine10 import CompilationEngine


def analyzeFile(path):
    stem   = os.path.splitext(os.path.basename(path))[0]
    outDir = os.path.dirname(path)
    srcFile = open(path).read()

    tokenizer = JackTokenizer(srcFile)

    open(os.path.join(outDir, 'my' + stem + 'T.xml'), 'w').write(tokenizer.toXML())

    engine = CompilationEngine(tokenizer)
    engine.compileClass()
    open(os.path.join(outDir,'my'+ stem + '.xml'), 'w').write(engine.getOutput())


if __name__ == "__main__":
    path = sys.argv[1]
    if os.path.isdir(path):
        files = sorted(f for f in os.listdir(path) if f.endswith('.jack'))
        for f in files:
            analyzeFile(os.path.join(path, f))
    else:
        analyzeFile(path)
