from typing import Tuple, Optional, List, Dict, Union
from ..ordered_set import OrderedSet
from ..grammar import Grammar, GrammarRule

class StateItem:
    """
    Represents a partially completed grammar rule in a state of a partially parsed grammar.
    Used as a component of a State object.
    """

    def __init__(self, rule: GrammarRule, follow: Tuple[str, ...], position: int = 0) -> None:
        self.head: str = rule.head
        self.body: Tuple[str, ...] = tuple(rule.body)
        self.follow: Tuple[str, ...] = tuple(follow)
        self.position: int = position

    @property
    def next_token(self) -> Optional[str]:
        if self.position < len(self.body):
            return self.body[self.position]
        else:
            return None

    def __eq__(self, other: object) -> bool:
        if hash(self) != hash(other):
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
        string = f"[{self.head} -> "
        
        for i, token in enumerate(self.body + (None,)):
            if i == self.position:
                string += " •"
            
            if i < len(self.body):
                string += f" {token}"

        string += f", ('{"' , '".join(self.follow)}')]"

        return string

class State:
    """
    A set of partially completed grammar rules, representing a state in a partially parsed grammar.
    When a state is created, it is automatically closed to include all subsequent rules that can be reached from the current state.

    Attributes:
        items (OrderedSet): A set of StateItems representing the rules in the state.
    """

    def __init__(self, grammar: Grammar, *items: StateItem) -> None:
        self.items: OrderedSet[StateItem] = OrderedSet(items)
        self._grammar: Grammar = grammar


        # Create closure
        for item in list(self.items):
            if item.position < len(item.body):
                self._close_helper(item, [])


    def _close_helper(self, item: StateItem, visited: List[StateItem]) -> None:
        next_token = item.body[item.position]

        if next_token in self._grammar.terminals:
            return   
            
        follow_set = self._grammar.follow_sets[next_token]    

        for rule in self._grammar.get_rules_by_head(next_token):
            new_item = StateItem(rule, follow_set)
            self.items.add(new_item)

            if new_item not in visited:
                self._close_helper(new_item, visited+[new_item])    

    def get_transition_result(self, token: str) -> 'State':
        def shift_item(item: StateItem) -> StateItem:
            return StateItem(item, item.follow, item.position+1)
        
        items = [shift_item(item) for item in self.items
                 if (item.position < len(item.body)) and (item.body[item.position] == token)]
        
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


class ParseTable:
    """
    Represents a parse table for a given grammar.
    
    Attributes:
        states (list): A list of states in the parse table.
        state_ids (dict): A dictionary mapping states to their corresponding IDs.
        goto_table (dict): A dictionary representing the Goto table of the parse table.
        action_table (dict): A dictionary representing the Action table of the parse table.
        
    Methods:
        goto(state: int, token: str) -> int:
            * Returns the state to which the given state transitions on the given token.
        action(state: int, token: str) -> Tuple[str, ...]:
            * Returns the action and any additional arguments for the given state and token.
        __getitem__(key: Tuple[int, str]) -> Tuple[str, ...]: 
            * Returns the action and any additional arguments for the given state and token.            
            """

    def __init__(self, grammar: Grammar) -> None:
        self._grammar: Grammar = grammar

        self.states: List[State] = []
        self.state_ids: Dict[State, int] = {}
        
        self.goto_table: Dict[Tuple[int, str], int] = {} #(state, token) -> state
        self.action_table: Dict[Tuple[int, str], Tuple[str, ...]] = {} #(state, token) -> (action, *args)

        self._generate_table()

    def goto(self, state: int, token: str) -> int:
        return self.goto_table.get((state, token), -1)

    def action(self, state: int, token: str) -> Tuple[str, ...]:
        return self.action_table.get((state, token), ("err",))

    def _generate_table(self) -> None:
        # Make Start State
        start = self._grammar.start_symbol
        start_item = StateItem(
            self._grammar.get_rules_by_head(start)[0],
            self._grammar.follow_sets[start]
        )
        current_state = State(self._grammar, start_item)
        self.state_ids[current_state] = 0

        # Populate Goto Table
        stack = [current_state]
        i = 1
        while len(stack) > 0:
            current_state = stack.pop(0)
            self.states.append(current_state)

            for token in self._grammar.terminals.union(self._grammar.nonterminals):            
                new_state = current_state.get_transition_result(token)
                if len(new_state.items) == 0: continue
                
                if new_state not in self.state_ids.keys():
                    stack.append(new_state)
                    
                    self.state_ids[new_state] = i
                    i += 1

                self.goto_table[(self.state_ids[current_state], token)] = self.state_ids[new_state]

        # Populate Action Table
        for state, id in self.state_ids.items():
            for item in state.items:
                if item.position == len(item.body):
                    if item.head == self._grammar.start_symbol:
                        self.action_table[(id, "$")] = ("acc",)
                    else:
                        for follow in item.follow:
                            self.action_table[(id, follow)] = ("red", item.head, len(item.body))

                elif (id, item.body[item.position]) in self.goto_table.keys():
                    self.action_table[(id, item.body[item.position])] = ("shft", self.goto_table[(id, item.body[item.position])])

                else:
                    print(f"Error, no valid action for {item} in state {id}:{state}")
                    
    def __getitem__(self, key: Tuple[int, str]) -> Tuple[str, ...]:
        return self.action_table.get(key, ("err",))


    def __str__(self) -> str:
        string = ""

        string += "States:\n"
        for state, id in self.state_ids.items():
            print(f"State {id}:{state}\n")
        

        string += "\nAction Table:\n"
        spacing = 15

        string += " "*5 + "│"
        for token in self._grammar.terminals:
            string += f"{token:^{spacing}}"


        string += "\n" + "─"*5 + "┼" +  "─"*(spacing*len(self._grammar.terminals) )


        for state, id in self.state_ids.items():
            string += f"\n{id:>4} │"
            
            for token in self._grammar.terminals:
                action = self.action_table.get((id, token), ("",))
                action = " ".join(map(str, action))
                string += f"{action:^{spacing}}"
            
        string += "\n" +  "="*200 + "\n"

        string += "\n\nGoto Table:\n"
        spacing = 8

        string += " "*5 + "│"
        for token in list(self._grammar.terminals) + list(self._grammar.nonterminals):
            string += f"{token:^{len(token)+4}}"


        string += "\n" + "─"*5 + "┼" +  "─"*(spacing*len(self._grammar.terminals) )

        for state, id in self.state_ids.items():
            string += f"\n{id:>4} │"
            
            for token in list(self._grammar.terminals) + list(self._grammar.nonterminals):
                new_state = self.goto_table.get((id, token), "")
                string += f"{new_state:^{len(token)+4}}"

        return string