import re
import pickle
from collections import namedtuple

from .utils import OrderedSet
from .utils.errors import ParserSyntaxError, ParserTokenizerError, GrammarError

from .symbol import Symbol
from .tree import ParseNode, SyntaxNode
from .grammar import Grammar, GrammarRule, ActionRoutine
from .table import ParseTable, Accept, Reduce, Shift, Error
from .tokenizer import Tokenizer, Token, TokenStream


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

class Parser:
    """
    Contains the logic for reading a syntax description file and extracting the grammar and tokenizer from it.
    """

    def __init__(self, filename):
        raw_token_rules, raw_grammar_rules =  self._read_file(filename)
        print("Grammar File Parsed")

        token_rules, terminals = self._process_token_rules(raw_token_rules)
        grammar_rules, start_symbol, nonterminals, terminals, token_rules = self._process_grammar_rules(raw_grammar_rules, terminals, token_rules)
        print("Rules Parsed")


        self.grammar = Grammar(grammar_rules, nonterminals, terminals, start_symbol)
        print("Grammar Done")
        self.table = ParseTable(self.grammar)
        print("Table Done")
        self.tokenizer =  Tokenizer(token_rules)
        print("Tokenizer Done")

    def parse(self, text):
        self.parser_state = ParserState(self.table, self.tokenizer(text))

        return self.parser_state()

    def resume(self, parser_state):
        self.parser_state = parser_state
        return self.parser_state()

    def _process_token_rules(self, raw_rules) -> tuple[list, OrderedSet]:
        rules = []
        terminals = OrderedSet()
        for head, body in raw_rules:
            terminals.add(Symbol(head, True))
            rules.append((Symbol(head, True), body))

        return rules, terminals

    def _process_grammar_rules(self, raw_rules, terminals, token_rules):
        # Find all nonterminals
        nonterminal_identifiers:OrderedSet = OrderedSet(head for head, _, _ in raw_rules)
        
        literal_tokens = []

        rules = []
        nonterminals = OrderedSet()
        
        for head, body, actions in raw_rules:
            head = Symbol(head, False)
             

            body_symbols = [
                Symbol(identifier, identifier not in nonterminal_identifiers)
                for _, identifier in body 
            ]

            action_routines = [
                ActionRoutine(dest, val_type, val_args)
                for dest, (val_type, val_args) in actions
            ]

            # Update Symbol Sets
            terminals.update([symbol for symbol in body_symbols if symbol.terminal])
            nonterminals.add(head)

            #Add to literal expression
            literal_tokens.extend([re.escape(symbol) for kind, symbol in body if kind == "literal"])
    
            # Add new grammar rule
            rules.append(GrammarRule(head, body_symbols, action_routines))

        literal_token_rule = ( Symbol("*", True), "|".join(literal_tokens) )
        token_rules.insert(0, literal_token_rule)

        start_symbol = rules[0].head
        
        return rules, start_symbol, nonterminals, terminals, token_rules


    def _read_file(self, filename:str) -> tuple[list, list]:
        with open("./parser/resources/cfg_parser.pkl", "rb") as f:
            cfg_grammar, cfg_tokenizer = pickle.load(f)
        
        with open(filename) as f:
            text = f.read()
        
        tree = None
        try:
            token_stream = cfg_tokenizer(text)
            cfg_parser = ParserState(ParseTable(cfg_grammar), token_stream)
            tree = cfg_parser()

        except ParserSyntaxError as e:
            raise GrammarError(f"Source grammar file has a syntax error. Unexpected token: {str(e.parser_state)}")
        except ParserTokenizerError as e:
            raise GrammarError(f"Source grammar file has an unparasble token at position {e.position}.")
       
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
                string = symbol["literal"].attributes["token"]
                if string[0] == '`' and string[-1] == '`':
                    string = string[1:-1]
                body.append(("literal", string))
            elif "id" in symbol:
                body.append(("id", symbol["id"].attributes["token"]))
            else:
                body.append(("literal", symbol[0].attributes["token"]))

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
            node_val = self._unpack_action_id(action_body["action_id"])
            
            node_children = tuple([
                self._unpack_node_id(action_id) for action_id in
                iter_recursed_node(action_body["node_ids"], "node_id", "node_ids")
            ])
            return ("Node", (node_val,) + node_children)

        elif action_body[0].symbol.identifier == "[":
            # Parse routine list declaration
            node_children = tuple([
                self._unpack_action_id(action_id) for action_id in
                iter_recursed_node(action_body["list_vals"], "action_id", "list_vals")
            ])
            
            return ("List", node_children)
       
        else:
            # Parse simple routine
            return ("Val", ( self._unpack_action_id(action_body["action_id"]), ))
    
    def _unpack_node_id(self, node_id) -> tuple:
        head = node_id["id"].attributes["token"]  
        body = self._unpack_action_id(node_id["action_id"])
        
        return (head, body)

    def _unpack_action_id(self, action_id) -> tuple:
        if "string_literal" in action_id:
            return action_id["string_literal"].attributes["token"][1:-1]
        else:
            index = int(action_id["number"].attributes["token"]) if ("number" in action_id) else 0
            id1 = action_id["id", 0].attributes["token"]
            id2 = action_id["id", 1].attributes["token"]
            
            return (id1, index, id2)

