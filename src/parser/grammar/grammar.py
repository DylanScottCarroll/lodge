import re
from ..ordered_set import OrderedSet

class GrammarRule:
    """
    Represents a production rule in a grammar.

    Attributes:
        head (str): The nonterminal symbol on the left-hand side of the rule.
        body (list): A list of symbols on the right-hand side of the rule.
    """
    
    def __init__(self, head: str, body: list[str]) -> None:
        self.head = head
        self.body = body

    def __str__(self) -> str:
        return f"{self.head} -> {' '.join(self.body)}"

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
        rule_body_map (dict): A dictionary mapping tokens to the indices of rules where they appear in the body.
        
        nonterminals (OrderedSet): An ordered set of nonterminal symbols in the grammar.
        terminals (OrderedSet): An ordered set of terminal symbols in the grammar.
        
        first_sets (dict): A dictionary mapping symbols to their first sets.
        follow_sets (dict): A dictionary mapping symbols to their follow sets.

    Methods:
        get_rules_by_head(nonterminal: str) -> list[GrammarRule]:
            * Returns a list of rules with the given nonterminal as the head.
        get_rules_by_body_token(token: str) -> list[GrammarRule]:
            * Returns a list of rules containing the given token in the body.
    """

    def __init__(self, filename: str) -> None:
        self.rules = []
        self.start_symbol = None

        self.rule_head_map = {}
        self.rule_body_map = {}

        self.nonterminals = OrderedSet()
        self.terminals = OrderedSet(["$"])

        self.first_sets = {}
        self.follow_sets = {}

        self._read_file(filename)
        self._populate_first_and_follow_sets()
        

    def get_rules_by_head(self, nonterminal: str) -> list[GrammarRule]:
        return list(map(lambda i: self.rules[i], self.rule_head_map[nonterminal]))
    
    def get_rules_by_body_token(self, token: str) -> list[GrammarRule]:
        return list(map(lambda i: self.rules[i], self.rule_body_map[token]))

    def _read_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            for line in f:                
                if "->" not in line:
                    continue
                
                head, body = re.split(r'\s+->\s+', line)
                body = re.split(r'\s+', body.strip())

                self.nonterminals.add(head)
                self.terminals.update(body)

                self._add_rule(GrammarRule(head, body))

        self.terminals -= self.nonterminals

        self.start_symbol = self.rules[0].head

    def _add_rule(self, rule: GrammarRule) -> None:
        i = len(self.rules)
        self.rules.append(rule)

        if rule.head in self.rule_head_map.keys():
            self.rule_head_map[rule.head].append(i)
        else:
            self.rule_head_map[rule.head] = [i]

        for body_token in rule.body:
            if body_token in self.rule_body_map.keys():
                if i not in self.rule_body_map[body_token]: 
                    self.rule_body_map[body_token].append(i)
            else:
                self.rule_body_map[body_token] = [i]

    def _populate_first_and_follow_sets(self) -> None:
        def in_order_traverse(token: str, visited: OrderedSet) -> None:
            if token in self.terminals:
                return
            
            for rule in self.get_rules_by_head(token):
                for rule_body_token in rule.body:
                    if rule_body_token not in visited:
                        in_order_traverse(rule_body_token, visited|{rule_body_token})

            self.first_sets[token] = self._find_first_set(token)
            self.follow_sets[token] = self._find_follow_set(token)

        in_order_traverse(self.start_symbol, OrderedSet(self.start_symbol))
        
        for nonterminal in self.nonterminals:
            if nonterminal not in self.first_sets or nonterminal not in self.follow_sets:
                print(f"WARNING: Variable '{nonterminal}' not reachable with the provided grammar.")

    def _find_first_set(self, token: str, explored_tokens: list[str] = None) -> OrderedSet:
        if explored_tokens is None: 
            explored_tokens = []
        
        if token in self.terminals:
            return OrderedSet([token])
        
        if token in self.first_sets:
            return self.first_sets[token]
        
        first_set = OrderedSet()
        for rule in self.get_rules_by_head(token):
            current_rule_set = self._find_first_from_nonterminal_list(rule.body, explored_tokens)
            first_set.update(current_rule_set)

        return first_set

    def _find_follow_set(self, token: str, explored_tokens: set[str] = None) -> OrderedSet:
        if explored_tokens is None:
            explored_tokens = []
        
        if token == self.start_symbol:
            self.follow_sets[token] = OrderedSet({"$"})
            return self.follow_sets[token]
        
        if token in self.follow_sets:
            return self.follow_sets[token]
        
        follow_set = OrderedSet()
        for rule in self.get_rules_by_body_token(token):
            if token not in rule.body: continue

            token_index = rule.body.index(token)    
            first_in_rest = self._find_first_from_nonterminal_list(rule.body[token_index+1:], [])
            follow_set.update(first_in_rest-{"ε"})

            if "ε" in first_in_rest:
                if rule.head not in explored_tokens:
                    head_follow_set = self._find_follow_set(rule.head, explored_tokens+[rule.head])
                    follow_set.update(head_follow_set)

        return follow_set

    def _find_first_from_nonterminal_list(self, token_list: list[str], explored_tokens: list[str]) -> OrderedSet:
        if len(token_list) == 0:
            return OrderedSet({"ε"})
        
        first_set = OrderedSet()
        current_rule_set = OrderedSet()
        for i, body_token in enumerate(token_list):
            if body_token in explored_tokens: break

            current_rule_set = self._find_first_set(body_token, explored_tokens+[body_token])
            first_set.update(current_rule_set-{"epsilon"})

            if "ε" not in current_rule_set: break

        if i == len(token_list)-1 and "ε" in current_rule_set:
            first_set.add("ε")

        return first_set
