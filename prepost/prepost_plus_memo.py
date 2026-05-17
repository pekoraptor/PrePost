from .data_formatter import format_itemsets
from .n_list import extract_n_lists
from .ppc_tree import PPCTree
from .prepost_plus import PrePostPlus


class PrePostPlusMemo(PrePostPlus):
    def mine(self, transactions, minsup_count):
        frequent = self.mine_itemsets(transactions, minsup_count)
        return format_itemsets(sorted(frequent.items()))

    def mine_itemsets(self, transactions, minsup_count):
        self._join_cache = {}
        self._single_path_cache = {}
        self._support_cache = {}

        return self._mine_frequent(transactions, minsup_count)

    def discover(self, transactions, minsup_count, rare_item_limit=18):
        self._join_cache = {}
        self._single_path_cache = {}
        self._support_cache = {}

        frequent = self._mine_frequent(transactions, minsup_count)
        closed, maximal = self._closed_maximal(frequent)
        rare = self._rare_itemsets(transactions, minsup_count, rare_item_limit)

        return {
            "frequent": frequent,
            "rare": rare,
            "closed": closed,
            "maximal": maximal,
        }

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
            prefix_support = self._support_cached(prefix_nlist)
            results[self._normalize(prefix)] = prefix_support

            for next_index in range(index + 1, len(ordered_items)):
                next_item = ordered_items[next_index]
                support = pair_supports[item].get(next_item, 0)

                if support < minsup_count:
                    continue

                pair_prefix = (item, next_item)
                pair_nlist = self._join_nlists_cached(
                    prefix_nlist, n_lists.get(next_item, [])
                )
                results[self._normalize(pair_prefix)] = support

                if prefix_support == support:
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
        prefix_support = self._support_cached(prefix_nlist)

        for next_index in range(start_index, len(ordered_items)):
            item = ordered_items[next_index]
            next_nlist = n_lists.get(item, [])

            if len(prefix_nlist) == 1:
                merged_nlist = self._join_single_path_cached(
                    prefix_nlist[0], next_nlist
                )
            else:
                merged_nlist = self._join_nlists_cached(prefix_nlist, next_nlist)

            support = self._support_cached(merged_nlist)

            if support < minsup_count:
                continue

            itemset = prefix + (item,)
            results[self._normalize(itemset)] = support

            if prefix_support == support:
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

    def _support_cached(self, n_list):
        key = tuple(n_list)
        if key in self._support_cache:
            return self._support_cache[key]

        support = self._support(n_list)
        self._support_cache[key] = support
        return support

    def _join_nlists_cached(self, prefix_nlist, next_nlist):
        key = (tuple(prefix_nlist), tuple(next_nlist))
        if key in self._join_cache:
            return self._join_cache[key]

        joined = self._join_nlists(prefix_nlist, next_nlist)
        self._join_cache[key] = joined
        return joined

    def _join_single_path_cached(self, ancestor, next_nlist):
        key = (ancestor, tuple(next_nlist))
        if key in self._single_path_cache:
            return self._single_path_cache[key]

        joined = self._join_single_path(ancestor, next_nlist)
        self._single_path_cache[key] = joined
        return joined

    def _closed_maximal(self, frequent):
        closed = {}
        maximal = {}
        itemsets = sorted(frequent, key=lambda itemset: (len(itemset), itemset))

        for itemset in itemsets:
            support = frequent[itemset]
            has_superset = False
            has_same_support_superset = False

            for candidate in itemsets:
                if len(candidate) <= len(itemset):
                    continue
                if not self._is_subset(itemset, candidate):
                    continue

                has_superset = True
                if frequent[candidate] == support:
                    has_same_support_superset = True
                    break

            if not has_same_support_superset:
                closed[itemset] = support
            if not has_superset:
                maximal[itemset] = support

        return closed, maximal

    def _rare_itemsets(self, transactions, minsup_count, rare_item_limit):
        items = sorted({item for transaction in transactions for item in transaction})
        if len(items) > rare_item_limit:
            raise ValueError(
                f"Rare mining is exponential and supports up to {rare_item_limit} unique items; got {len(items)}"
            )

        rare = {}

        def recurse(prefix, start):
            for index in range(start, len(items)):
                candidate = prefix + (items[index],)
                support = self._subset_support(candidate, transactions)

                if support == 0:
                    continue

                if support < minsup_count:
                    rare[candidate] = support

                recurse(candidate, index + 1)

        recurse((), 0)
        return rare

    def _subset_support(self, itemset, transactions):
        itemset = set(itemset)
        count = 0

        for transaction in transactions:
            if itemset.issubset(transaction):
                count += 1

        return count

    def _is_subset(self, small, large):
        small_index = 0
        large_index = 0

        while small_index < len(small) and large_index < len(large):
            if small[small_index] == large[large_index]:
                small_index += 1
                large_index += 1
            elif small[small_index] > large[large_index]:
                large_index += 1
            else:
                return False

        return small_index == len(small)
