from parser import BasicSyntaxDescription, SyntaxDescription, CFG_Parser
from parser.symbol import Symbol
import readline
import pickle

def main():
    syntax = SyntaxDescription("calc.lang")

    string = input()

    token_stream = syntax.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()

    token_stream = syntax.tokenizer(string)
    tree = syntax.parser(token_stream)
    tree.print()
    print(tree.attributes)


if __name__ == "__main__":
    main()
    exit()

    syntax = BasicSyntaxDescription("cfg.lang")
    
    cfg_parser = CFG_Parser(syntax.parser.table.goto_table, syntax.parser.table.action_table)
   
    with open("calc.lang") as f:
        string = f.read()

    token_stream = syntax.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()


    token_stream = syntax.tokenizer(string)
    tree = syntax.parser(token_stream)
    tree.print()

    with open("./parser/cfg_parser.pkl", "wb") as f:
        pickle.dump((syntax.tokenizer, cfg_parser), f)

