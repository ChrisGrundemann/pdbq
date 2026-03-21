"""
Standalone sync entrypoint for Fly.io scheduled machine.
Runs: python sync/run.py [--incremental]
"""
import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdbq.sync.run import run_sync

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    parser = argparse.ArgumentParser(description="Sync PeeringDB data into DuckDB")
    parser.add_argument("--incremental", action="store_true", help="Only fetch updated records")
    args = parser.parse_args()

    results = run_sync(incremental=args.incremental)
    failed = [r for r, c in results.items() if c < 0]

    for resource, count in results.items():
        status = "OK" if count >= 0 else "FAILED"
        print(f"{resource:20s} {count:8d}  {status}")

    if failed:
        print(f"\nFailed resources: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
