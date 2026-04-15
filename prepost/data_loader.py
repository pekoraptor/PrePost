from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SPMFLoaderConfig:
    encoding: str = "utf-8"
    item_separator: str = " "
    spmf_header_marker: str = "@CONVERTED_FROM_TEXT"
    spmf_item_marker: str = "@ITEM="
    default_minsup: float = 0.0
    min_minsup: float = 0.0
    max_minsup: float = 1.0


class SPMFDataLoader:
    def __init__(self, config=None, **overrides):
        if config is None:
            config = SPMFLoaderConfig()

        if overrides:
            config = replace(config, **overrides)

        self.config = config
        self.items_map = {}
        self.transactions = []
        self.minsup = self.config.default_minsup

    def load(self, filepath, minsup=None, validate=True):
        if minsup is None:
            minsup = self.config.default_minsup

        if validate and not (
            self.config.min_minsup <= minsup <= self.config.max_minsup
        ):
            raise ValueError(
                f"minsup must be between {self.config.min_minsup} and {self.config.max_minsup}"
            )

        self._reset_state()
        self.minsup = minsup

        with open(filepath, "r", encoding=self.config.encoding) as f:
            header_parsed = False

            for line in f:
                line = line.strip()
                if not line:
                    continue

                if not header_parsed and line.startswith(
                    self.config.spmf_header_marker
                ):
                    continue

                elif not header_parsed and line.startswith(
                    self.config.spmf_item_marker
                ):
                    parts = line.split("=", 2)
                    self.items_map[int(parts[1])] = parts[2]

                else:
                    header_parsed = True
                    transaction = {
                        int(item.strip())
                        for item in line.split(self.config.item_separator)
                        if item.strip()
                    }

                    if transaction:
                        self.transactions.append(transaction)

        if not self.transactions:
            raise ValueError("No valid transactions loaded")

        minsup_count = (
            max(1, int(self.minsup * len(self.transactions))) if self.minsup > 0 else 0
        )

        return self.transactions, minsup_count, self.items_map

    def _reset_state(self):
        self.items_map.clear()
        self.transactions.clear()

    def get_statistics(self):
        all_items = set()
        sizes = []

        for transaction in self.transactions:
            all_items.update(transaction)
            sizes.append(len(transaction))

        minsup_count = (
            max(1, int(self.minsup * len(self.transactions))) if self.minsup > 0 else 0
        )

        return {
            "num_transactions": len(self.transactions),
            "num_unique_items": len(all_items),
            "unique_items": sorted(all_items),
            "avg_transaction_size": sum(sizes) / len(sizes) if sizes else 0,
            "min_transaction_size": min(sizes) if sizes else 0,
            "max_transaction_size": max(sizes) if sizes else 0,
            "minsup": self.minsup,
            "minsup_count": minsup_count,
        }
