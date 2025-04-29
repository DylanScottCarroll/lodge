from typing import List, Optional, Tuple
from .table import ParseTable
from .tokenizer import Token, TokenStream
from .symbol import Symbol


class ParseNode:
    def __init__(self, symbol:Symbol, parent:Symbol|None=None, children:list|None=None):
        self.symbol:Symbol = symbol
        self.parent:ParseNode = parent
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
                string +=  f' : "{child.text.replace("\n", "\\n")}"'
            else:
                string += "\n" + "    "*(level+1) + f'<{str(type(child))} : "{str(child)}">' + "\n"


        return string
    
    def __str__(self):
        return f"<ParseNode {str(self.symbol)}>"
    
    def __repr__(self):
        return str(self)

class Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, grammar: str):
        self.grammar = grammar
        self.table = ParseTable(grammar)

    def __call__(self, token_stream: TokenStream) -> ParseNode:
        # Make the stack of named tuples
        stack: List[Tuple[ParseNode|None, int]] = [(None, 0)]



        while True:
            _, state = stack[-1]
            
            #token = string[0] if len(string) > 0 else "$"
            token = token_stream.peek()
            
            # print("="*80)
            
            # print("Stack:\n\t", stack, end="\n\n")
            # print("State:", end="\n\t")
            # print(*self.table.states[state].items, sep="\n\t", end="\n\n")

            # print("Next Token:\n\t", token, end="\n\n")

            # print("Action:\n\t", self.table[state, token.symbol])

            # print()
            action = self.table[state, token.symbol]

            if action[0] == "shft":
                _, goto = action

                new_node = ParseNode(token.symbol, children=[token])

                stack.append((new_node, goto))

                token_stream.pop()

            elif action[0] == "red":
                _, head, body_length = action
                
                children = [stack_item[0] for stack_item in stack[-body_length:]]
                stack = stack[:-body_length]
                
                new_node = ParseNode(head, children=children)

                goto_state = self.table[stack[-1][1], head][1]    
                
                stack.append((new_node, goto_state))

            elif action[0] == "acc":
                return ParseNode(self.grammar.start_symbol, None, [stack[1][0]])
            
            else:
                print(f"ERROR: Unexpected token {token}")

                print("Stack Contents:")
                print(stack)

                print("Possible parser states:")
                print(self.table.states[state])
                    
                print()
                breakpoint()
                exit()
