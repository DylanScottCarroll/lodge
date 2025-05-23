from .symbol import Symbol
from .tokenizer import Token


class ParseNode:
    def __init__(self, symbol:Symbol, parent:'ParseNode|None'=None, children:list|None=None, token:Token|None = None):
        self.symbol:Symbol = symbol
        self.parent:ParseNode|None= parent
        self.attributes = {}
        
        if not((children is None) ^ (token is None)):
            raise ValueError("ParseNode must recieve ParseNode children or Token child and not both.")

        self.children: list[ParseNode] = children or []
        self.token: Token|None = token
        self.spanned_tokens = []
        
        if token is None:
            for child in self.children:
                child.parent = self
                self.spanned_tokens.extend(child.spanned_tokens)
        else:
            self.attributes["token"] = token.text

    def _get(self, symbol:Symbol|str|None=None, index:int=0):
        if symbol is None:
            return self.children[index]
        else:
            for child in self.children:
                if child.symbol == symbol or child.symbol.identifier == symbol:
                    if index == 0:
                        return child
                    else:
                        index -= 1

            raise KeyError(f"Index {index} out of bounds for symbol {repr(symbol)}.")

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get(None, key)
        elif isinstance(key, Symbol) or isinstance(key, str):
            return self._get(symbol=key)
        elif isinstance(key, tuple) and len(key) == 2:
            symbol, index = key
            if isinstance(symbol, Symbol) or isinstance(symbol, str):
                return self._get(symbol=symbol, index=index)
            else:
                raise KeyError(f"Unexpected symbol type: '{symbol}'")

        else:
            raise KeyError(f"Unexpected key for ParseNode: '{key}'")
    
    def __contains__(self, key):
        try:
            if isinstance(key, tuple):
                self[*key]
            else:
                self[key]

            return True
        except KeyError:
            return False



    def format_tree(self, level:int=0):
        if len(self.children) > 0:
            string = f"{'    '*level}{str(self.symbol)}"  
            for child in self.children:
                string += "\n" + child.format_tree(level+1)
        elif self.token is not None:
            string =  f"{'    '*level}{str(self.symbol)} : {repr(self.token.text)}"
        else:
            string =  f"{'    '*level}{str(self.symbol)} : ε"

        return string

    def __str__(self):
        return self.format_tree()
    
    def __repr__(self):
        return f"<ParseNode {str(self.symbol)}>"


class SyntaxNode:
    def __init__(self, value:str, attributes:dict):
        self.value = value
        self.attributes = attributes

    def format_tree(self, level:int=0, prefix="") -> str:
        string = f"{'    '*level}{prefix}{':' if prefix else ''} {self.value}"
        for key, child in self.attributes.items():
            if isinstance(child, SyntaxNode):
                string += "\n" + child.format_tree(level=(level+1), prefix=key)
            else:
                string += f"\n{key}: {child}"
        return string

    def __str__(self):
        return self.format_tree()

    def __repr__(self):
        return f"SyntaxNode({self.value}: {list(self.attributes.values())})"

