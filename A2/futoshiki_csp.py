# Look for #IMPLEMENT tags in this file.
'''
All models need to return a CSP object, and a list of lists of Variable objects
representing the board. The returned list of lists is used to access the
solution.

For example, after these three lines of code

    csp, var_array = futoshiki_csp_model_1(board)
    solver = BT(csp)
    solver.bt_search(prop_FC, var_ord)

var_array[0][0].get_assigned_value() should be the correct value in the top left
cell of the Futoshiki puzzle.

1. futoshiki_csp_model_1 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only
      binary not-equal constraints for both the row and column constraints.

2. futoshiki_csp_model_2 (worth 20/100 marks)
    - A model of a Futoshiki grid built using only n-ary
      all-different constraints for both the row and column constraints.
    
    The input board is specified as a list of n lists. Each of the n lists
    represents a row of the board. If a 0 is in the list it represents an empty
    cell. Otherwise if a number between 1--n is in the list then this
    represents a pre-set board position.

    Each list is of length 2n-1, with each space on the board being separated
    by the potential inequality constraints. '>' denotes that the previous
    space must be bigger than the next space; '<' denotes that the previous
    space must be smaller than the next; '.' denotes that there is no
    inequality constraint.

    E.g., the board

    -------
    | > |2|
    | | | |
    | | < |
    -------
    would be represented by the list of lists

    [[0,>,0,.,2],
     [0,.,0,.,0],
     [0,.,0,<,0]]

'''
import cspbase
import itertools


def futoshiki_csp_model_1(futo_grid):
    # use assign() to assign the var with value
    # the domain for each var will always be the same    
    temp_grid = [[None for _ in range(len(futo_grid))] for _ in range(len(futo_grid))]
    cur_col = 0
    avail_domain = list(range(1, len(futo_grid) + 1))
    csp = cspbase.CSP("model1")

    for i in range(len(futo_grid)):
        for j in range(0, 2 * len(futo_grid) - 1, 2):
            if futo_grid[i][j] == 0:
                temp_grid[i][cur_col] = cspbase.Variable(f"X{i}Y{cur_col}", avail_domain)
            else:
                temp_grid[i][cur_col] = cspbase.Variable(f"X{i}Y{cur_col}", [futo_grid[i][j]])
            csp.add_var(temp_grid[i][cur_col])
            cur_col += 1
        cur_col = 0

    for i in range(len(temp_grid)):
        prune_row = temp_grid[i]
        prune_col = []
        for j in range(len(temp_grid)):
            prune_col.append(temp_grid[j][i])
        for j, k in itertools.combinations(prune_row, 2):
            constraint = cspbase.Constraint(f"Row_NotEqual_{j}_{k}", [j, k])
            satisfy = [(x, y) for x in j.domain() for y in k.domain() if x != y]
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)
        for j, k in itertools.combinations(prune_col, 2):
            constraint = cspbase.Constraint(f"Col_NotEqual_{j}_{k}", [j, k])
            satisfy = [(x, y) for x in j.domain() for y in k.domain() if x != y]
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)
    
    for i in range(len(futo_grid)):
        for j in range(1, len(futo_grid) * 2 - 1, 2):
            left = temp_grid[i][(j-1) // 2]
            right = temp_grid[i][(j+1) // 2]

            match futo_grid[i][j]:
                case '<':
                    constraint = cspbase.Constraint(f"{left}_Less_{right}", [left, right])
                    satisfy = [(x, y) for x in left.domain() for y in right.domain() if x < y]
                case '>':
                    constraint = cspbase.Constraint(f"{left}_Greater_{right}", [left, right])
                    satisfy = [(x, y) for x in left.domain() for y in right.domain() if x > y]
                case '.':
                    continue
            
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)

    return csp, temp_grid
  

def futoshiki_csp_model_2(futo_grid):
    # constraints : x1 != x2 != x3 != x4.....
    ##IMPLEMENT
    temp_grid = [[None for _ in range(len(futo_grid))] for _ in range(len(futo_grid))]
    cur_col = 0
    avail_domain = list(range(1, len(futo_grid) + 1))

    csp = cspbase.CSP("model2")

    for i in range(len(futo_grid)):
        for j in range(0, 2 * len(futo_grid) - 1, 2):
            if futo_grid[i][j] == 0:
                temp_grid[i][cur_col] = cspbase.Variable(f"X{i}Y{cur_col}", avail_domain)
            else:
                temp_grid[i][cur_col] = cspbase.Variable(f"X{i}Y{cur_col}", [futo_grid[i][j]])
            csp.add_var(temp_grid[i][cur_col])
            cur_col += 1
        cur_col = 0

    for i in range(len(temp_grid)):
        prune_row = temp_grid[i]
        prune_col = []
        for j in range(len(temp_grid)):
            prune_col.append(temp_grid[j][i])

        satisfy = get_satisfying_tuples(prune_row, len(temp_grid))
        if satisfy != None:
            constraint = cspbase.Constraint(f"Row_{i}_NotEqual", prune_row)
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)
        satisfy = get_satisfying_tuples(prune_col, len(temp_grid))
        if satisfy != None:
            constraint = cspbase.Constraint(f"Col_{i}_NotEqual", prune_col)
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)
            
    
    for i in range(len(futo_grid)):
        for j in range(1, len(futo_grid) * 2 - 1, 2):
            left = temp_grid[i][(j-1) // 2]
            right = temp_grid[i][(j+1) // 2]

            match futo_grid[i][j]:
                case '<':
                    constraint = cspbase.Constraint(f"{left}_Less_{right}", [left, right])
                    satisfy = [(x, y) for x in left.domain() for y in right.domain() if x < y]
                case '>':
                    constraint = cspbase.Constraint(f"{left}_Greater_{right}", [left, right])
                    satisfy = [(x, y) for x in left.domain() for y in right.domain() if x > y]
                case '.':
                    continue
            
            constraint.add_satisfying_tuples(satisfy)
            csp.add_constraint(constraint)

    return csp, temp_grid

def get_satisfying_tuples(prune_row, n):
    temp = list()
    domain_list = list()
    for e in prune_row:
        domain_list.append(e.domain())

    for p in itertools.product(*domain_list):
        if len(set(p)) == n:
            temp.append(p)
    return temp
    
        
