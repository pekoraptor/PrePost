from collections import deque


class PPCNode:
    def __init__(self, item=None, parent=None):
        self.item = item
        self.count = 0
        self.parent = parent
        self.children = {}
        self.pre_order = 0
        self.post_order = 0


class PPCTree:
    def __init__(self):
        self.root = PPCNode()
        self._next_pre = 1
        self._next_post = 1

    def add_transaction(self, items):
        node = self.root

        for item in items:
            child = node.children.get(item)

            if child is None:
                child = PPCNode(item=item, parent=node)
                node.children[item] = child

            child.count += 1
            node = child

    def build(self, transactions, minsup_count):
        counts = {}

        for transaction in transactions:
            for item in set(transaction):
                counts[item] = counts.get(item, 0) + 1

        frequent = {
            item: support for item, support in counts.items() if support >= minsup_count
        }

        order = sorted(frequent, key=lambda item: (-frequent[item], item))
        rank = {item: idx for idx, item in enumerate(order)}

        self.root = PPCNode()

        for transaction in transactions:
            filtered = [item for item in transaction if item in frequent]
            filtered.sort(key=lambda item: rank[item])

            if filtered:
                self.add_transaction(filtered)

        self.encode()
        return frequent

    def encode(self):
        self._next_pre = 1
        self._next_post = 1
        self._encode_node(self.root)

    def _encode_node(self, node):
        node.pre_order = self._next_pre
        self._next_pre += 1

        for item in sorted(node.children):
            self._encode_node(node.children[item])

        node.post_order = self._next_post
        self._next_post += 1

    def iter_nodes(self):
        stack = deque([self.root])

        while stack:
            node = stack.pop()
            if node is not self.root:
                yield node
            for item in sorted(node.children, reverse=True):
                stack.append(node.children[item])
