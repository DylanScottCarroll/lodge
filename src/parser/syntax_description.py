import re

from .tokenizer import Tokenizer, Token, TokenType
from .ordered_set import OrderedSet
from .grammar import Grammar, GrammarRule 

class SyntaxDescription:
    """
    Contains the logic for reading a syntax description file and extracting the grammar and tokenizer from it.
    """

    def __init__(self, filename):
        self.filename = filename

        # Grammar Information
        self._rules = []
        self._nonterminals = OrderedSet()
        self._terminals = OrderedSet()
        self._start_symbol = None

        # Tokenizer Information
        self._tokenizer_rules = []  

        self._read_file(filename)

    def get_grammar(self) -> Grammar:
        return Grammar(self._rules, self._nonterminals, self._terminals, self._start_symbol)

    def get_tokenizer(self) -> 'Tokenizer':
        return Tokenizer(self.tokenizer_rules)

    def _read_file(self, filename: str) -> None:
        raw_grammar_rules: list = []
        self.tokenizer_rules: list = []
        
        with open(filename, 'r') as f:
            for i, line in enumerate(f):                
                grammar_match = re.match(r'([a-zA-Z0-9]*) *-> *(.+)', line)
                token_match = re.match(r'([a-zA-Z0-9]*) *= */(.+)/ *', line)
                ignored_match = re.match(r'#.*|', line)  
                
                if grammar_match:
                    head, body = grammar_match.groups()
                    body = body.strip().split()
                    raw_grammar_rules.append((head, body))
                elif token_match:
                    head, body = token_match.groups()
                    self.tokenizer_rules.append((head, body))

                elif not ignored_match:
                    raise ValueError(f"Invalid syntax on line {i}:\n{line}")

        self._parse_grammar_rules(raw_grammar_rules)
                                    

    def _parse_grammar_rules(self, raw_rules) -> None:
        # Find all nonterminals
        nonterminal_identifiers = set(head for head, _ in raw_rules)

        # Add the rules to the grammar
        for head, body in raw_rules:
            tokenized_head = Token(TokenType.nonterminal, head)
            self._nonterminals.add(tokenized_head)

            # Convert the string token body int to a list of Token objects
            # and add any terminals to the set 
            
            def token_type(token: str) -> TokenType:
                if token in nonterminal_identifiers:
                    return TokenType.nonterminal
                else:
                    return TokenType.terminal

            tokenized_body = [
                Token(token_type(token), token)
                for token in body 
            ]
            self._terminals.update([token for token in tokenized_body if token.is_terminal])


            # Add the prepared rule to the grammar
            self._rules.append(GrammarRule(tokenized_head, tokenized_body))


        self._start_symbol = self._rules[0].head