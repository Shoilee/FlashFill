import itertools
from typing import List, Tuple, Union, Set
from functools import lru_cache
import re

# Define Token classes and other related enums


class Token:
    pass


class Special(Token):
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return f"'{self.value}'"


class TokenClass(Token):
    Alpha, Lower, Upper, Num, Space = range(5)

    def __init__(self, value):
        self.value = value

    def __str__(self):
        token_class_names = ["AlphaTok", "LowerTok", "UpperTok", "NumTok", "Space"]
        return token_class_names[self.value]


class OneOrMore(Token):
    def __init__(self, token_class: TokenClass):
        self.token_class = token_class

    def __str__(self):
        return f"{self.token_class}+"


class ExcludeOneOrMore(Token):
    def __init__(self, token_class: TokenClass):
        self.token_class = token_class

    def __str__(self):
        return f"Not({self.token_class}+)"


# Lazy initialization of tokens
@lru_cache(None)
def all_tokens():
    specials = ['/', '-', '(', ')', '.', ',']
    classes = [TokenClass.Alpha, TokenClass.Lower, TokenClass.Upper, TokenClass.Num, TokenClass.Space]
    tokens = [Special(s) for s in specials] + \
             [OneOrMore(c) for c in classes] + \
             [ExcludeOneOrMore(c) for c in classes]
    return tokens


# Regular expression class
class RegularExpr:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def concat(self, other):
        return RegularExpr(self.tokens + other.tokens)

    @staticmethod
    def empty():
        return RegularExpr([])

    def __str__(self):
        if not self.tokens:
            return 'e'
        return ', '.join(str(token) for token in self.tokens)


# Initialize all token sequences
@lru_cache(None)
def all_tokenseqs():
    all = [RegularExpr([token]) for token in all_tokens()]
    all.insert(0, RegularExpr.empty())
    return all


# Define other expression classes
class StringExpr:
    def __init__(self, exprs: List[Tuple['Bool', 'TraceExpr']]):
        self.exprs = exprs

    def __str__(self):
        if len(self.exprs) == 1:
            return str(self.exprs[0][1])
        return "Switch(" + ", ".join(f"{b}, {e}" for b, e in self.exprs) + ")"


class Bool:
    def __init__(self, conjuncts: List['Conjunct']):
        self.conjuncts = conjuncts

    def __str__(self):
        return "(" + " & ".join(str(conj) for conj in self.conjuncts) + ")"


class Conjunct:
    def __init__(self, predicates: List['Predicate']):
        self.predicates = predicates

    def __str__(self):
        return "(" + " | ".join(str(pred) for pred in self.predicates) + ")"


class Predicate:
    def __init__(self, is_match: bool, match: 'Match'):
        self.is_match = is_match
        self.match = match

    def __str__(self):
        return f"{'!' if not self.is_match else ''}{self.match}"


class Match:
    def __init__(self, v: int, r: RegularExpr, k: int):
        self.v = v
        self.r = r
        self.k = k

    def __str__(self):
        return f"(v{self.v + 1}, {self.r}, {self.k})"


class TraceExpr:
    def __init__(self, exprs: List['AtomicExpr']):
        self.exprs = exprs

    def __str__(self):
        return "Concat(" + ", ".join(str(expr) for expr in self.exprs) + ")"


class AtomicExpr:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def __str__(self):
        if self.kind == "SubStr":
            v, p1, p2 = self.value
            return f"SubStr({v}, {p1}, {p2})"
        elif self.kind == "ConstStr":
            return f"ConstStr({self.value})"
        elif self.kind == "Loop":
            return f"Loop(lambda w: {self.value})"


class Position:
    def __init__(self, kind: str, value):
        self.kind = kind
        self.value = value

    def __str__(self):
        if self.kind == "CPos":
            return f"CPos({self.value})"
        elif self.kind == "Pos":
            r1, r2, c = self.value
            return f"Pos({r1}, {r2}, {c})"


class IntegerExpr:
    def __init__(self, kind: str, value=None):
        self.kind = kind
        self.value = value

    def __str__(self):
        if self.kind == "Constant":
            return str(self.value)
        elif self.kind == "Bound":
            return "w"


# Example usage
if __name__ == "__main__":
    all_tokens()
    all_tokenseqs()
    print("Tokens and token sequences initialized.")
