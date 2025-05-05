import re

from .tokenizer import Tokenizer
from .ordered_set import OrderedSet
from .grammar import Grammar, GrammarRule, ActionRoutine 
from .parser import Parser, ParseNode
from .symbol import Symbol

import pickle

def iter_recursed_node(node:ParseNode, value_id:str, rest_id:str):
    children_left = True
    while children_left:
        if value_id in node:
            yield node[value_id]
        else:
            children_left = False

        if rest_id in node:
            node = node[rest_id]
        else:
            children_left = False

class SyntaxDescription:
    """
    Contains the logic for reading a syntax description file and extracting the grammar and tokenizer from it.
    """

    def __init__(self, filename):
        raw_token_rules, raw_grammar_rules =  self._read_file(filename)

        token_rules, terminals = self._process_token_rules(raw_token_rules)
        grammar_rules, start_symbol, nonterminals, terminals = self._process_grammar_rules(raw_grammar_rules, terminals)
    

        self.grammar = Grammar(grammar_rules, nonterminals, terminals, start_symbol)
        self.parser = Parser(self.grammar)
        self.tokenizer =  Tokenizer(token_rules)

        print(*self.tokenizer.rules, sep="\n")
        
        print("#"*100)

        print(*self.grammar.rules, sep="\n")
       
        print("#"*100)
        
        print(self.parser.table)

    def _process_token_rules(self, raw_rules) -> tuple[list, OrderedSet]:
        rules = []
        terminals = OrderedSet()
        for head, body in raw_rules:
            terminals.add(Symbol(head, True))
            rules.append((Symbol(head, True), body))

        return rules, terminals

    def _process_grammar_rules(self, raw_rules, terminals):
        # Find all nonterminals
        nonterminal_identifiers:OrderedSet = OrderedSet(head for head, _, _ in raw_rules)
        
        rules = []
        nonterminals = OrderedSet()
        
        for head, body, actions in raw_rules:
            head = Symbol(head, False)
             
            body = [
                Symbol(identifier, identifier not in nonterminal_identifiers)
                for identifier in body 
            ]

            action_routines = [
                ActionRoutine(dest, val_type, val_args)
                for dest, (val_type, val_args) in actions
            ]

            # Update Symbol Sets
            terminals.update([symbol for symbol in body if symbol.terminal])
            nonterminals.add(head)

            # Add new grammar rule
            rules.append(GrammarRule(head, body, action_routines))


        start_symbol = rules[0].head
        
        return rules, start_symbol, nonterminals, terminals


    def _read_file(self, filename:str) -> tuple[list, list]:
        with open("./parser/cfg_parser.pkl", "rb") as f:
            cfg_tokenizer, cfg_parser = pickle.load(f)
        
        with open(filename) as f:
            text = f.read()
        
        token_stream = cfg_tokenizer(text)
        tree = cfg_parser(token_stream)
                    
        return self._unpack_tree(tree)

    def _unpack_tree(self, tree) -> tuple[list, list]:
        lines = iter_recursed_node(tree["lines"], "line", "lines")
        token_rules = []
        grammar_rules = []
        for line in lines:
            if "=" in line:
                token_rule = self._unpack_token_rule(line)
                token_rules.append(token_rule)
            elif "arrow" in line:
                grammar_rule = self._unpack_grammar_rule(line)
                grammar_rules.append(grammar_rule)
        
        return (token_rules, grammar_rules)

    def _unpack_token_rule(self, line) -> tuple:
        head = line["id"].attributes["token"]
        body:str = line["regex"].attributes["token"][1:-1] 

        return (head, body)

    def _unpack_grammar_rule(self, line) -> tuple:
        head = line["id"].attributes["token"]
        
        body = []
        for symbol in iter_recursed_node(line["cfg_body"], "symbol", "cfg_body"):
            if "literal" in symbol:
                body.append(symbol[0].attributes["token"][1:-1])
            else:
                body.append(symbol[0].attributes["token"])

            print(body[0])
        
        if "action_routines" in line:
            routines = self._unpack_action_routines(line["action_routines"])
        else:
            routines = []
        
        return (head, body, routines)


    def _unpack_action_routines(self, routines) -> list[tuple]:
        parsed_routines = []
        for routine in iter_recursed_node(routines, "action_routine", "action_routines"):
            head = routine["id"].attributes["token"]
            body = self._unpack_action_body(routine["action_body"])

            parsed_routines.append((head, body))
        return parsed_routines

    def _unpack_action_body(self, action_body):
        if action_body[0].symbol.identifier == "(":
            # Parse routine node declaration   
            node_val = self._unpack_action_val(action_body["action_val"])
            
            node_children = tuple([
                self._unpack_action_val(action_val) for action_val in
                iter_recursed_node(action_body["action_val_list"], "action_val", "action_val_list")
            ])
            
            return ("Node", (node_val,) + node_children)

        elif action_body[0].symbol.identifier == "[":
            # Parse routine list declaration
            node_children = tuple([
                self._unpack_action_val(action_val) for action_val in
                iter_recursed_node(action_body["action_val_list"], "action_val", "action_val_list")
            ])
            
            return ("List", node_children)
       
        else:
            # Parse simple routine
            return ("Val", ( self._unpack_action_val(action_body["action_val"]), ))

    
    def _unpack_action_val(self, action_val) -> tuple:
        if "string_literal" in action_val:
            return (action_val["string_literal"].attributes["token"][1:-1] , )
        else:
            index = int(action_val["number"].attributes["token"]) if ("number" in action_val) else 0
            id1 = action_val["id", 0].attributes["token"]
            id2 = action_val["id", 1].attributes["token"]
            
            return (id1, index, id2)


class BasicSyntaxDescription:


    def __init__(self, filename):
        self.filename = filename

        # Grammar Information
        self._grammar_rules = []
        
        self._nonterminals = OrderedSet()
        self._terminals = OrderedSet()

        self._start_symbol = None

        # Tokenizer Information
        self._tokenizer_rules = []  

        self._read_file(filename)

        self.grammar = Grammar(self._grammar_rules, self._nonterminals, self._terminals, self._start_symbol)
        self.parser = Parser(self.grammar)
        self.tokenizer =  Tokenizer(self._tokenizer_rules)


    def _read_file(self, filename: str) -> None:
        raw_grammar_rules: list = []
        
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                line = line.rstrip("\n")
                
                grammar_match = re.fullmatch(r'([a-zA-Z0-9_-]*) *-> *(.+)', line)
                token_match = re.fullmatch(r'([a-zA-Z0-9_-]*|ε|\*) *= *\/(.+)\/ *', line)
                ignored_match = re.fullmatch(r'#.*|', line)  

                if grammar_match:
                    head, body = grammar_match.groups()
                    body = body.strip().split()
                    raw_grammar_rules.append((head, body))
                
                elif token_match:
                    head, body = token_match.groups()
                    head = Symbol(head, True)

                    
                    self._terminals.add(head)
                    self._tokenizer_rules.append((head, body))

                elif not ignored_match:
                    raise ValueError(f"Invalid syntax on line {i}:\n{line}")

        self._process_grammar_rules(raw_grammar_rules)
                                    

    def _process_grammar_rules(self, raw_rules) -> None:
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
            self._grammar_rules.append(GrammarRule(head_symbol, body_symbols))


        self._start_symbol = self._grammar_rules[0].head
