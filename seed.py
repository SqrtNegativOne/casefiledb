"""Top-level entry point: python seed.py"""

from __future__ import annotations

import logging

from catalog.seed import run_seed

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    run_seed()
