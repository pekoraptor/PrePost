import argparse
from pathlib import Path

from .data_loader import SPMFDataLoader
from .prepost import PrePost
from .prepost_plus import PrePostPlus
from .prepost_plus_memo import PrePostPlusMemo


IMPLEMENTATIONS = {
    "prepost": PrePost,
    "prepost-plus": PrePostPlus,
    "prepost-plus-memo": PrePostPlusMemo,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run PrePost on an SPMF dataset.")
    parser.add_argument("input", help="Path to an input dataset in SPMF format.")
    parser.add_argument("minsup", type=float, help="Minimum support as a fraction, e.g. 0.4.")
    parser.add_argument(
        "--impl",
        choices=sorted(IMPLEMENTATIONS),
        default="prepost",
        help="Implementation variant to use.",
    )
    parser.add_argument(
        "--output",
        help="Optional path for the formatted SPMF-style output. Defaults to stdout.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    loader = SPMFDataLoader()
    transactions, minsup_count, _ = loader.load(args.input, args.minsup)
    miner = IMPLEMENTATIONS[args.impl]()
    output = miner.mine(transactions, minsup_count)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
