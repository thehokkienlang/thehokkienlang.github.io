# OpenCC conversion subset

Unmodified files from `opencc-python-reimplemented==0.1.7` (Apache-2.0), with
only the `t2s` and `tw2s` configurations and their dictionaries retained.
The package and conversion dictionaries are vendored so Windows Desktop and
GitHub Actions use exactly the same conversion without extra installation.

Sources: https://github.com/yichen0831/opencc-python and
https://github.com/BYVoid/OpenCC. See `LICENSE.txt` and the original file headers.

Tangliengim calls the converter only for contiguous Hanri spans. This package
does not decide canonical orthography, IDs, pronunciation, or candidate order.
