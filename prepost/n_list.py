from collections import namedtuple

NListNode = namedtuple("NListNode", ["pre_order", "post_order", "support"])


def extract_n_lists(tree):
    n_lists = {}

    for node in tree.iter_nodes():
        item = node.item
        if item not in n_lists:
            n_lists[item] = []
        n_lists[item].append(NListNode(node.pre_order, node.post_order, node.count))

    for item in n_lists:
        n_lists[item].sort(key=lambda n: n.pre_order)

    return n_lists
