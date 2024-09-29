from .table import ParseTable

class ParseNode:
    def __init__(self, token, children=None):
        self.token = token
        self.children = children if children is not None else []

    def __str__(self):
        return self._stringify(0)

    def _stringify(self, level):
        string = f"{'   '*level}{self.token}\n"
        for child in self.children:
            string += "   "*level + child._stringify(level+1) + "\n"

        return string

    def __repr__(self):
        return str(self)

class Parser:
    def __init__(self, grammar):
        self.grammar = grammar
        self.table = ParseTable(grammar)

    def __call__(self, string):
        stack = [(None, 0)]

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