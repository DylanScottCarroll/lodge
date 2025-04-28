import re

from .tokenizer import Tokenizer
from .ordered_set import OrderedSet
from .grammar import Grammar, GrammarRule 
from .parser import Parser
from .symbol import Symbol

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

        # Tokenizer Information
        self._tokenizer_rules = []  

        self._start_symbol: Symbol = self._read_file(filename)

        self.grammar = Grammar(self._rules, self._nonterminals, self._terminals, self._start_symbol)
        self.parser = Parser(self.grammar)
        self.tokenizer =  Tokenizer(self.tokenizer_rules)

    def _read_file(self, filename: str) -> Symbol:
        raw_grammar_rules: list = []
        self.tokenizer_rules: list = []
        
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                line = line.rstrip("\n")
                
                grammar_match = re.fullmatch(r'([a-zA-Z0-9_-]*) *-> *(.+)', line)
                token_match = re.fullmatch(r'([a-zA-Z0-9_-]*|ε) *= *\/(.+)\/ *', line)
                ignored_match = re.fullmatch(r'#.*|\s*', line)  

                if grammar_match:
                    head, body = grammar_match.groups()
                    body = body.strip().split()
                    raw_grammar_rules.append((head, body))
                
                elif token_match:
                    head, body = token_match.groups()
                    head = Symbol(head, True)

                    self._terminals.add(head)
                    self.tokenizer_rules.append((head, body))

                elif not ignored_match:
                    raise ValueError(f"Invalid syntax on line {i}:\n{line}")

        return self._process_grammar_rules(raw_grammar_rules)
                                    

    def _process_grammar_rules(self, raw_rules) -> Symbol:
        # Find all nonterminals
        nonterminal_identifiers = OrderedSet(head for head, _ in raw_rules)

        # Add the processed rules to the grammar
        for head, body in raw_rules:
            head_symbol = Symbol(head, False)
            self._nonterminals.add(head_symbol)

            # Convert the string list body int to a list of Symbol objects
            body_symbols = [
                Symbol(identifier, identifier not in nonterminal_identifiers)
                for identifier in body 
            ]
            # Add any new terminals to the termian set
            self._terminals.update([symbol for symbol in body_symbols if symbol.terminal])

            # Add the prepared rule to the grammar
            self._rules.append(GrammarRule(head_symbol, body_symbols))


        return self._rules[0].head
