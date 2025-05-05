from .table import Action, Accept, Shift, Reduce, Error
from .tokenizer import Token, TokenStream
from .symbol import Symbol
from .parser import ParseNode

from  collections import namedtuple

class CFG_Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, goto_table: dict[tuple[int, Symbol], int], action_table:dict[tuple[int, Symbol], Action]):
        self.goto_table = goto_table
        self.action_table = action_table

    def show_state(self, stack, state, token):
        print("="*100)
        print("Stack:")
        for node in stack:
            if isinstance(node[0], ParseNode):
                node[0].print()
            else:
                print(node[0])
        print("-"*(len(str(token))+1))
        print(token)

    def __call__(self, token_stream: TokenStream) -> ParseNode:
        StackItem = namedtuple("StackItem", "node, state")
        stack: list[StackItem]= [StackItem(None, 0)]

        while True:
            _, state = stack[-1]
            token = token_stream.peek()

            action = self.action_table[state, token.symbol]

            if isinstance(action, Shift):
                new_node = ParseNode(token.symbol, tokens=[token])
                
                stack.append(StackItem(new_node, action.new_state))
                
                token_stream.pop()

            elif isinstance(action, Reduce):
                head, body_length = action.head, action.body_length
                
                children = [stack_item.node for stack_item in stack[len(stack)-body_length:] ]
                stack = stack[:len(stack)-body_length]

                new_node = ParseNode(head, children=children)
                goto_state = self.goto_table[stack[-1].state, head]
                stack.append(StackItem(new_node, goto_state))

            elif isinstance(action, Accept):
                return ParseNode(action.start, None, [stack[1].node])
            
            else:

                self.show_state(stack, state, token)

                print(f"ERROR: Unexpected token {token}")
                breakpoint()
                exit()

