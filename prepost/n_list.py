from collections import namedtuple

NListNode = namedtuple("NListNode", ["pre_order", "post_order", "count"])


def extract_n_lists(tree):
    n_lists = {}

    for node in tree.iter_nodes():
        item = node.item
        if item not in n_lists:
            n_lists[item] = []
        n_lists[item].append(NListNode(node.pre_order, node.post_order, node.count))

    return n_lists
