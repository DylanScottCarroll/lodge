class OrderedSet:
    def __init__(self, iterable=None):
        self.data = {}
        if iterable:
            self.update(iterable)

    def add(self, element):
        self.data[element] = None

    def update(self, iterable):
        for element in iterable:
            self.add(element)

    def union(self, *sets):
        result = OrderedSet(self)
        for other_set in sets:
            result.update(other_set)
        return result

    def intersection(self, *sets):
        result = OrderedSet(self)
        for other_set in sets:
            result.data = {element: None for element in result.data if element in other_set}
        return result

    def difference(self, *sets):
        result = OrderedSet(self)
        for other_set in sets:
            result.data = {element: None for element in result.data if element not in other_set}
        return result

    def symmetric_difference(self, other_set):
        return self.union(other_set).difference(self.intersection(other_set))

    def discard(self, element):
        self.data.pop(element, None)

    def remove(self, element):
        if element not in self.data:
            raise KeyError(f"{element} not found in set")
        del self.data[element]

    def pop(self):
        if not self.data:
            raise KeyError("pop from an empty set")
        key, _ = self.data.popitem()
        return key

    def clear(self):
        self.data.clear()

    def copy(self):
        return OrderedSet(self)

    def issubset(self, other_set):
        return all(element in other_set for element in self)

    def issuperset(self, other_set):
        return all(element in self for element in other_set)

    def isdisjoint(self, other_set):
        return all(element not in self for element in other_set)

    def intersection_update(self, *sets):
        self.data = self.intersection(*sets).data

    def difference_update(self, *sets):
        self.data = self.difference(*sets).data

    def symmetric_difference_update(self, other_set):
        self.data = self.symmetric_difference(other_set).data

    def __len__(self):
        return len(self.data)

    def __contains__(self, element):
        return element in self.data

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f"OrderedSet({list(self.data)})"

    def __eq__(self, other):
        if not isinstance(other, OrderedSet):
            return NotImplemented
        return list(self.data) == list(other.data)

    def __le__(self, other_set):
        return self.issubset(other_set)

    def __lt__(self, other_set):
        return self.issubset(other_set) and len(self) < len(other_set)

    def __ge__(self, other_set):
        return self.issuperset(other_set)

    def __gt__(self, other_set):
        return self.issuperset(other_set) and len(self) > len(other_set)

    def __or__(self, other_set):
        return self.union(other_set)

    def __and__(self, other_set):
        return self.intersection(other_set)

    def __sub__(self, other_set):
        return self.difference(other_set)

    def __xor__(self, other_set):
        return self.symmetric_difference(other_set)

    def __ior__(self, other_set):
        self.update(other_set)
        return self

    def __iand__(self, other_set):
        self.intersection_update(other_set)
        return self

    def __isub__(self, other_set):
        self.difference_update(other_set)
        return self

    def __ixor__(self, other_set):
        self.symmetric_difference_update(other_set)
        return self
