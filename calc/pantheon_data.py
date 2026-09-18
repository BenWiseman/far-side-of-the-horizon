"""Resolve the two external Pantheon+ inputs without a machine-specific path."""
import os
from pathlib import Path

FILENAMES = ('PantheonPlusSH0ES.dat', 'PantheonPlusSH0ES_STAT+SYS.cov')


def pantheon_directory():
    default = Path(__file__).resolve().parents[1] / 'data' / 'pantheon_plus'
    return Path(os.environ.get('PAPER2_PANTHEON_DIR', str(default))).expanduser().resolve()


def pantheon_files():
    directory = pantheon_directory()
    files = tuple(directory / name for name in FILENAMES)
    missing = [str(path) for path in files if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            'Missing Pantheon+ input(s): ' + ', '.join(missing)
            + '. See data/README.md for pinned download URLs and hashes, or set '
            'PAPER2_PANTHEON_DIR to an existing data directory.'
        )
    return files
