import pytest

from mdtoc import build_toc, headings, update
from mdtoc.cli import main

DOC = """# Title

## Install
text
```bash
# not a heading
```
## Usage
### Flags
## Usage
"""


def test_headings_skip_code_fences_and_dedupe_anchors():
    got = [(lvl, anchor) for lvl, _, anchor in headings(DOC)]
    assert got == [(1, "title"), (2, "install"), (2, "usage"), (3, "flags"), (2, "usage-1")]


def test_build_toc_indents_by_level():
    assert build_toc(DOC) == "\n".join([
        "- [Title](#title)", "  - [Install](#install)", "  - [Usage](#usage)",
        "    - [Flags](#flags)", "  - [Usage](#usage-1)",
    ])


def test_max_level():
    assert "Flags" not in build_toc(DOC, max_level=2)


def test_punctuation_and_emphasis_in_anchor():
    assert headings("## What's `new`? v1.2")[0][2] == "whats-new-v12"


def test_update_is_idempotent_and_replaces_old_toc():
    doc = "<!-- toc -->\nstale\n<!-- /toc -->\n\n# A\n## B\n"
    once = update(doc)
    assert "stale" not in once and "[B](#b)" in once
    assert update(once) == once


def test_update_requires_markers():
    with pytest.raises(ValueError):
        update("# A")


def test_cli_write(tmp_path, capsys):
    f = tmp_path / "R.md"
    f.write_text("<!-- toc -->\n<!-- /toc -->\n# A\n## B\n")
    assert main([str(f), "--write"]) == 0
    assert "[B](#b)" in f.read_text()
    assert main([str(f)]) == 0
    assert "[A](#a)" in capsys.readouterr().out
