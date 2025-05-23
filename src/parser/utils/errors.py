
class GrammarError(Exception):
    def __init__(self, message):
        super().__init__( message)

class ParserError(Exception):
    pass

class ParserSyntaxError(ParserError):
    def __init__(self, parser_state):
        super().__init__("Unexpected token. " + str(parser_state))
        self.parser_state = parser_state

class ParserTokenizerError(ParserError):
    def __init__(self, tokenizer, text, position):
        super().__init__(f"Tokenizer couldn't match any token at position {position} of the text.")

        self.tokenizer = tokenizer
        self.text = text
        self.position = position
