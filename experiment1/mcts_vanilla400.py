
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 400
explore_faction = 2.

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

    # Loop through nodes in tree
    while not board.is_ended(current_state):
        # If there are untried actions we quit the loop
        if current.untried_actions != []:
            break
        else:
            # Otherwise we descend through the tree
            best_UCT = 0
            best_children = []

            for key, child in current.child_nodes.items():
                # Calculate UCT factor for child
                exploit_term = child.wins / float(child.visits)
                explore_term = explore_faction * sqrt(log(current.visits) / child.visits)

                child_UCT = (exploit_term if board.current_player(current_state) == identity else (1 - exploit_term)) + explore_term

                # Update best_children list
                if child_UCT == best_UCT:
                    best_children.append(child)
                elif child_UCT > best_UCT:
                    best_children = [child]
                    best_UCT = child_UCT

            current = choice(best_children)
            current_state = board.next_state(current_state, current.parent_action)

    # Return best_child/ending node
    return current, current_state


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        state:  The state of the game.

    Returns:    The added child node.

    """

    # Choose a random action from untried_actions
    chosen_action = choice(node.untried_actions)
    child = MCTSNode(parent=node, parent_action=chosen_action, action_list=board.legal_actions(board.next_state(state,chosen_action)))

    # Update node fields
    node.untried_actions.remove(chosen_action)
    node.child_nodes[chosen_action] = child

    return child

def rollout(board, state, identity):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        state:  The state of the game.

    Returns:    True if player won, False otherwise

    """
    current_state = state

    # Play until end (win/lose)
    while not board.is_ended(current_state):
        move = choice(board.legal_actions(current_state))
        current_state = board.next_state(current_state, move)

    # Return True if won, false otherwise
    return True if board.points_values(current_state)[identity] == 1 else False

def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    temp = node

    # Traverse up the tree and update node wins/visits
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

    # Initialize variables
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state

        # Start at root
        node = root_node

        # Traverse tree until leaf is reached, get new state
        leaf, new_state = traverse_nodes(node, board, sampled_game, identity_of_bot)

        # If the reached leaf is not a game ending state, expand the tree
        if not board.is_ended(new_state):
            child = expand_leaf(leaf, board, new_state)
            new_state = board.next_state(new_state, child.parent_action)
        else:
            child = leaf

        # Simulate possible outcome for leaf
        won = rollout(board, new_state, identity_of_bot)

        # Backpropogate simulation results
        backpropagate(child, won)

    best_UCT = 0
    best_children = []

    # Choose best child depending on UCT calculation
    for key, child in root_node.child_nodes.items():
        child_UCT = child.wins / float(child.visits)

        if child_UCT == best_UCT:
            best_children.append(child)
        elif child_UCT > best_UCT:
            best_children = [child]
            best_UCT = child_UCT

    best_child = choice(best_children)

    print("MCTS vanilla picking {} with ratio {}".format(best_child.parent_action, best_UCT))
    return best_child.parent_action
