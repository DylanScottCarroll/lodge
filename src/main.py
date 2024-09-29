from parser import Grammar, Parser
if __name__ == "__main__":
    grammar = Grammar("grammar.txt")
    parser = Parser(grammar)

    print(parser.table)

    while True:
        string = input("Enter string to parse: ")
        string = string.replace(" ", "")
        print(parser(string))