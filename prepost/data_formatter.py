def format_itemset(items, support):
    return f"{' '.join(str(item) for item in sorted(items))} #SUP: {support}"


def format_itemsets(itemsets):
    return "\n".join(format_itemset(items, support) for items, support in itemsets)
