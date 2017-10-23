
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

gboard = None

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    current = node
    current_state = state

    finished = False

    # Loop through nodes in tree
    while not finished:
        # If there are untried actions or the game has ended we need to quit the loop
        if current.untried_actions != []:
            finished = True
        elif board.is_ended(current_state):
             finished = True
        else:
            # Otherwise we descend through the tree
            best_UCT = 0
            best_child = None
            children = current.child_nodes

            for key, child in children.items():
                ratio = child.wins / child.visits
                child_UCT = (ratio if board.current_player(current_state) == identity else 1 - ratio) + explore_faction * sqrt(log(current.visits / child.visits))
                if child_UCT > best_UCT:
                    best_UCT = child_UCT
                    best_child = child

            current = best_child
            current_state = board.next_state(current_state, best_child.parent_action)
    #print(current)
    return current, current_state


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """
    """
    available_actions = node.untried_actions
    chosen_action = get_winning_action(available_actions)

    if chosen_action != None:
        losing_actions = get_losing_actions(available_actions)
        try:
            chosen_action = random.choice(list(set(available_actions) - set(losing_actions)))
        except IndexError:
            chosen_action = random.choice(losing_actions)
    """

    chosen_action = choice(node.untried_actions)

    node.untried_actions.remove(chosen_action)

    return MCTSNode(parent=node, parent_action=chosen_action, action_list=board.legal_actions(board.next_state(state,chosen_action)))

def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    Returns:    True if player won, False otherwise

    """
    identity = 1 if board.current_player(state) == 2 else 2
    current_state = state

    # Play until end (win/lose)
    while not board.is_ended(current_state):
        move = choice(board.legal_actions(current_state))
        current_state = board.next_state(current_state, move)

    if identity != board.current_player(current_state):
        # Won
        won = True
    else:
        # Lost
        won = False

    return won

def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    temp = node
    while True:
        node.wins += 1 if won else 0
        node.visits += 1
        node = node.parent
        
        if node == None:
            break


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        leaf, new_state = traverse_nodes(node, board, sampled_game, identity_of_bot)
        if leaf.untried_actions != []:
            child = expand_leaf(leaf, board, new_state)
            leaf.child_nodes[child.parent_action] = child
            won = rollout(board, board.next_state(new_state, child.parent_action))
            backpropagate(child, won)
            
    best_child = None
    best_ratio = 0

    # print("N. first children: {}".format(len(root_node.child_nodes)))

    for key, child in root_node.child_nodes.items():
        ratio = child.wins/child.visits
        # print("- Child [{}] ratio: {}".format(child.parent_action, ratio))
        if ratio >= best_ratio:
            best_child = child
            best_ratio = ratio

    print("MCTS vanilla picking {} with ratio {}".format(best_child.parent_action, best_ratio))
    return best_child.parent_action
