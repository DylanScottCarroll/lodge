from parser import SyntaxDescription
from parser.symbol import Symbol
import readline

if __name__ == "__main__":
    syntax = SyntaxDescription("cfg.lang")

    with open("calc.lang") as f:
        string = f.read()

    token_stream = syntax.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()

    token_stream = syntax.tokenizer(string)
    tree = syntax.parser(token_stream)
    tree.print()
