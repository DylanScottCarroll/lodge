import re
import enum

class TokenType(enum.Enum):
    """Describes the type of a token.

    # Text Tokens
    
    abstract_token:
        An input stram token that can have any number of concrete values. This would be used for token
        types like identifiers, numbers, and literals.
    
    raw_token:
        A token whose exact value is important for parsing and interpretation. This would be usd for
        token types like keywords, operators, and punctuation.
    
    # Grammar Tokens
    
    nonterminal:
        Used in grammar descriptions to represent a nonterminal symbol.
    
    terminal:
        Used in grammar descriptions to represent a terminal symbol. The identifiers for these
        symbols correspond to the identifiers of input stream tokens.
    
    eof:
        A special token used to represent the end of the input stream. This is only used as an intermedaite
        in the parsing process and is not outward-facing.
    
    epsilon:
        A special token used to represent an empty string. This is only used as an intermediate in the grammar
        logic and is not outward-facing.
        
    """
    
    abstract_token = 0
    raw_token = 1

    nonterminal = 2
    terminal = 3
    eof = 4
    epsilon = 5 


class Token:
    """Describes a tokken for the purpose of grammar description, parse tables, and input streams.
    
    Attributes:
        type: TokenType
            Describes the type of the token and is used to differentate between grammar description tokens, 
            tokens in the input stream, and special intermediate tokens like EOF and epsilon.
        
        identifier: str
            Used as the basis of comparison between tokens when the underlying text is not important. This
            corresponds to the name of the token in the grammar description.
        
        value: str
            This is the underlying text of the token. This is not used for parsing but is neccessary for
            interpreting the parsed program.

        location: tuple[int, int]
            Describes the location of the token in the input stream. This is used for error reporting.
    """

    @classmethod
    def eof(cls) -> 'Token':
        return Token(TokenType.eof)
    
    @classmethod
    def epsilon(cls) -> 'Token':
        return Token(TokenType.epsilon)
    

    def __init__(self, type: TokenType, identifier:str=None, value:str=None, location: tuple[int, int]=None) -> None:
        self.type: TokenType = type
        self.identifier: str = identifier
        self.value: str = value
        self.location: tuple[int, int] = location
        

    @property
    def is_terminal(self) -> bool:
        if self.type == TokenType.terminal or self.type == TokenType.eof or self.type == TokenType.epsilon:
            return True
        elif self.type == TokenType.nonterminal:
            return False
        else:
            raise ValueError("Non-grammar token types do not have terminality.")
    
    @property
    def is_nonterminal(self) -> bool:
        if self.type == TokenType.terminal or self.type == TokenType.eof or self.type == TokenType.epsilon:
            return False
        elif self.type == TokenType.nonterminal:
            return True
        else:
            raise ValueError("Non-grammar token types do not have terminality.")
    

    def __eq__(self, other: 'Token') -> bool:
        return self.type == other.type \
               and self.value == other.value \
               and self.identifier == other.identifier
    
    def __hash__(self) -> int:
        return hash(self.type) ^ hash(self.value) ^ hash(self.identifier)
    
    def __str__(self) -> str:
        # return f"<{self.type} {self.identifier}>"
        
        match self.type:
            case TokenType.abstract_token:
                return f"<{self.identifier} ({self.value})>"
            case TokenType.raw_token:
                return f"{self.identifier}"
            case TokenType.nonterminal:
                return f"<{self.identifier}>"
            case TokenType.terminal:
                return f"'{self.identifier}'"
            case TokenType.eof:
                return "$"
            case TokenType.epsilon:
                return "ε"

    def __repr__(self) -> str:
        return str(self)

class Tokenizer:
    def __init__(self, rules) -> None:
        # Build the compount regular expression that describes the tokenizer

        self._expression = "" # The regular expression that describes the tokenizer, concatenating all the rules
        self._group_num_map: dict[int, (TokenType, str)] = {} # Maps the group number to the token type and identifier
        for i, (head, body) in enumerate(rules):
            # Add the rule to the expression
            self._expression += f"({body})|"

            # Add the rule to the mapping
            self._group_num_map[i] = (TokenType.abstract_token, head)
        
        # Add default rule to the expression
        self._expression += "(.)"
        self._group_num_map[len(rules)] = (TokenType.raw_token, None)

        print(self._expression)
        print(self._group_num_map)
        # exit()

        # Initialize the text
        self.text = None

    def __call__(self, text) -> 'Tokenizer':
        self.text = text
        self.position = 0
    
    def __iter__(self) -> 'Tokenizer':
        return self
    
    def __next__(self) -> Token:
        if self.text is None or self.position >= len(self.text):
            raise StopIteration
        
        match = re.match(self._expression, self.text[self.position:])
        if not match:
            #TODO: Make this logic more sophisticated
            raise ValueError(f"Invalid token at position {self.position} in '{self.text}'")
        
        for i, match in match.groups():
            if match is not None:
                break

        token_type, identifier = self._group_num_map[i]
            
    

        pass

        
