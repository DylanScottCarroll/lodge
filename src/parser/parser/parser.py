from typing import List, Optional, Tuple
from .table import ParseTable

class ParseNode:
    """
    Represents a node in the parse tree.

    Attributes:
        token (str): The token associated with the node.
        children (List[ParseNode]): A list of child nodes.
    """

    def __init__(self, token: str, children: Optional[List['ParseNode']] = None):
        self.token = token
        self.children = children if children is not None else []

    def __str__(self) -> str:
        return self._stringify(0)

    def _stringify(self, level: int) -> str:
        string = f"{'   '*level}{self.token}\n"
        for child in self.children:
            string += "   "*level + child._stringify(level+1) + "\n"

        return string

    def __repr__(self) -> str:
        return str(self)

class Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, grammar: str):
        self.grammar = grammar
        self.table = ParseTable(grammar)

    def __call__(self, string: str) -> ParseNode:
        stack: List[Tuple[Optional[ParseNode], int]] = [(None, 0)]

        while True:
            state = stack[-1][1]
            token = string[0] if len(string) > 0 else "$"

            action = self.table[state, token]

            if action[0] == "shft":
                _, goto = action

                new_node = ParseNode(token)

                stack.append((new_node, goto))
                string = string[1:]

            elif action[0] == "red":
                _, head, body_length = action
                
                children = [stack_item[0] for stack_item in stack[-body_length:]]
                stack = stack[:-body_length]
                
                new_node = ParseNode(head, children)
                goto = self.table[stack[-1][1], head][1]    
                
                stack.append((new_node, goto))

            elif action[0] == "acc":
                return ParseNode(self.grammar.start_symbol, [stack[1][0]])
            
            else:
                return "Error"
