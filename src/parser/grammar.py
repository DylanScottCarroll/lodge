from .ordered_set import OrderedSet
from .symbol import Symbol

from typing import Callable

class ActionRoutine:
    def __init__(self, dest:str, val_type:str, val_args:tuple):
        self.dest:str = dest
        
        self.val_type = val_type
        if val_type not in ["Node", "List", "Val"]:
            raise ValueError(f"The val_type of an ActionRoutine must be 'Node', 'List', or 'Val'. Not '{val_type}'.")

        self.val_args = val_args


class GrammarRule:
    """
    Represents a production rule in a grammar.

    Attributes:
        head (str): The nonterminal symbol on the left-hand side of the rule.
        body (list): A list of symbols on the right-hand side of the rule.
    """
    
    def __init__(self, head: Symbol, body: list[Symbol], action_routines:list[ActionRoutine]|None=None) -> None:
        self.head = head
        self.body = body

        self.action_routines = action_routines or []

    def __str__(self) -> str:
        return f"{str(self.head)} -> {' '.join(map(str, self.body))}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        return self.head == other.head and self.body == other.body
    
    def __hash__(self) -> int:
        return hash(self.head) ^ hash(self.body)

class Grammar:
    """
    Represents a grammar object.

    Attributes:
        rules (list): A list of GrammarRule objects representing the production rules of the grammar.
        start_symbol (str): The start symbol of the grammar.
        
        rule_head_map (dict): A dictionary mapping nonterminals to the indices of rules where they are the head.
        rule_body_map (dict): A dictionary mapping symbols to the indices of rules where they appear in the body.
        
        nonterminals (OrderedSet): An ordered set of nonterminal symbols in the grammar.
        terminals (OrderedSet): An ordered set of terminal symbols in the grammar.
        
        first_sets (dict): A dictionary mapping symbols to their first sets.
        follow_sets (dict): A dictionary mapping symbols to their follow sets.

    Methods:
        get_rules_by_head(nonterminal: str) -> list[GrammarRule]:
            * Returns a list of rules with the given nonterminal as the head.
        get_rules_by_body_symbol(symbol: Symbol) -> list[GrammarRule]:
            * Returns a list of rules containing the given symbol in the body.
    """

    def __init__(self, rules: list[GrammarRule], nonterminals: OrderedSet, terminals: OrderedSet, start_symbol: Symbol) -> None:
        self.rules:list[GrammarRule] = []
        self.start_symbol:Symbol = start_symbol

        self.rule_head_map: dict[Symbol, list[int]] = {}
        self.rule_body_map: dict[Symbol, list[int]] = {}

        self.nonterminals = nonterminals
        self.terminals = terminals

        self.first_sets = {}
        self.follow_sets = {}

        for rule in rules:
            self._add_rule(rule)

        self._check_rules()
        
        self._populate_first_and_follow_sets()        

    def get_rules_by_head(self, nonterminal: Symbol) -> list[GrammarRule]:
        return list(map(lambda i: self.rules[i], self.rule_head_map[nonterminal]))
    
    def get_rules_by_body_symbol(self, symbol: Symbol) -> list[GrammarRule]:
        return list(map(lambda i: self.rules[i], self.rule_body_map[symbol]))


    def _add_rule(self, rule: GrammarRule) -> None:
        i = len(self.rules)
        self.rules.append(rule)

        if rule.head in self.rule_head_map.keys():
            self.rule_head_map[rule.head].append(i)
        else:
            self.rule_head_map[rule.head] = [i]

        for body_symbol in rule.body:
            if body_symbol in self.rule_body_map.keys():
                if i not in self.rule_body_map[body_symbol]: 
                    self.rule_body_map[body_symbol].append(i)
            else:
                self.rule_body_map[body_symbol] = [i]
    
    def _check_rules(self):
        """Perform a series of validations for the grammar rules"""

        for i, head in enumerate(self.rule_head_map.keys()):
            if head not in self.rule_body_map.keys() and i!=0:
                print(f"WARNING: Symbol '{head}' appears in no rule body, so is not accessible")
                self.rule_body_map[head] = []

    def _populate_first_and_follow_sets(self) -> None:
        def in_order_traverse(symbol: Symbol, visited: OrderedSet) -> None:
            if symbol in self.terminals:
                return
            
            for rule in self.get_rules_by_head(symbol):
                for rule_body_symbol in rule.body:
                    if rule_body_symbol not in visited:
                        in_order_traverse(rule_body_symbol, visited|{rule_body_symbol})

            self.first_sets[symbol] = self._find_first_set(symbol)
            self.follow_sets[symbol] = self._find_follow_set(symbol)

        in_order_traverse(self.start_symbol, OrderedSet({self.start_symbol}))
        
        for nonterminal in self.nonterminals:
            if (nonterminal not in self.first_sets):
                self.first_sets[nonterminal] = []
            if (nonterminal not in self.follow_sets):
                self.follow_sets[nonterminal] = []


    def _find_first_set(self, symbol: Symbol, explored_symbols: OrderedSet|None = None) -> OrderedSet:
        if explored_symbols is None: 
            explored_symbols = OrderedSet()
          
        if symbol.terminal:
            return OrderedSet([symbol])
        
        if symbol in self.first_sets:
            return self.first_sets[symbol]
        
        first_set = OrderedSet()
        for rule in self.get_rules_by_head(symbol):
            current_rule_set = self._find_first_from_nonterminal_list(rule.body, explored_symbols)
            first_set.update(current_rule_set)

        return first_set

    def _find_follow_set(self, symbol: Symbol, explored_symbols: OrderedSet|None = None) -> OrderedSet:
        if explored_symbols is None:
            explored_symbols = OrderedSet()
        
        if symbol == self.start_symbol:
            self.follow_sets[symbol] = OrderedSet({Symbol.eof})
            return self.follow_sets[symbol]
        
        if symbol in self.follow_sets:
            return self.follow_sets[symbol]
        
        follow_set = OrderedSet()
        for rule in self.get_rules_by_body_symbol(symbol):
            if symbol not in rule.body: continue

            symbol_index = rule.body.index(symbol)    
            first_in_rest = self._find_first_from_nonterminal_list(rule.body[symbol_index+1:], OrderedSet())
            follow_set.update(first_in_rest-{Symbol.epsilon})

            if Symbol.epsilon in first_in_rest:
                if rule.head not in explored_symbols:
                    head_follow_set = self._find_follow_set(rule.head, explored_symbols|{rule.head})
                    follow_set.update(head_follow_set)

        return follow_set

    def _find_first_from_nonterminal_list(self, symbol_list: list[Symbol], explored_symbols: OrderedSet|None = None) -> OrderedSet:
        if explored_symbols is None:
            explored_symbols = OrderedSet()
        
        if len(symbol_list) == 0:
            return OrderedSet({Symbol.epsilon})
        
        first_set = OrderedSet()
        current_rule_set = OrderedSet()
        i=0 
        for i, body_symbol in enumerate(symbol_list):
            if body_symbol in explored_symbols: break

            current_rule_set = self._find_first_set(body_symbol, explored_symbols|{body_symbol})
            first_set.update(current_rule_set-{ Symbol.epsilon })

            if Symbol.epsilon not in current_rule_set: break

        if i == len(symbol_list)-1 and Symbol.epsilon in current_rule_set:
            first_set.add(Symbol.epsilon)

        return first_set
