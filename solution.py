assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

#Definition of the diagonal units used to solve the Diagonal Sudoku
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9', ], ['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1', ]]

unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Method to set values for the PyGame visualization
    Args:
        values(dict): dictionary of values
        box: key of the value in the dictionary you want to set
        value: value you want to set in the values[box]

    Returns:
        The updated values (dict)
    """
    
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def check_naked_twins_in_units(values, unitlist):
    """Check for naked twins in a give list of units and modify the values(dict) when Naked Twins are found
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
        unitlist(list): a list of the units where to look for the Naked Twins

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        for box in unit:
            #If the box contains just two digits it's a potential Naked Twin
            if(len(values[box]) == 2):
                #Fill a list of all the boxes in the unit with the same value of the box we are considering
                places = [place for place in unit if values[place] == values[box] and place != box]
                #If there's just one box that contains the same identical two digits of the box we are taking into account we
                #have found the Naked Twins
                if (len(places) == 1):
                    #For each digit in the Naked Twin, delete that digit in the other boxes in the same unit 
                    for digit in values[box]:
                        for changeBox in unit:
                            #Delete the digit only in the other boxes of the same Unit of the Naked Twins
                            if (changeBox != box and changeBox != places[0]):
                                assign_value(values, changeBox, values[changeBox].replace(digit, ''))
                                
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    
    #Find Naked Twins in the Rows
    values = check_naked_twins_in_units(values, row_units)
    
    #Find Naked Twins in the columns
    values = check_naked_twins_in_units(values, column_units)
    
    #Find Naked Twins in the squares
    values = check_naked_twins_in_units(values, square_units)
    
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    
    #For each element in the Grid replace the character with the digits '123456789' if the char is a '.'
    for c in grid:
        #The char is a digit, so leave it as it is
        if c in digits:
            chars.append(c)
        #The char is a '.', so replace it with a string '123456789'
        if c == '.':
            chars.append(digits)
    #Verify that the chars (list) contains 81 items
    assert len(chars) == 81
    #Return a dictionary with the "boxes" as keys and the char items as values
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Eliminates the digits in each peer of an already solved box
    Args:
        values(dict): The sudoku in dictionary form
    """
    #Create a list of all the solved boxes
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    
    for box in solved_values:
        digit = values[box]
        #Iterate on each peer and delete the digit of the solved box if present
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit, ''))
    return values

def only_choice(values):
    """
    Set a box to a certain digit if that box is the only one, among all its peers, that contains that digit
    Args:
        values(dict): The sudoku in dictionary form
    """
    for unit in unitlist:
        for digit in '123456789':
            #Fill a list of boxes in the unit the digit belongs to
            dplaces = [box for box in unit if digit in values[box]]
            #If there's just one box in the list we can consider that box as solved and set its value to that digit
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit)
    return values

def reduce_puzzle(values):
    """
    Apply the constraints to reduce the puzzle (reduce the domains of the variables)
    Args:
        values(dict): The sudoku in dictionary form
    """
    #Put up a list of all the solved boxes
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    #Init the puzzle solution process as "not stalled"
    stalled = False
    
    #Keep applying the constraints until there are no progress towards a solution
    while not stalled:
        
        #Keep track of the number of solved boxes before applying the constraints
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        
        #Apply the Constraints Eliminate, Only Choice and Naked Twins
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        
        #Check how many solved boxes there are in the grid after applying the constraints
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        
        #If the number of solved boxes have not been increased after applying the constraints, we can't make progress
        stalled = solved_values_before == solved_values_after
        
        #Return False if a box has no digits
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
        
    return values

def search(values):
    """
    Search all the possible solutions applying the Depth First Search algorithm
    Args:
        values(dict): The sudoku in dictionary form
    """
    #Try reducing the puzzle
    values = reduce_puzzle(values)
    
    #Exit Conditions
    #Check if the reduce_puzzle() ran into issues
    if values is False:
        return False ## Failed earlier
    #Check if all the boxes have been solved (contain just one digit)
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus
    for value in values[s]:
        #Make a copy of the sudoku to work with a new one
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    #Create a Dictionary of all the values with the given grid(string)
    values = grid_values(grid)
    #Apply the Depth First Search to solve the Sudoku
    values = search(values)
    return values
    

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
