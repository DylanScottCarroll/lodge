from .utils import OrderedSet

from .symbol import Symbol
from .grammar import Grammar, GrammarRule
from .grammar import ActionRoutine

import copy

class StateItem:
    """
    Represents a partially completed grammar rule in a state of a partially parsed grammar.
    Used as a component of a State object.
    """

    def __init__(self, rule: GrammarRule, follow: tuple[Symbol, ...], position: int = 0) -> None:
        self.head: Symbol = rule.head
        self.body: tuple[Symbol, ...] = tuple(rule.body)
        self.action_routines:list[ActionRoutine] = rule.action_routines
        
        if self.body == (Symbol.epsilon,):
            self.body = ()

        self.follow: tuple[Symbol, ...] = tuple(follow)
        self.position: int = position

        self.finished:bool = self.position == len(self.body)
            
    @property
    def next_symbol(self) -> Symbol|None:
        if self.position < len(self.body):
            return self.body[self.position]
        else:
            return None

    def without_follow(self):
        other = copy.deepcopy(self)
        other.follow = ()
        return other

    def __eq__(self, other) -> bool:
        if hash(self) != hash(other) or not isinstance(other, StateItem):
            return False
        
        elif (self.head == other.head and self.body == other.body and 
              self.position == other.position and self.follow == other.follow):
                
            return True
            
        else:
            return False

    def __hash__(self) -> int:
        return ( hash(self.head) 
               ^ hash(self.body) 
               ^ hash(self.position)
               ^ hash(self.follow) )
    
    def __str__(self) -> str:
        string:str = f"[{self.head} -> "
        
        for i, symbol in enumerate(self.body + (None,)):
            if i == self.position:
                string += " •"
            
            if i < len(self.body):
                string += f" {symbol}"

        string += f", ('{"' , '".join(map(str, self.follow))}')]"

        return string

    def __repr__(self):
        return str(self)



class State:
    """
    A set of partially completed grammar rules, representing a state in a partially parsed grammar.
    When a state is created, it is automatically closed to include all subsequent rules that can be reached from the current state.

    Attributes:
        items (OrderedSet): A set of StateItems representing the rules in the state.
    """

    def __init__(self, grammar: Grammar, *items: StateItem) -> None:
        self.items: OrderedSet = OrderedSet(items)
        self._grammar: Grammar = grammar

        # Create closure
        for item in list(self.items):
            item:StateItem
            if not item.finished:
                new_items = self._close_helper(item, OrderedSet())
                self.items.update(new_items)


    def _close_helper(self, item: StateItem, visited: OrderedSet) -> OrderedSet:
        if item.body == ():
            return OrderedSet()

        next_symbol:Symbol = item.body[item.position]
        if next_symbol.terminal:
            return OrderedSet()
        
        follow_set = self._grammar.follow_sets[next_symbol]    
        
        items = OrderedSet()
        for rule in self._grammar.get_rules_by_head(next_symbol):
            new_item = StateItem(rule, follow_set)
            items.add(new_item)

            if new_item.without_follow() not in visited:
                visited.add(new_item.without_follow())
                new_items = self._close_helper(new_item, visited)    
                items.update(new_items)

        return items

    def get_transition_result(self, symbol: Symbol) -> 'State':
        def shift_item(item: StateItem) -> StateItem:
            return StateItem(item, item.follow, item.position+1)
        
        items = [shift_item(item) for item in self.items
                 if (item.position < len(item.body)) and (item.body[item.position] == symbol)]
        
        return State(self._grammar, *items)


    def __hash__(self) -> int:
        hash_value = 0
        for item in self.items:
            hash_value ^= hash(item)

        return hash_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return False
        return self.items == other.items

    
    def __str__(self) -> str:
        return "ItemSet{" + "\n\t".join(map(str, self.items)) + "}"
    
    def __repr__(self) -> str:
        return str(self)




class Accept:
    def __init__(self, start:Symbol, action_routines:list[ActionRoutine]|None=None):
        self.start = start
        self.action_routines = action_routines or []

    def __str__(self):
        return "Acc"

class Reduce:
    def __init__(self, head: Symbol, body_length:int, action_routines:list[ActionRoutine]|None=None):
        self.head = head
        self.body_length = body_length
        self.action_routines = action_routines or []
    def __str__(self):
        return f"Red({self.head.identifier} {self.body_length})"

class Shift:
    def __init__(self, new_state: int):
        self.new_state = new_state
    def __str__(self):
        return f"Shf({self.new_state})"

class Error:
    def __str__(self):
        return "Err"

type Action = (Accept | Reduce | Shift | Error)

