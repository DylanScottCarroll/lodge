import re
from .symbol import Symbol

class Token:
    def __init__(self, symbol:Symbol, text:str, span:tuple[int, int]):
        self.symbol:Symbol = symbol
        self.text:str = text
        self.span:tuple[int, int] = span

    def __str__(self):
        return f"[{str(self.symbol)} {repr(self.text)}]"
    
    def __repr__(self):
        return f"Token({str(self)})"


class Tokenizer:
    def __init__(self, rules:list[tuple]) -> None:
        # Build the compound regular expression that describes the tokenizer
        self.rules = []
        for symbol, pattern in rules:
            try:
                symbol_pattern = (symbol, re.compile(pattern) )
            except re.PatternError: 
                print(f'Error: The regular expression for "{symbol}" is malformed: /{pattern}/')
                continue 
            self.rules.append(symbol_pattern)

    def __call__(self, text:str) -> 'TokenStream':
        return TokenStream(self, text)
    
    
    def next_token(self, text:str, position:int) -> tuple[Token|None, int]:
        if position >= len(text):
            return Token(Symbol.eof, "", (position, position)), position
        
        # Find the earliest match
        # Ties between matches are broken by length
        match:re.Match|None = None
        symbol: Symbol|None = None
        for current_symbol, pattern in self.rules:
            new_match:re.Match = pattern.match(text, pos=position)
            if not new_match: continue

            def compare_matches(match, new_match):
                old_start = match.start()
                old_len = len(match.group())
                new_start = new_match.start()
                new_len = len(new_match.group())

                return ( (new_start < old_start) ) or (( new_start == old_start ) and ( new_len > old_len))

            if (match is None) or compare_matches(match, new_match):
                match = new_match
                symbol = current_symbol
        
        if (match is None) or (symbol is None):
            # If no token matches, treat a single character as a tokenp
            print("Syntax Error! No token match")
            breakpoint()
        
        start, end = match.span() #type: ignore

        # Return a new token
        if symbol == Symbol.epsilon:
            return None, end
        elif symbol == Symbol("*", True):
            symbol = Symbol(text[start:end], True)
            return Token(symbol, text[start:end], (start, end)), end
        else:
            return Token(symbol, text[start:end], (start, end)), end
    


class TokenStream:
    def __init__(self, tokenizer:Tokenizer, text:str):
        self.tokenizer = tokenizer  
        self.text:str = text
        self.position:int = 0
        self.next_token:(Token|None) = None

    def _next(self):
        while True:
            val, self.position = self.tokenizer.next_token(self.text, self.position)
            if val is not None:
                return val

    def pop(self):
        if self.next_token is None:
            self.next_token = self._next()

        result = self.next_token
        self.next_token = self._next()
        
        return result

    def peek(self):
        if self.next_token is None:
            self.next_token = self._next()

        return self.next_token
