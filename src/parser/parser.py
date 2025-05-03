from typing import List, Optional, Tuple
from .table import ParseTable
from .tokenizer import Token, TokenStream
from .symbol import Symbol
from .grammar import Grammar


class ParseNode:
    def __init__(self, symbol:Symbol, parent:'ParseNode|None'=None, children:list|None=None):
        self.symbol:Symbol = symbol
        self.parent:ParseNode|None= parent
        self.children: list[ParseNode] = children or []
        self.attributes = {}

        for child in self.children:
            child.parent = self

    def print(self):
        print(self.format_tree())

    def format_tree(self, level:int=0):
        string = f"{'    '*level}{str(self.symbol)}"  
        for child in self.children:
            if isinstance(child, ParseNode):
                string += "\n" + child.format_tree(level+1)
            
            elif isinstance(child, Token):
                string +=  "\n" + "    "*(level+1) + f'{child.symbol} : "{child.text.replace("\n", "\\n")}"'
            else:
                string += "\n" + "    "*(level+1) + f'<{str(type(child))} : "{str(child)}">' + "\n"


        return string
    
    def __str__(self):
        return f"<ParseNode {str(self.symbol)}>"
    
    def __repr__(self):
        return str(self)

class Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
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
        # Make the stack of named tuples
        stack: list[tuple]= [(None, 0)]


        #for state in self.table.states:
        #    for item in state.items:
        #        print(item)
        #
        #    print("="*50)
        #print(self.table)
        

        while True:
            _, state = stack[-1]
            token = token_stream.peek()


            self.show_state(stack, state, token)
            input()


            action = self.table[state, token.symbol]

            if action[0] == "shft":
                _, goto = action

                # new_node = ParseNode(token.symbol, children=[token])
                new_node = token

                stack.append((new_node, goto))

                token_stream.pop()

            elif action[0] == "red":
                _, head, body_length = action #type: ignore
                head: Symbol
                body_length: int
                
                children = [stack_item[0] for stack_item in stack[len(stack)-body_length:] ]
                stack = stack[:len(stack)-body_length]

                new_node = ParseNode(head, children=children)
                goto_state = self.table[stack[-1][1], head][1]    
                stack.append((new_node, goto_state))

            elif action[0] == "acc":
                return ParseNode(self.grammar.start_symbol, None, [stack[1][0]])
            
            else:

                self.show_state(stack, state, token)

                print(f"ERROR: Unexpected token {token}")
                breakpoint()
                exit()

