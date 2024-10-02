import re

from .tokenizer import Tokenizer
from .ordered_set import OrderedSet
from .grammar import Grammar, GrammarRule 

class SyntaxDescription:
    """
    Contains the logic for reading a syntax description file and extracting the grammar and tokenizer from it.
    """

    def __init__(self, filename):
        self.filename = filename

        self._rules = []
        self._nonterminals = OrderedSet()
        self._terminals = OrderedSet()
        self._start_symbol = None

        self._read_file(filename)

    def get_grammar(self) -> Grammar:
        return Grammar(self._rules, self._nonterminals, self._terminals, self._start_symbol)

    def get_tokenizer(self) -> 'Tokenizer':
        return Tokenizer()

    def _read_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            for line in f:                
                if "->" not in line:
                    continue
                
                head, body = re.split(r'\s+->\s+', line)
                body = re.split(r'\s+', body.strip())

                self._nonterminals.add(head)
                self._terminals.update(body)

                self._rules.append(GrammarRule(head, body))

        self._terminals -= self._nonterminals

        self._start_symbol = self._rules[0].head