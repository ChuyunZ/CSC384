#   Look for #IMPLEMENT tags in this file. These tags indicate what has
#   to be implemented to complete the warehouse domain.

#   You may add only standard python imports
#   You may not remove any imports.
#   You may not import or otherwise source any of your own files

import os  # for time functions
import math  # for infinity
from search import *  # for search engines
from sokoban import sokoban_goal_state, SokobanState, Direction, PROBLEMS  # for Sokoban specific classes and problems

# SOKOBAN HEURISTICS
def heur_alternate(state):
    # IMPLEMENT
    '''a better heuristic'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # heur_manhattan_distance has flaws.
    # Write a heuristic function that improves upon heur_manhattan_distance to estimate distance between the current state and the goal.
    # Your function should return a numeric value for the estimate of the distance to the goal.
    # EXPLAIN YOUR HEURISTIC IN THE COMMENTS. Please leave this function (and your explanation) at the top of your solution file, to facilitate marking.

    # Steps for calculating heuristic:
    # Determine unsolvable states in which we return infinity:
    # 1. If the number of storages is less than that of boxes
    # 2. If there are boxes in the corner but there is no storage at that corner
    # 3. If a box is blocked in either up and left, or up and right, or down and left, or down and right directions or more
    # 4. If a box is along the wall, and there is an immediate box or obstacle on the same direction of the wall that is beside the box
    # 5. If two boxes are immediate beside each other, and there are at least two obstacles blocking each of them on the longer side
    # 6. The number of storages on a side of the wall is less than the number of boxes on that side of the wall

    # Next, check if there are any immediate surrounding boxes (in the up, down, left, right) directions, if so, add the number of them to
    # the heuristic value for penalty (i.e. they might cause re-routing which costs more steps and time, or leading to unsolvable state)

    # Finally, calculate the shortest distances between each box and the storage where each storage can only be occupied once, 
    # also calculate the shortest distances between each box and the robot, add these two numbers to the heuristic value.
    # Additional to this, also add the number of obstacles that is within the area enclosed by the box and the storage, and enclosed
    # by the box and the robot, each obstacle adds 1 to the heuristic value.
    
    # Check the number of storages and the boxes before executing
    if (len(state.storage) < len(state.boxes)):
        return math.inf

    # Find the coordinates of the walls and obstacles to cover the case where the box is next to the wall
    walls = set()
    for width in range(state.width):
        walls.add((width, -1))
        walls.add((width, state.height))
    for height in range(state.height):
        walls.add((-1, height))
        walls.add((state.width, height))

    # combine all the blocked ocrrdinates
    obstacle_and_wall = state.obstacles.union(walls)
    # Initialize manhatten distance 
    res = 0

    box_on_wall_up_wall = set()
    box_on_wall_down_wall = set()
    box_on_wall_left_wall = set()
    box_on_wall_right_wall = set()
    

    # coordinates for corners
    corners_for_box = [(0, 0), (0, state.height - 1), (state.width - 1, 0), (state.width - 1, state.height - 1)]

    for box in state.boxes:
        if box not in state.storage:
            # Base case: if box is in the corner, then the state is unsolvable. Return a heuristic of infinity
            if box in corners_for_box:
                return math.inf

            # Find the positions for moving the box in the four basic directions 
            up_pos = (box[0], box[1] - 1) 
            up_pos_bool = up_pos in obstacle_and_wall 
            down_pos = (box[0], box[1] + 1)
            down_pos_bool = down_pos in obstacle_and_wall 
            left_pos = (box[0] - 1, box[1])
            left_pos_bool = left_pos in obstacle_and_wall 
            right_pos = (box[0] + 1, box[1])
            right_pos_bool = right_pos in obstacle_and_wall 

            # If a box is blocked in two or more directions by obstacles or walls, then it is blocked, so the state is unsolvable
            if (up_pos_bool and (left_pos_bool or right_pos_bool)) or (down_pos_bool and (left_pos_bool or right_pos_bool)):
                return math.inf
            
            # If a box is blocked by an obstacle in the y direction with the same x coordinate, then if there is a horizontal neighbour box and is also blocked
            # in any of its y direction, then the state is unsolvable
            if (up_pos_bool or down_pos_bool) and ((left_pos in state.boxes and ((left_pos[0], left_pos[1] + 1) in obstacle_and_wall or (left_pos[0], left_pos[1] - 1) in obstacle_and_wall)) or (right_pos in state.boxes and ((right_pos[0], right_pos[1] + 1) in obstacle_and_wall or (right_pos[0], right_pos[1] - 1) in obstacle_and_wall))):
                return math.inf
            # If a box is blocked by an obstacle in the x direction with the same y coordinate, then if there is a horizontal neighbour box and is also blocked
            # in any of its y direction, then the state is unsolvable
            if (left_pos_bool or right_pos_bool) and ((up_pos in state.boxes and ((up_pos[0] - 1, up_pos[1]) in obstacle_and_wall or (up_pos[0] + 1, up_pos[1]) in obstacle_and_wall)) or (down_pos in state.boxes and ((down_pos[0] - 1, down_pos[1]) in obstacle_and_wall or (down_pos[0] + 1, down_pos[1]) in obstacle_and_wall))):
                return math.inf
            
            # If box is on the left/right wall and there is a consecutive box or obstacle below or above it, the the state is unsolvable
            if box[0] == 0:
                if (box[0], box[1] + 1) in state.boxes or (box[0], box[1] - 1) in state.boxes or (box[0], box[1] + 1) in state.obstacles or (box[0], box[1] - 1) in state.obstacles:
                    return math.inf
                else:
                    box_on_wall_left_wall.add(box)
            
            if box[0] == state.width - 1:
                if (box[0], box[1] + 1) in state.boxes or (box[0], box[1] - 1) in state.boxes or (box[0], box[1] + 1) in state.obstacles or (box[0], box[1] - 1) in state.obstacles:
                    return math.inf
                else:
                    box_on_wall_right_wall.add(box)
            
            # If box is on the up/down wall and there is a consecutive box below or above it, the the state is unsolvable
            if box[1] == 0:
                if (box[0] + 1, box[1]) in state.boxes or (box[0] - 1, box[1]) in state.boxes or (box[0] + 1, box[1]) in state.obstacles or (box[0] - 1, box[1]) in state.obstacles:
                    return math.inf
                else:
                    box_on_wall_up_wall.add(box)

            if box[1] == state.height - 1:
                if (box[0] + 1, box[1]) in state.boxes or (box[0] - 1, box[1]) in state.boxes or (box[0] + 1, box[1]) in state.obstacles or (box[0] - 1, box[1]) in state.obstacles:
                    return math.inf
                else:
                    box_on_wall_down_wall.add(box)
            
            # penalize for crowded boxes as it might increase the number of pushes
            else:
                res += len(set((up_pos, down_pos, left_pos, right_pos)).intersection(state.boxes))

            
            
    # Collect the x and y positions to see if there are sufficient storages on wall sides for the boxes on the wall sides.
    storage_on_wall_up_wall = set()
    storage_on_wall_down_wall = set()
    storage_on_wall_left_wall = set()
    storage_on_wall_right_wall = set()

    storage_notassigned = set()

    # Find storages that are on the wall, if the number of storages < number of boxes on the side of the wall, then the state is unsolvable
    for storage in state.storage:
        if storage not in state.boxes:
            if storage[0] == 0:
                storage_on_wall_left_wall.add(storage)
            if storage[0] == state.width - 1:
                storage_on_wall_right_wall.add(storage)
            if storage[1] == 0:
                storage_on_wall_up_wall.add(storage)
            if storage[1] == state.height - 1:
                storage_on_wall_down_wall.add(storage)
            storage_notassigned.add(storage)

    if len(storage_on_wall_left_wall) < len(box_on_wall_left_wall) or len(storage_on_wall_right_wall) < len(box_on_wall_right_wall) or len(storage_on_wall_up_wall) < len(box_on_wall_up_wall) or len(storage_on_wall_down_wall) < len(box_on_wall_down_wall):
        return math.inf
    

    # Find the minimum distances between boxes and storages and add it to res, each storage can only be pushed to once
    for box in state.boxes:
        if box not in state.storage:
            min_distance = math.inf
            current_used_storage = None
            for storage in storage_notassigned:
                dist = abs(box[0] - storage[0]) + abs(box[1] - storage[1])
                if dist < min_distance:
                    current_used_storage = storage
                    min_distance = dist
            storage_notassigned.remove(current_used_storage)
            res += min_distance + obstacle_in_between(box, current_used_storage, state.obstacles)

    # Find the minimum distances between boxes and robots and add it to res
    for box in state.boxes:
        if box not in state.storage:
            min_distance = math.inf
            best_robot = None
            for robot in state.robots:
                dist = abs(robot[0]-box[0]) + abs(robot[1]-box[1])
                min_distance = min(dist, min_distance)
                best_robot = robot
            res += min_distance + obstacle_in_between(best_robot, box, state.obstacles)

    return res
            

def obstacle_in_between(box, storage, obstacle):
    '''Calculate the distance between the box and the storage by adding the number of obstacles in between'''
    res = 0
    (up, low) = (min(box[1], storage[1]), max(box[1], storage[1]))
    (left, right) = (min(box[0], storage[0]), max(box[0], storage[0]))
    
    for obs in obstacle:
        if (left <= obs[0]) and (obs[0] <= right) and (up <= obs[1]) and (obs[1] <= low):
            res += 1
    return res


def heur_zero(state):
    '''Zero Heuristic can be used to make A* search perform uniform cost search'''
    return 0

def heur_manhattan_distance(state):
    # IMPLEMENT
    '''admissible sokoban puzzle heuristic: manhattan distance'''
    '''INPUT: a sokoban state'''
    '''OUTPUT: a numeric value that serves as an estimate of the distance of the state to the goal.'''
    # We want an admissible heuristic, which is an optimistic heuristic.
    # It must never overestimate the cost to get from the current state to the goal.
    # The sum of the Manhattan distances between each box that has yet to be stored and the storage point nearest to it is such a heuristic.
    # When calculating distances, assume there are no obstacles on the grid.
    # You should implement this heuristic function exactly, even if it is tempting to improve it.
    # Your function should return a numeric value; this is the estimate of the distance to the goal.
    val = 0
    for box in state.boxes:
        if box not in state.storage:
            dist = []
            for s in state.storage:
                dist.append(abs(box[0] - s[0]) + abs(box[1] - s[1]))
            val += min(dist)
    return val
          

def fval_function(sN, weight):
    # IMPLEMENT
    """
    Provide a custom formula for f-value computation for Anytime Weighted A star.
    Returns the fval of the state contained in the sNode.

    @param sNode sN: A search node (containing a SokobanState)
    @param float weight: Weight given by Anytime Weighted A star
    @rtype: float
    """
    return sN.gval + weight * sN.hval

# SEARCH ALGORITHMS
def weighted_astar(initial_state, heur_fn, weight, timebound):
    # IMPLEMENT    
    '''Provides an implementation of weighted a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of weighted astar algorithm'''
    se = SearchEngine('custom', 'full')
    wrapped_fval_function = (lambda sN: fval_function(sN, weight))     
    se.init_search(initial_state, sokoban_goal_state, heur_fn, wrapped_fval_function)     
    final, stats = se.search(timebound)     
    return final, stats

def iterative_astar(initial_state, heur_fn, weight=1, timebound=5):  # uses f(n), see how autograder initializes a search line 88
    # IMPLEMENT
    '''Provides an implementation of realtime a-star, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False as well as a SearchStats object'''
    '''implementation of iterative astar algorithm'''
    start_time = os.times()[0]
    best_soln = None
    best_cost = float('inf')
    best_stats = None
    
    current_weight = weight
    
    while True:
        used_time = os.times()[0] - start_time
        remain = timebound - used_time
        if remain <= 0:
            break
        
        wrapped_fval = (lambda sN: fval_function(sN, current_weight))
        se = SearchEngine(strategy='custom', cc_level='full')
        se.init_search(initial_state, goal_fn=sokoban_goal_state, heur_fn=heur_fn, fval_function=wrapped_fval)

        costbound = (float('inf'), float('inf'), best_cost)

        result, stats = se.search(timebound=remain, costbound=costbound)

        if not result:
            break

        if result.gval < best_cost:
            best_soln = result
            best_cost = result.gval
            best_stats = stats

        current_weight = max(current_weight * 0.6, 1)
        # current_weight *= 0.6

    return best_soln, best_stats

def iterative_gbfs(initial_state, heur_fn, timebound=5):  # only use h(n)
    # IMPLEMENT
    '''Provides an implementation of anytime greedy best-first search, as described in the HW1 handout'''
    '''INPUT: a sokoban state that represents the start state and a timebound (number of seconds)'''
    '''OUTPUT: A goal state (if a goal is found), else False'''
    '''implementation of iterative gbfs algorithm'''
    start_time = os.times()[0]
    best_soln = None
    best_cost = float('inf')
    best_stats = None

    while True:
        used_time = os.times()[0] - start_time
        remain = timebound - used_time
        if remain <= 0:
            break

        se = SearchEngine(strategy='best_first', cc_level='full')
        se.init_search(initial_state,  goal_fn=sokoban_goal_state, heur_fn=heur_fn)

        costbound = (best_cost, float('inf'), float('inf'))

        result, stats = se.search(timebound=remain, costbound=costbound)
        if not result:
            break

        if result.gval < best_cost:
            best_soln = result
            best_cost = result.gval
            best_stats = stats

    return best_soln, best_stats