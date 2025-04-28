from parser import SyntaxDescription
from parser.symbol import Symbol

if __name__ == "__main__":
    syntax = SyntaxDescription("cfg.lang")

    print(syntax.tokenizer.rules)

    while True:
        string = input("Enter string to parse: ")
        # for token in syntax.tokenizer(string):
        #     print(token)
        token_stream = syntax.tokenizer(string)
        while True:
            print(tok:=token_stream.pop(), end = " ")
            if tok.symbol == Symbol.eof: break
        print("\n")

        tree = syntax.parser(syntax.tokenizer(string))
        tree.print()
