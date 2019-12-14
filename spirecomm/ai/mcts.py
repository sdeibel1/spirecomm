import math
import operator
# from spirecomm.ai.combatSim import CombatSim


def backpropagate(node, result):
    """Backpropagates a result of a simulation up the tree."""
    n = node
    while n:
        n.increment(result)
        n = n.parent


class MCTS:
    def __init__(self, sim, combat_state):
        self.sim = sim
        root = Tree(combat_state)

    def get_action(self, n=100):
        """Returns the best action after running n rounds of MCTS."""
        self.build_tree(n)
        best = max(self.root.children, key=operator.attrgetter("value"))
        return best.card, best.target

    def build_tree(self, n):
        """Runs the process of selection, expansion, rollout, backpropagation n times."""
        for i in range(n):
            node_to_expand = self.select()
            rollout_node = self.expand(node_to_expand)
            result = self.rollout(rollout_node)
            backpropagate(rollout_node, result)

    # node is the root node at which we start, recursively goes down and selects
    def select(self, node):
        """Recursively selects a node for expansion."""
        if node.fully_expanded():
            max_child = max(node.children, key=operator.attrgetter("value"))
            return self.select(max_child)
        else:
            return node

    def expand(self, node):
        """Adds a node to the tree if the node for expansion is not fully expanded.
        Otherwise, returns the node for expansion.

        Args:
            node -- the node to expand.

        Returns:
            Tree. the node to be simulated next.
        """
        self.sim.change_state(node.state)
        self.sim.play(node.card, node.target)
        if self.sim.is_over():
            return node
        else:
            expanded = {(n.card, n.target) for n in node.children}
            possible = node.get_possible_actions()
            action_to_expand = (possible - expanded).sample(1)
            child = Tree(self.sim.get_state(), action_to_expand)
            node.add_child(child)
            return child

    def rollout(self, node):
        self.sim.change_state(node.state)
        result = self.sim.sim_combat(node.card, node.target)
        return result


class Tree:
    def __init__(self, state, card=None, target=None):
        self.state = state
        self.action = (card, target)
        self.children = []
        self.parent = None
        self.wins = 0
        self.total = 0
        self.value = 0

    def add_child(self, node, result):
        self.children.append(node)
        node.parent = self

    def increment(self, result):
        self.wins += result
        self.total += 1
        self.value = self.calc_value()

    def calc_value(self):
        ave_reward = self.wins/self.total
        parent_sims = self.parent.total

        return ave_reward + math.sqrt(2)*(math.sqrt(math.log(parent_sims)/self.total))

    def fully_expanded(self):
        expanded = {(n.card, n.target) for n in self.children}
        possible = self.get_possible_actions()

        return False if (possible - expanded) else True

    def get_possible_actions(self):
        actions = set()
        for c in self.state['hand']:
            if c.has_target:
                for t in self.state['monsters']:
                    actions.add((c, t))
            else:
                actions.add((c, self.state['player']))
        return actions