class ParseTable:
    """
    Represents an LR(1) parse table for a given grammar.
    
    Attributes:
        states (list): A list of states in the parse table.
        state_ids (dict): A dictionary mapping states to their corresponding IDs.
        goto_table (dict): A dictionary representing the Goto table of the parse table.
        action_table (dict): A dictionary representing the Action table of the parse table.
        
    Methods:
        goto(state: int, symbol: str) -> int:
            * Returns the state to which the given state transitions on the given symbol.
        action(state: int, token: str) -> Tuple[str, ...]:
            * Returns the action and any additional arguments for the given state and token.
        __getitem__(key: Tuple[int, str]) -> Tuple[str, ...]: 
            * Returns the action and any additional arguments for the given state and token.            
            """

    def __init__(self, grammar: Grammar) -> None:
        self._grammar: Grammar = grammar

        self.states: list[State] = []
        self.state_ids: dict[State, int] = {}
        
        self.goto_table: dict[tuple[int, Symbol], int] = {}
        self.action_table: dict[tuple[int, Symbol], Action] = {}

        self._generate_table()

    def goto(self, state: int, symbol: Symbol) -> int:
        return self.goto_table.get((state, symbol), -1)

    def action(self, state: int, symbol: Symbol) -> Action:
        return self.action_table.get((state, symbol), Error())

    def _generate_table(self) -> None:
        # Make Start State
        start = self._grammar.start_symbol

        start_rules = self._grammar.get_rules_by_head(start)
        if len(start_rules) != 1:
            print("ERROR: The start symbol must only have one production!")
            exit()

        start_item = StateItem(start_rules[0], self._grammar.follow_sets[start] )
        current_state = State(self._grammar, start_item)
        self.state_ids[current_state] = 0

        # Populate Goto Table
        stack = [current_state]
        i = 1
        while len(stack) > 0:
            current_state = stack.pop(0)
            self.states.append(current_state)

            for symbol in self._grammar.terminals.union(self._grammar.nonterminals):            
                new_state = current_state.get_transition_result(symbol)
                if len(new_state.items) == 0: continue
                
                if new_state not in self.state_ids.keys():
                    stack.append(new_state)
                    
                    self.state_ids[new_state] = i
                    i += 1

                self.goto_table[(self.state_ids[current_state], symbol)] = self.state_ids[new_state]
                
        
        # Populate Action Table
        for state, id in self.state_ids.items():
            for item in state.items:
                item: StateItem
                if item.finished: # or (item.body == [Symbol.epsilon]):
                    if item.head == self._grammar.start_symbol:
                        self.action_table[id, Symbol.eof] = Accept(self._grammar.start_symbol, item.action_routines)
                    else:
                        for follow in item.follow:
                            self.action_table[(id, follow)] = Reduce(item.head, len(item.body), item.action_routines)
                
                elif (id, item.next_symbol) in self.goto_table.keys():
                    id: int
                    if item.next_symbol is not None:
                        self.action_table[id, item.next_symbol] = Shift(self.goto_table[id, item.next_symbol])
                else:
                    print(f"Error, no valid action for {item} in state {id}:{state}")
                    breakpoint()


    def __str__(self) -> str:
        string:str = ""

        string += "States:\n"
        for state, id in self.state_ids.items():
            print(f"State {id}:{state}\n")
        
        string += "\nAction Table:\n"
        spacing = 20

        string += " "*5 + "│"
        for token in self._grammar.terminals:
            string += f"{str(token
            ):^{spacing}}"


        string += "\n" + "─"*5 + "┼" +  "─"*(spacing*len(self._grammar.terminals) )


        for state, id in self.state_ids.items():
            string += f"\n{id:>4} │"
            
            for token in self._grammar.terminals:
                action = self.action_table.get((id, token), Error())
                action = str(action)
                string += f"{action:^{spacing}}"
            
        #string += "\n" +  "="*200 + "\n"

        string += "\n\nGoto Table:\n"
        spacing = 8

        string += " "*5 + "│"
        for token in list(self._grammar.terminals) + list(self._grammar.nonterminals):
            string += f"{str(token):^{len(str(token))+4}}"


        string += "\n" + "─"*5 + "┼" +  "─"*(spacing*(len(self._grammar.terminals)+len(self._grammar.nonterminals)+1) )

        for state, id in self.state_ids.items():
            string += f"\n{id:>4} │"
            
            for token in list(self._grammar.terminals) + list(self._grammar.nonterminals):
                new_state = self.goto_table.get((id, token), "")
                string += f"{new_state:^{len(str(token))+4}}"

        return string

