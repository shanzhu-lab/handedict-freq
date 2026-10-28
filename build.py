"""Strip the editing history from HanDeDict and sort it by wordfreq Zipf frequency."""

import argparse
import re
import sys
import textwrap
import warnings
from importlib.metadata import metadata
from pathlib import Path

# The licences this script's header is written for; it stops if either changes.
HANDEDICT_LICENCE = "CC-BY-SA 3.0"
WORDFREQ_LICENCE = "Creative Commons Attribution-ShareAlike 4.0"
WORDLIST = "large"
# where SUBTLEX-CH is to be had today: the address wordfreq's README gives for it is gone
SUBTLEX_URL = (
    "https://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexch"
)

ENTRY_RE = re.compile(r"^(\S+) (\S+) \[([^\]]*)\] (/.*/)$")
ID_RE = re.compile(r"^# ID-(\S+)$")
VERSION_RE = re.compile(r"^# Ver \S+ (\S+) ")
TIMESTAMP_RE = re.compile(r"^# Datenstand: (\S+)$")
LICENCE_RE = re.compile(r"^# Lizenz: (.+)$")

# An entry's ID, traditional and simplified headwords, pinyin and definitions
Entry = tuple[str, str, str, str, str]


def parse(path: Path) -> tuple[str | None, str | None, set[str], list[Entry]]:
    """Return (data timestamp, licence, contributors, entries) of a HanDeDict export.

    Only the current version of each entry is kept; commented-out past versions
    are dropped.
    """
    timestamp = None
    licence = None
    contributors = set()
    entries = []
    entry_id = None
    with path.open(encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if m := ID_RE.match(line):
                entry_id = m[1]
            elif m := VERSION_RE.match(line):
                contributors.add(m[1])
            elif m := TIMESTAMP_RE.match(line):
                timestamp = m[1]
            elif m := LICENCE_RE.match(line):
                licence = m[1].strip()
            elif line and not line.startswith("#"):
                m = ENTRY_RE.match(line)
                if m is None:
                    raise ValueError(f"Malformed entry: {line!r}")
                if entry_id is None:
                    raise ValueError(f"Entry without ID: {line!r}")
                trad, simp, pinyin, defs = m.groups()
                entries.append((entry_id, trad, simp, pinyin, defs))
                entry_id = None
    return timestamp, licence, contributors, entries


def comment_block(text: str) -> str:
    return "".join(f"# {line}".rstrip() + "\n" for line in text.splitlines())


def header(
    rev: str, timestamp: str, contributors: set[str], wordfreq_version: str
) -> str:
    names = textwrap.fill(
        ", ".join(sorted(contributors, key=str.casefold)),
        width=76,
        initial_indent="  ",
        subsequent_indent="  ",
    )
    return comment_block(f"""\
HanDeDict, nach Worthäufigkeit sortiert
Kollaborativ entwickeltes, freies chinesisch-deutsches Wörterbuch,
ergänzt um Worthäufigkeiten aus wordfreq.
Datenstand: {timestamp}

Lizenz: CC BY-SA 4.0
https://creativecommons.org/licenses/by-sa/4.0/deed.de

Änderungen gegenüber dem Original:
- Die Änderungsgeschichte wurde entfernt; nur die aktuelle Version jedes
  Eintrags ist enthalten.
- Jeder Eintrag ist mit seiner Zipf-Häufigkeit aus wordfreq versehen (Liste
  "{WORDLIST}" der Sprache "zh"), ermittelt für die vereinfachte Schreibung.
  Zipf = log10(Vorkommen pro Milliarde Wörter).
  0 = in wordfreq nicht als ein Wort enthalten. Für Ausdrücke, die wordfreq
  zerlegt, wird seine aus den Bestandteilen geschätzte Häufigkeit nicht
  übernommen: Sie ist für jede Folge häufiger Zeichen hoch.
- Einträge aus mehreren Zeichen mit der Zipf-Häufigkeit 0 wurden entfernt;
  Einträge aus einem Zeichen sind alle enthalten.
- Die Einträge sind absteigend nach Zipf-Häufigkeit sortiert.
- Die Zeile "# ID-<HanDeDict-ID>" ist ohne das Präfix "ID-" mit der
  Zipf-Häufigkeit zu einer Kommentarzeile zusammengefasst (siehe Format); die
  Leerzeilen zwischen den Einträgen sind entfernt.

Format: kompatibel mit dem CEDICT-Format. Jedem Eintrag geht die
Kommentarzeile "# <HanDeDict-ID> <Zipf-Wert>" voraus, z. B. "# j50lW6h 7.79".


Quelle der Einträge: HanDeDict
https://github.com/gugray/HanDeDict (Commit {rev})
Veröffentlicht von Gábor L Ugray unter der Lizenz CC BY-SA 3.0
https://creativecommons.org/licenses/by-sa/3.0/deed.de

Ursprünglich erstellt mit der Unterstützung der Chinesisch-Deutschen Gesellschaft e.V. Hamburg,
unter der Leitung von Dr. Michael Klaus Engel und Jan Hefti
https://web.archive.org/web/20150325185952/http://www.handedict.de/chinesisch_deutsch.php?mode=dl
https://web.archive.org/web/20150325174145/http://www.handedict.de/chinesisch_deutsch.php?mode=about

Beitragende (Benutzernamen aus der Änderungsgeschichte):
{names}

Die vollständige Änderungsgeschichte jedes Eintrags ist in der Datei
handedict.u8 des oben genannten Commits sowie unter https://handedict.zydeo.net/
einsehbar.


Quelle der Worthäufigkeiten: wordfreq {wordfreq_version} von Robyn Speer
https://github.com/rspeer/wordfreq
Daten lizenziert unter CC BY-SA 4.0 (Code unter Apache 2.0).
Robyn Speer. (2022). rspeer/wordfreq: v3.0 (v3.0.2). Zenodo.
https://doi.org/10.5281/zenodo.7199437

wordfreq enthält Daten aus:
- Google Books Ngrams, http://books.google.com/ngrams
- Google Books Syntactic Ngrams,
  http://commondatastorage.googleapis.com/books/syntactic-ngrams/index.html
- The Leeds Internet Corpus, University of Leeds Centre for Translation Studies,
  http://corpus.leeds.ac.uk/list.html
- Wikipedia, http://www.wikipedia.org
- ParaCrawl, https://paracrawl.eu
- OPUS OpenSubtitles 2018, http://opus.nlpl.eu/OpenSubtitles.php, aus dem
  OpenSubtitles-Projekt, http://www.opensubtitles.org/
- SUBTLEX-CH: Cai, Q., & Brysbaert, M. (2010). SUBTLEX-CH: Chinese word and
  character frequencies based on film subtitles. PLoS One, 5(6), e10729.
  SUBTLEX ist frei verfügbar unter
  {SUBTLEX_URL}
- NewsCrawl 2014, GlobalVoices, OSCAR, Twitter und der Wortliste des
  Jieba-Segmentierers, https://github.com/fxsjy/jieba
""")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, required=True, help="HanDeDict handedict.u8"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rev", required=True, help="HanDeDict git commit")
    args = parser.parse_args()

    # jieba, which wordfreq segments Chinese with, has escapes that newer Pythons
    # warn about when compiling it, so it is only imported once they are silenced.
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    import jieba  # noqa: PLC0415
    from wordfreq import tokenize, zipf_frequency  # noqa: PLC0415

    jieba.setLogLevel(60)

    meta = metadata("wordfreq")
    if WORDFREQ_LICENCE not in str(meta.json.get("description", "")):
        sys.exit("build.py: wordfreq's README no longer says CC BY-SA 4.0, check it")
    timestamp, licence, contributors, entries = parse(args.input)
    if licence != HANDEDICT_LICENCE:
        sys.exit(f"build.py: HanDeDict is now licensed {licence!r}, check it")
    if timestamp is None:
        sys.exit("build.py: HanDeDict's header has no „Datenstand“")

    def zipf(word: str) -> float:
        # Of a word jieba splits, wordfreq would estimate a frequency from its
        # parts, which is high for any string of frequent glyphs: 5.72 for 不的,
        # against 5.29 for 老师. Such words count as 0.
        if len(tokenize(word, "zh")) != 1:
            return 0.0
        return zipf_frequency(word, "zh", wordlist=WORDLIST)

    # Keep the entries of a single glyph and of the words wordfreq has a frequency for.
    scored = ((zipf(e[2]), e) for e in entries)
    kept = ((z, e) for z, e in scored if z > 0 or len(e[2]) == 1)

    # Sort by descending frequency; ties are broken by headword for a stable output.
    ranked = sorted(
        kept,
        key=lambda x: (-x[0], x[1][2], x[1][1], x[1][3], x[1][4]),
    )

    with args.output.open("w", encoding="utf-8") as f:
        f.write(header(args.rev, timestamp, contributors, meta["Version"]) + "\n")
        f.writelines(
            f"# {entry_id} {zipf:.2f}\n{trad} {simp} [{pinyin}] {defs}\n"
            for zipf, (entry_id, trad, simp, pinyin, defs) in ranked
        )


if __name__ == "__main__":
    main()
