from .grammar import Grammar
from .symbol import Symbol
from .tokenizer import Tokenizer, TokenStream, Token

class ParseNode:
    def __init__(self, symbol:Symbol, children:list|None=None):
        self.symbol = symbol
        self.children = children or []
        self.attributes = {}

    def print(self):
        print(self.format_tree())

    def format_tree(self, level:int=0):
        string = f"{'   '*level}{str(self.symbol)}\n"        
        for child in self.children:
            if isinstance(child, ParseNode):
                string += "   "*level + child.format_tree(level+1) + "\n"
            elif isinstance(child, Token):
                string += "   "*(level*2) + child.text + "\n"
            else:
                string += "   "*(level*2) + str(child) + "\n"


        return string

class Parser:
    """Encapsulates the parsing process for a given grammar."""

    def __init__(self, grammar: Grammar):
        self.grammar:Grammar = grammar
        self.table:dict[Symbol, dict[Symbol, list[Symbol]]] = self._find_ll_table()
        
        return
        for k, v in self.table.items():
            print(f"{str(k)}:")
            for sk, sv in v.items():
                print(f"\t{str(sk): <15}: {" ".join(map(str, sv))}")


    def __call__(self, token_stream: "TokenStream") -> ParseNode:
        return self.parse(self.grammar.start_symbol, token_stream)
    
    def parse(self, symbol:Symbol, token_stream:'TokenStream') -> ParseNode:              
        root_node = ParseNode(symbol) 
        stack = [root_node]

        while stack:
            node = stack.pop()
            symbol = node.symbol
    
            if symbol.terminal:
                if symbol == token_stream.peek().symbol:
                    node.children.append(token_stream.pop())
                elif symbol != Symbol.epsilon:
                    raise SyntaxError(f"Expected {symbol}, but found {token_stream.peek().symbol}")
            
            else:
                next_token = token_stream.peek()
                if next_token.symbol not in self.table[symbol]:
                    raise SyntaxError(f"The symbol {next_token.symbol} doesn't seem like it can go here. {symbol}")

                production = self.table[symbol][next_token.symbol]
                for prod_symbol in production[::-1]:
                    new_node = ParseNode(prod_symbol)
                    
                    node.children.insert(0, new_node)
                    stack.append(new_node)


        return root_node



    # def parse(self, symbol:Symbol, token_stream:Tokenizer) -> ParseNode:              
    #     next_token = token_stream.peek()
        
    #     if next_token.symbol not in self.table[symbol]:
    #         raise SyntaxError(f"The symbol {next_token.symbol} doesn't seem like it can go here. {symbol}")
        
    #     node = ParseNode(symbol, [])

    #     production = self.table[symbol][next_token.symbol]
        
    #     for prod_symbol in production:
    #         if not prod_symbol.terminal:
    #             child = self.parse(prod_symbol, token_stream)
    #             if child:
    #                 node.children.append(child)
    #         else:
    #             if prod_symbol == token_stream.peek().symbol:
    #                 token_stream.pop()
    #                 node.children.append(ParseNode(prod_symbol))
    #             elif prod_symbol != Symbol.epsilon:
    #                 raise SyntaxError(f"Expected {prod_symbol}, but found {token_stream.peek().symbol}")
                
        # return node

    def _find_ll_table(self) -> dict:
        g = self.grammar

        table = {}

        for symbol in g.nonterminals:
            rules = g.get_rules_by_head(symbol)
            table[symbol] = {}
            for rule in rules:
                terminals = g._find_first_from_nonterminal_list(rule.body)
                if Symbol.epsilon in terminals:
                    terminals = terminals - {Symbol.epsilon}
                    terminals.update(g.follow_sets[symbol])

                for terminal in terminals:
                    if terminal in table[symbol]:
                        print(f"ERROR: First set conflict between:\n" +
                            f"\t({symbol.identifier}, {terminal.identifier}) -> {" ".join(map(str, table[symbol][terminal]))}\n" +
                            f"\t({symbol.identifier}, {terminal.identifier}) -> {" ".join(map(str, rule.body))}"
                            ) 
                    else:
                        table[symbol][terminal] = rule.body

        return table
    
    
