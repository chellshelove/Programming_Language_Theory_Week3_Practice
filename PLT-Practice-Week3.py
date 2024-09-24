import re
from functools import lru_cache

def parser(syntax, str_input):
    grammar = {}
    non_terminal_pattern = re.compile(r'<([^<>]+)>')

    for rule in syntax:
        try:
            lhs, rhs = rule.split('::=')
        except ValueError:
            raise ValueError(f"Invalid rule format: '{rule}'. Expected '::=' separator.")
        
        lhs_match = non_terminal_pattern.match(lhs.strip())
        if not lhs_match:
            raise ValueError(f"Invalid non-terminal in rule: '{lhs}'.")
        lhs = lhs_match.group(1)

        # Split the RHS into productions separated by '|'
        productions = rhs.split('|')
        grammar[lhs] = []
        for prod in productions:
            symbols = []
            for token in prod.strip().split():
                token_match = non_terminal_pattern.match(token)
                if token_match:
                    symbols.append(token_match.group(1))  # Non-terminal without <>
                else:
                    symbols.append(token)  # Terminal symbol
            grammar[lhs].append(symbols)

    # This regex matches words (\w+) or specific operators (=, +, -)
    token_pattern = re.compile(r'\w+|[=+-]')
    tokens = token_pattern.findall(str_input)

    @lru_cache(maxsize=None)
    def parse(symbol, pos):
        if pos > len(tokens):
            return []

        if symbol not in grammar:
            if pos < len(tokens) and tokens[pos] == symbol:
                return [pos + 1]
            else:
                return []
        else:
            possible_positions = []
            for production in grammar[symbol]:
                current_positions = [pos]  # Start with the current position
                for sym in production:
                    new_positions = []
                    for cp in current_positions:
                        res = parse(sym, cp)
                        new_positions.extend(res)
                    current_positions = new_positions  # Update positions after parsing sym
                    if not current_positions:
                        break  # This production failed; try the next one
                possible_positions.extend(current_positions)
            return possible_positions

    start_symbol = list(grammar.keys())[0]
    final_positions = parse(start_symbol, 0)

    if len(tokens) in final_positions:
        print('Parse OK!')
    else:
        print('Parse Failed!')

if __name__ == "__main__":
    
    # Updated syntax
    syntax = [
        '<Assign> ::= <Name> = <BinOp> | <Name> = <Name> | <Name>, <Name> = <Constant>, <Constant> | <Name> = <Constant> <BinOp> <Constant>',
        '<BinOp> ::= <Name> <Add> <Constant> | <Name> <Sub> <Constant> | <Constant> <Add> <Name> | <Constant> <Sub> <Name> | <Constant> <Sub> <Constant>',
        '<Constant> ::= 3 | 4 | 5 | 1',
        '<Name> ::= a | b | x | y | c',
        '<Add> ::= +',
        '<Sub> ::= -'
    ]

    str_inputs = [
        'a = 3 + b',
        'x = y',
        'a = b + 5',
        'a, b = 3, 5',
        'c = 4 - 1'  
    ]
    
    for str_input in str_inputs:
        parser(syntax, str_input)
