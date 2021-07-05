from config import Names


class State:
    """
    Node class for a state
    """
    def __init__(self, key, state, next=None, prev=None):
        """
        Node that describes a state
        :param key: state key
        :param state: state name
        :param next: node of next state alphabetically
        :param prev: node of previous state alphabetically
        """
        self.key = key
        self.state = state
        self.next = next
        self.prev = prev


def get_states_linked_list():
    """
    Method that creates a circular linked list to add to the carousel
    :return: dict - {State Name: Node as defined in State with prev and next pointers}
    """
    n = len(Names.state_names) - 1
    state_nodes = []
    for i, k in enumerate(Names.state_names):
        if k != "un":
            state_nodes.append(State(k, Names.state_names[k]))

    for i, state in enumerate(state_nodes):
        if i == 0:
            # Condition for first state to access last state when clicked on previous
            state.prev = state_nodes[-1]
        else:
            state.prev = state_nodes[i - 1]
        if i == n - 1:
            # Condition for last state to click on first state when clicked on next
            state.next = state_nodes[0]
        else:
            state.next = state_nodes[i + 1]
    state_nodes_dict = {state.state: state for state in state_nodes}
    return state_nodes_dict
