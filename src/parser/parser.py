from .table import ParseTable, Accept, Shift, Reduce, Error
from .tokenizer import Token, TokenStream
from .symbol import Symbol
from .grammar import Grammar

from  collections import namedtuple

class ParseNode:
    def __init__(self, symbol:Symbol, parent:'ParseNode|None'=None, children:list|None=None, tokens:list|None = None):
        self.symbol:Symbol = symbol
        self.parent:ParseNode|None= parent
        
        self.children: list[ParseNode] = children or []
        self.tokens: list[Token] = tokens or []
        
        self.attributes = {}

        for child in self.children:
            child.parent = self
            self.tokens.extend(child.tokens)
        
        if len(self.tokens) == 1 and len(self.children) == 0:
            self.attributes["token"] = self.tokens[0].text

    def _get(self, symbol:Symbol|str|None=None, index:int=0):
        if symbol is None:
            return self.children[index]
        else:
            for child in self.children:
                if child.symbol == symbol or child.symbol.identifier == symbol:
                    if index == 0:
                        return child
                    else:
                        index -= 1

            raise KeyError(f"Index {index} out of bounds for symbol {repr(symbol)}.")

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._get(None, key)
        elif isinstance(key, Symbol) or isinstance(key, str):
            return self._get(symbol=key)
        elif isinstance(key, tuple) and len(key) == 2:
            symbol, index = key
            if isinstance(symbol, Symbol) or isinstance(symbol, str):
                return self._get(symbol=symbol, index=index)
            else:
                raise KeyError(f"Unexpected symbol type: '{symbol}'")

        else:
            raise KeyError(f"Unexpected key for ParseNode: '{key}'")
    
    def __contains__(self, key):
        try:
            if isinstance(key, tuple):
                self[*key]
            else:
                self[key]

            return True
        except KeyError:
            return False


    def print(self):
        print(self.format_tree())

    def format_tree(self, level:int=0):
        if len(self.children) > 0:
            string = f"{'    '*level}{str(self.symbol)}"  
            for child in self.children:
                string += "\n" + child.format_tree(level+1)
        elif len(self.tokens) != 0:
            string =  f"{'    '*level}{str(self.symbol)} : {repr(self.tokens[0].text)}"
        else:
            string =  f"{'    '*level}{str(self.symbol)} : ε"

        return string

    def __str__(self):
        return f"<ParseNode {str(self.symbol)}>"
    
    def __repr__(self):
        return str(self)


class Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, grammar: Grammar):
        self.table = ParseTable(grammar)

    def show_state(self, stack, state, token):
        print("="*100)
        print("Stack:")
        for node in stack:
            if isinstance(node[0], ParseNode):
                node[0].print()
            else:
                print(node[0])
        print("-"*50)
        print("Parser state:")
        print(self.table.states[state])
        
        print("-"*50)
        print(f"Next Token: {token}")

    def __call__(self, token_stream: TokenStream) -> ParseNode:
        StackItem = namedtuple("StackItem", "node, state")
        stack: list[StackItem]= [StackItem(None, 0)]

        while True:
            _, state = stack[-1]
            token = token_stream.peek()
            action = self.table.action(state, token.symbol)

            if isinstance(action, Shift):
                new_node = ParseNode(token.symbol, tokens=[token])
                
                stack.append(StackItem(new_node, action.new_state))
                
                token_stream.pop()

            elif isinstance(action, Reduce):
                head, body_length = action.head, action.body_length
                
                children = [stack_item.node for stack_item in stack[len(stack)-body_length:] ]
                stack = stack[:len(stack)-body_length]

                new_node = ParseNode(head, children=children)
                
                for action_routine in action.action_routines:
                    self.apply_action_routine(new_node, action_routine)
            
                goto_state = self.table.goto(stack[-1].state, head)    
                stack.append(StackItem(new_node, goto_state))

            elif isinstance(action, Accept):
                root_node = ParseNode(action.start, None, [stack[1].node])
                
                for action_routine in action.action_routines:
                    self.apply_action_routine(root_node, action_routine)
                
                return root_node
                
            else:

                self.show_state(stack, state, token)

                print(f"ERROR: Unexpected token {token}")
                breakpoint()
                exit()

    def apply_action_routine(self, parse_node, action_routine):
        def eval_action_val(val):
            if isinstance(val, str):
                return val
            else:
                symbol, index, attribute = val
                return parse_node[symbol, index].attributes[attribute]

        if action_routine.val_type == "Node":
            vals = list(map(eval_action_val, action_routine.val_args))
            
            node_children = []
            for child in vals[1:]:
                if isinstance(child, list):
                    node_children.extend(child)
                else:
                    node_children.append(child)
            print(f"{parse_node}.{action_routine.dest} = {vals[0]}{node_children}")
            parse_node.attributes[action_routine.dest] = ( vals[0], node_children )

        if action_routine.val_type == "List":
            vals = list(map(eval_action_val, action_routine.val_args))

            new_list = []
            for elem in vals:
                if isinstance(elem, list):
                    new_list.extend(elem)
                else:
                    new_list.append(elem)

            print(f"{parse+_node}.{action_routine.dest} = {new_list}")
            parse_node.attributes[action_routine.dest] = new_list

        if action_routine.val_type == "Val":
            val = eval_action_val(action_routine.val_args[0]) 
            print(f"{parse_node}.{action_routine.dest} = {val}")
            parse_node.attributes[action_routine.dest] = val
