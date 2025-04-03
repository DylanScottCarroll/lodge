from parser import Parser
from parser import SyntaxDescription

<<<<<<< HEAD
if __name__ == "__main__":
    language_file = SyntaxDescription("test.lang")
    
    tokenizer = language_file.get_tokenizer()
=======

if __name__ == "__main__":
    language_file = SyntaxDescription("grammar.txt")
    
>>>>>>> 6c70fe12ac072ea9fce296c53afe9f989e230e30
    grammar = language_file.get_grammar()
    parser = Parser(grammar)

    print(parser.table)

    while True:
        string = input("Enter string to parse: ")
        string = string.replace(" ", "")
        print(parser(string))
