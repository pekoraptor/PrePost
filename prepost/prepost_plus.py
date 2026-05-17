from .n_list import extract_n_lists
from .ppc_tree import PPCTree
from .prepost import PrePost


class PrePostPlus(PrePost):
    def mine_itemsets(self, transactions, minsup_count):
        return self._mine_frequent(transactions, minsup_count)

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
            prefix_support = self._support(prefix_nlist)
            results[self._normalize(prefix)] = prefix_support

            for next_index in range(index + 1, len(ordered_items)):
                next_item = ordered_items[next_index]
                support = pair_supports[item].get(next_item, 0)

                if support < minsup_count:
                    continue

                pair_prefix = (item, next_item)
                pair_nlist = self._join_nlists(prefix_nlist, n_lists.get(next_item, []))
                results[self._normalize(pair_prefix)] = support

                if self._is_cpe(prefix_support, support):
                    self._mine_recursive(
                        pair_prefix,
                        prefix_nlist,
                        ordered_items,
                        next_index + 1,
                        minsup_count,
                        n_lists,
                        results,
                    )
                    continue

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
        prefix_support = self._support(prefix_nlist)

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

            if self._is_cpe(prefix_support, support):
                self._mine_recursive(
                    itemset,
                    prefix_nlist,
                    ordered_items,
                    next_index + 1,
                    minsup_count,
                    n_lists,
                    results,
                )
                continue

            self._mine_recursive(
                itemset,
                merged_nlist,
                ordered_items,
                next_index + 1,
                minsup_count,
                n_lists,
                results,
            )

    def _is_cpe(self, parent_support, child_support):
        return parent_support == child_support
