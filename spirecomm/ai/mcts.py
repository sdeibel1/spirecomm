import copy
import math
import operator
import random


def backpropagate(node, result):
    """Backpropagates a result of a simulation up the tree."""
    n = node
    while n:
        n.increment(result)
        n = n.parent


class MCTS:
    def __init__(self, sim):
        self.sim = sim
        self.root = Tree(sim.get_state())
        self.num = 0
        # print("INITIALIZE MCTS")
        # print("root player hp: {0}, root monster hp: {1}".format(self.root.state["player"].current_hp, self.root.state["monsters"][0].current_hp))

    def change_state(self, state):
        self.root = Tree(state)

    def get_action(self, n=200):
        """Returns the best action after running n rounds of MCTS."""
        self.build_tree(n)
        self.sim.change_state(self.root.state)
        best = max(self.root.children, key=operator.attrgetter("value"))

        # print("wins:", best.wins, "total:", best.total)
        # print("Best card: {0}, best target: {1}".format(best.card.name, best.target))

        return best.card, best.target


    def build_tree(self, n):
        """Runs the process of selection, expansion, rollout, backpropagation n times."""
        for i in range(n):
            # print(self.root.state["player"].current_hp, self.root.state["monsters"][0].current_hp)
            node_to_expand = self.select(self.root)
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
            node -- the node for expansion.

        Returns:
            Tree. the node to be simulated next.
        """
        self.sim.change_state(node.state)
        if node.card is not None:
            self.sim.play(node.card, node.target)
        if node.fully_expanded():
            return node
        else:
            expanded = {(n.card, n.target) for n in node.children}
            possible = node.get_possible_actions()
            action_to_expand = random.sample((possible - expanded), 1)[0]
            # print(action_to_expand)
            child = Tree(self.sim.get_state(), action=action_to_expand)
            node.add_child(child)
            # print("else", child)
            return child

    def rollout(self, node):
        self.sim.change_state(node.state)
        # print(node.card)
        result = self.sim.sim_combat(node.card, node.target)
        return result


class Tree:
    def __init__(self, state, action=(None, None)):
        self.state = copy.deepcopy(state)
        if action[0] is not None:
            self.card = copy.deepcopy(action[0])
        else:
            self.card = action[0]
        self.target = action[1]
        # self.target = copy.deepcopy(action[1])
        self.children = []
        self.parent = None
        self.wins = 0
        self.total = 0
        self.value = 0

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def increment(self, result):
        self.wins += result
        self.total += 1
        if self.parent:
            self.value = self.calc_value()

    def calc_value(self):
        ave_reward = self.wins/self.total
        parent_sims = self.parent.total
        if parent_sims == 0:
            return 0
        return ave_reward + math.sqrt(2)*(math.sqrt(math.log(parent_sims)/self.total))

    def fully_expanded(self):
        expanded = {(n.card, n.target) for n in self.children}
        possible = self.get_possible_actions()

        return False if (possible - expanded) else True

    def get_possible_actions(self):
        actions = set()
        playable = [c for c in self.state['hand'] if self.state['player'].can_play(c)]
        for c in playable:
            if c.has_target:
                for i in range(len(self.state['monsters'])):
                    actions.add((c, i))
                # for t in self.state['monsters']:
                #     actions.add((c, t))
            else:
                actions.add((c, -1))
                # actions.add((c, self.state['player']))
        return actions
