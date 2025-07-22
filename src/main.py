from parser import Parser 
import readline

def main():
    parser = Parser("./lodge.lang")
    
    with open("test.lodge", "r") as f:
        string = f.read()
    
    
    tree = parser.parse(string)
    breakpoint()

if __name__ == "__main__":
    main()
