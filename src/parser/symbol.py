class _SymbolMeta(type):
    def __new__(cls, name, bases, attrs):
        Symbol = super().__new__(cls, name, bases, attrs)
        
        Symbol.epsilon = Symbol("ε", True, _special_type="epsilon")
        Symbol.eof = Symbol("$", True, _special_type="eof")
        
        return Symbol

class Symbol(metaclass=_SymbolMeta):
    """A symbol in the syntax description used by the tokenizer and grammar."""

    epsilon:'Symbol' = None# Filled in by metaclass
    eof:'Symbol' = None

    instances = {}

    # Improve size and speed with slots
    # __slots__ = ("identifier", "terminal", "_special_type", "_frozen")

    def __new__(cls, identifier:str, terminal:bool, *, _special_type:str=""):
        # Check if the symbol already exists
        if identifier in cls.instances:
            cached = cls.instances[identifier]
            if terminal != cached.terminal:
                raise ValueError(f"Cached symbol doesn't match terminal state. {identifier}:{cached.terminal}!={terminal}")
            return cached
        
        # Create a new instance
        instance = super().__new__(cls)
        cls.instances[identifier] = instance
        return instance

    def __init__(self, identifier:str, terminal:bool, *, _special_type:str=""):
        self._frozen = False

        self.identifier:str = identifier
        self.terminal:bool = terminal

        self._special_type:str = _special_type
        self._frozen = True



    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return NotImplemented

        return self.identifier == other.identifier \
            and self.terminal == other.terminal \
            and self._special_type == other._special_type
    
    def __setattr__(self, name, value):
        # Make symbols immutable
        if hasattr(self, "_forzen") and self._frozen:
            raise AttributeError("This symbol is immutable.")
        else:
            super().__setattr__(name, value)

    def __hash__(self):
        return hash(self.identifier) ^ hash(self.terminal) ^ hash(self._special_type)
    
    def __str__(self):
            return f"<{self.identifier}>"

    def __repr__(self):
        if self._special_type != "":
            return f"Symbol({self._special_type})"
        else:
            return f"Symbol({self.identifier!r}, {'terminal' if self.terminal else 'non-terminal'})"
