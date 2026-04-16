from .n_list import NListNode, extract_n_lists
from .ppc_tree import PPCTree
from .data_formatter import format_itemsets


class PrePost:
    def mine(self, transactions, minsup_count):
        frequent = self._mine_frequent(transactions, minsup_count)
        return format_itemsets(sorted(frequent.items()))

    def _mine_frequent(self, transactions, minsup_count):
        tree = PPCTree()
        frequent = tree.build(transactions, minsup_count)
        n_lists = extract_n_lists(tree)
        ordered_items = sorted(frequent, key=lambda item: (-frequent[item], item))
        pair_supports = self._pair_supports(tree, ordered_items)
        results = {}

        for index, item in enumerate(ordered_items):
            prefix = (item,)
            prefix_nlist = n_lists.get(item, [])
            results[self._normalize(prefix)] = self._support(prefix_nlist)

            for next_index in range(index + 1, len(ordered_items)):
                next_item = ordered_items[next_index]
                support = pair_supports[item].get(next_item, 0)

                if support < minsup_count:
                    continue

                pair_prefix = (item, next_item)
                pair_nlist = self._join_nlists(prefix_nlist, n_lists.get(next_item, []))
                results[self._normalize(pair_prefix)] = support
                self._mine_recursive(
                    pair_prefix,
                    pair_nlist,
                    ordered_items,
                    next_index + 1,
                    minsup_count,
                    n_lists,
                    results,
                )

        return results

    def _mine_recursive(
        self,
        prefix,
        prefix_nlist,
        ordered_items,
        start_index,
        minsup_count,
        n_lists,
        results,
    ):
        for next_index in range(start_index, len(ordered_items)):
            item = ordered_items[next_index]
            next_nlist = n_lists.get(item, [])
            if len(prefix_nlist) == 1:
                merged_nlist = self._join_single_path(prefix_nlist[0], next_nlist)
            else:
                merged_nlist = self._join_nlists(prefix_nlist, next_nlist)
            support = self._support(merged_nlist)

            if support < minsup_count:
                continue

            itemset = prefix + (item,)
            results[self._normalize(itemset)] = support
            self._mine_recursive(
                itemset,
                merged_nlist,
                ordered_items,
                next_index + 1,
                minsup_count,
                n_lists,
                results,
            )

    def _join_nlists(self, prefix_nlist, next_nlist):
        merged = []
        left_index = 0
        right_index = 0

        while left_index < len(prefix_nlist) and right_index < len(next_nlist):
            left_node = prefix_nlist[left_index]
            right_node = next_nlist[right_index]

            if left_node.pre_order >= right_node.pre_order:
                right_index += 1
                continue

            if left_node.post_order <= right_node.post_order:
                left_index += 1
                continue

            self._append_merged(
                merged,
                right_node.pre_order,
                right_node.post_order,
                right_node.count,
            )
            right_index += 1

        return merged

    def _join_single_path(self, ancestor, next_nlist):
        merged = []

        for node in next_nlist:
            if (
                ancestor.pre_order < node.pre_order
                and ancestor.post_order > node.post_order
            ):
                self._append_merged(
                    merged,
                    node.pre_order,
                    node.post_order,
                    node.count,
                )

        return merged

    def _support(self, n_list):
        return sum(node.count for node in n_list)

    def _pair_supports(self, tree, ordered_items):
        matrix = {item: {} for item in ordered_items}

        def visit(node, path_items):
            next_path = path_items

            if node.item is not None:
                for ancestor_item in path_items:
                    ancestor_row = matrix[ancestor_item]
                    ancestor_row[node.item] = (
                        ancestor_row.get(node.item, 0) + node.count
                    )

                next_path = path_items + [node.item]

            for child in node.children.values():
                visit(child, next_path)

        visit(tree.root, [])

        return matrix

    def _append_merged(self, merged, pre_order, post_order, count):
        if (
            merged
            and merged[-1].pre_order == pre_order
            and merged[-1].post_order == post_order
        ):
            last = merged[-1]
            merged[-1] = NListNode(last.pre_order, last.post_order, last.count + count)
            return

        merged.append(NListNode(pre_order, post_order, count))

    def _normalize(self, itemset):
        return tuple(sorted(itemset))