StackItem = namedtuple("StackItem", "node, state")
class ParserState:
    """Encapsulates the parsing process for a given grammar and input stream."""

    def __init__(self, table: ParseTable, token_stream: TokenStream):
        self.table = table
        self.token_stream: TokenStream = token_stream

        self.stack: list[StackItem]= [StackItem(None, 0)]
        self.token: Token = Token(Symbol.epsilon, "", (0, 0))
        self.state: int = 0


    def __str__(self):
        string = f"\n{' Stack ':-^75}\n"
        for node in self.stack:
            if isinstance(node[0], ParseNode):
                string += f"{node[0]}\n"
            else:
                string += "{node[0]}\n"
        string += f"{' Parser state ':-^75}\n"
        string += f"{
        self.table.states[self.state]}\n"
        
        string += "-"*75 + "\n"
        string += f"Next Token: {self.token}\n"

        return string


    def __call__(self) -> ParseNode:
        while True:
            _, self.state = self.stack[-1]
            self.token = self.token_stream.peek()
            action = self.table.action(self.state, self.token.symbol)

            if isinstance(action, Shift):
                new_node = ParseNode(self.token.symbol, token=self.token)
                self.stack.append(StackItem(new_node, action.new_state))
                self.token_stream.pop()

            elif isinstance(action, Reduce):
                head, body_length = action.head, action.body_length
                
                children = [stack_item.node for stack_item in self.stack[len(self.stack)-body_length:] ]
                self.stack = self.stack[:len(self.stack)-body_length]

                new_node = ParseNode(head, children=children)
                
                for action_routine in action.action_routines:
                    self.apply_action_routine(new_node, action_routine)
            
                goto_state = self.table.goto(self.stack[-1].state, head)    
                self.stack.append(StackItem(new_node, goto_state))

            elif isinstance(action, Accept):
                root_node = ParseNode(action.start, None, [self.stack[1].node])
                
                for action_routine in action.action_routines:
                    self.apply_action_routine(root_node, action_routine)
                
                return root_node
                
            else:
                raise ParserSyntaxError(self)
        

    def apply_action_routine(self, parse_node, action_routine):
        def eval_action_val(val):
            if isinstance(val, str):
                return val
            else:
                symbol, index, attribute = val
                return parse_node[symbol, index].attributes[attribute]

        if action_routine.val_type == "Node":
            node_id, *node_attribute_pairs = action_routine.val_args
            node_value = eval_action_val(node_id)
            node_attributes = {
                key : eval_action_val(id) 
                for key, id in node_attribute_pairs
            }

            parse_node.attributes[action_routine.dest] = SyntaxNode(node_value, node_attributes)

        if action_routine.val_type == "List":
            vals = list(map(eval_action_val, action_routine.val_args))

            new_list = []
            for elem in vals:
                if isinstance(elem, list):
                    new_list.extend(elem)
                else:
                    new_list.append(elem)

            parse_node.attributes[action_routine.dest] = new_list

        if action_routine.val_type == "Val":
            val = eval_action_val(action_routine.val_args[0]) 
            parse_node.attributes[action_routine.dest] = val


