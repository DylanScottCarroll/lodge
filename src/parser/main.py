import sys
import pickle
import readline

from .parser import Parser
from .symbol import Symbol

def test():
    parser = Parser("./parser/resources/calc.lang")

    # with open("./parser/resources/cfg.lang") as f:
    #     string = f.read()

    string = input()

    token_stream = parser.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()

    tree = parser.parse(string)
    if "node" in tree.attributes:
        print(tree.attributes["node"])
    else:
        print(tree)


def refresh_cfg_parser():
    parser = Parser("./parser/resources/cfg.lang")
    
    print(f"{'='*100}\n{' Testing on Test Language ':=^100}\n{'='*100}")
    with open("./parser/resources/calc.lang") as f:
        string = f.read()
    
    print("Token Stream:")
    token_stream = parser.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()


    tree = parser.parse(string)
    print("Parse Tree:")
    print(tree)

    print(f"{' Testing on Self ':=^100}")
    
    with open("./parser/resources/cfg.lang") as f:
        string = f.read()
    
    print("Token Stream:")
    token_stream = parser.tokenizer(string)
    while (t := token_stream.pop()).symbol != Symbol.eof:
        print(t, end=" ")
    print()


    tree = parser.parse(string)
    print("Parse Tree:")
    print(tree)


    print("Saving parse tables...")
    with open("./parser/resources/cfg_parser.pkl", "wb") as f:
        pickle.dump((parser.grammar, parser.tokenizer), f)

    print("Done!")

if __name__ == "__main__":
    def usage():
        print("Usage: main.py test|refresh")
        exit()

    if len(sys.argv) != 2:
        usage()
    elif sys.argv[1] == "refresh":
        refresh_cfg_parser()
    elif sys.argv[1] == "test":
        test()
    else:
        usage()


