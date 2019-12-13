import math
import operator
from spirecomm.ai.combatSim import CombatSim


class MCTS:
    def __init__(self, combat_state):
        self.sim = CombatSim(combat_state)
        self.root_state = combat_state
        root = Tree(self.sim.get_state())
        self.nodes = []
        self.expand(root)


    def build_tree(self, n):
        for i in range(n):
            node_to_expand = self.select()
            rollout_node = self.expand(node_to_expand)
            result = self.rollout(rollout_node)
            self.backpropagate(rollout_node, result)



    def get_possible_actions(self, node):
        actions = set()
        sim = CombatSim(node.state)
        for c in sim.hand:
            if c.has_target:
                for t in sim.monsters:
                    actions.add((c, t))
            else:
                actions.add(c, sim.player)
        return actions

    # node is the root node at which we start, recursively goes down and selects
    def select(self, node):
        if self.fully_expanded(node):
            max_child = max(node.children, key=operator.attrgetter("value"))
            return self.select(max_child)
        else:
            return node

    def fully_expanded(self, node):
        expanded = {(n.card, n.target) for n in node.children}
        possible = self.get_possible_actions(node)

        return False if (possible - expanded) else True

    def rollout(self, node):
        self.sim.change_state(node.state)
        result = self.sim.sim_combat(node.card, node.target)



    def expand(self, node):
        sim = CombatSim(node.state)
        sim.play(node.card, node.target)
        if sim.is_over():
            return node
        else:
            expanded = {(n.card, n.target) for n in node.children}
            possible = self.get_possible_actions(node)
            action_to_expand = (possible - expanded).sample(1)
            sim.change_state(node.state)
            sim.play(action_to_expand)
            node_to_expand = Tree(sim)


        ancestors = []
        parent = node.parent
        while parent:
            ancestors.append(parent)
        for a in ancestors.reverse():
            if a.card is not None:
                self.sim.play(a.card, a.target)

        expanded = {(n.card, n.target) for n in node.children}
        possible = self.get_possible_actions(node)

        if (possible - expanded):
            node_to_expand = (possible - expanded).sample(1)
        else:
            node_to_expand =


        for c in self.sim.hand:
            if c.has_target:
                for t in self.sim.monsters:
                    if (c, t) not in set(map(lambda n: (n.card, n.target), node.children)):
                    result = self.sim.sim_combat(c, t)
                    new_node = Tree(c, t)
                    node.add_child(new_node, result)
                    self.nodes.append(new_node)
            else:
                result = self.sim.sim_combat(c, self.sim.player)
                new_node = Tree(c, t)
                node.add_child(new_node, result)
                self.nodes.append(node)

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
        node.increment(result)
        node.backpropagate(result)

    def increment(self, result):
        self.wins += result
        self.total += result
        self.value = self.calc_value()

    def calc_value(self):
        ave_reward = self.wins/self.total
        parent_sims = self.parent.total

        return ave_reward + math.sqrt(2)*(math.sqrt(math.log(parent_sims)/self.total))

    def backpropagate(self, result):
        p = self.parent
        while p:
            p.increment()
            p = p.parent
