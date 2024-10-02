from parser import Parser
from parser import SyntaxDescription


if __name__ == "__main__":
    language_file = SyntaxDescription("grammar.txt")
    
    grammar = language_file.get_grammar()
    parser = Parser(grammar)

    print(parser.table)

    while True:
        string = input("Enter string to parse: ")
        string = string.replace(" ", "")
        print(parser(string))