from parser import BasicSyntaxDescription, SyntaxDescription, CFG_Parser
from parser.symbol import Symbol
import readline
import pickle

def main():
    syntax = SyntaxDescription("test.lang")

    #with open("calc.lang") as f:
    #    string = f.read()

    string = input()

    token_stream = syntax.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()

    token_stream = syntax.tokenizer(string)
    tree = syntax.parser(token_stream)
    if "node" in tree.attributes:
        print(tree.attributes["node"])
    else:
        print(tree)



def refresh_cfg_parser():
    syntax = SyntaxDescription("cfg.lang")
    
    cfg_parser = CFG_Parser(syntax.parser.table.goto_table, syntax.parser.table.action_table)
   
    with open("cfg.lang") as f:
        string = f.read()

    token_stream = syntax.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()


    token_stream = syntax.tokenizer(string)
    tree = syntax.parser(token_stream)
    print(tree)

    with open("./parser/cfg_parser.pkl", "wb") as f:
        pickle.dump((syntax.tokenizer, cfg_parser), f)

if __name__ == "__main__":
    main()
    #refresh_cfg_parser()


