"""Run with: python -m pcm_aliasing [--output DIRECTORY]."""

import argparse
from pathlib import Path

from .demo import OUT, main


def cli():
    parser = argparse.ArgumentParser(description="Generate the 64-to-32 kHz PCM aliasing demo.")
    parser.add_argument("--output", type=Path, default=OUT,
                        help="Directory for WAV files, plots, report and verification JSON")
    args = parser.parse_args()
    main(args.output)


if __name__ == "__main__":
    cli()
