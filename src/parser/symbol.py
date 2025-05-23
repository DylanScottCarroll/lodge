class Symbol():
    """A symbol in the syntax description used by the tokenizer and grammar."""

    epsilon:'Symbol' # Filled in by metaclass
    eof:'Symbol'

    instances = {}

    def __new__(cls, identifier:str|None=None, terminal:bool=True):
        # Check if the symbol already exists
        if identifier in cls.instances:
            cached = cls.instances[identifier]
            if terminal != cached.terminal:
                raise ValueError(f"Cached symbol doesn't match terminal state. {identifier}:{cached.terminal}!={terminal}")
            return cached
        
        # Create a new instance
        instance = super().__new__(cls)
        
        if identifier is not None:
            cls.instances[identifier] = instance
        
        return instance

    def __init__(self, identifier:str, terminal:bool=True):
        self._frozen = False

        self.identifier:str = identifier
        self.terminal:bool = terminal

        self._frozen = True


    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return NotImplemented

        return self.identifier == other.identifier \
            and self.terminal == other.terminal
    
    def __setattr__(self, name, value):
        # Make symbols immutable
        if hasattr(self, "_forzen") and self._frozen:
            raise AttributeError("This symbol is immutable.")
        else:
            super().__setattr__(name, value)

    def __hash__(self):
        return hash(self.identifier) ^ hash(self.terminal)
    
    def __str__(self):
            return f"{self.identifier}"

    def __repr__(self):
        return f"Symbol({self.identifier!r}, {'terminal' if self.terminal else 'non-terminal'})"

Symbol.epsilon = Symbol("ε")
Symbol.eof = Symbol("$")
