"""Score a CraftSuite document task by inspecting the saved docx independently.

Usage: python craft_score.py <docx_path>

Checks are based on the task spec in craft_doc_task.md. Each check returns
pass/fail with evidence. No dependence on the agent's own claims.
"""
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def load(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        doc = z.read("word/document.xml").decode("utf-8", "replace")
        styles = ""
        if "word/styles.xml" in names:
            styles = z.read("word/styles.xml").decode("utf-8", "replace")
        media = [n for n in names if n.startswith("word/media/")]
        media_bytes = {n: len(z.read(n)) for n in media}
    return names, doc, styles, media_bytes


def text_of(xml):
    return "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", xml, re.S))


def main():
    path = Path(sys.argv[1])
    if not path.exists():
        print("MISSING FILE:", path)
        return 2

    names, doc, styles, media = load(path)
    plain = text_of(doc)
    results = []

    def check(name, ok, evidence=""):
        results.append((name, bool(ok), evidence))

    # 1. Required text strings
    for s in ["Project Aurora", "Quarterly Report", "Executive Summary", "Q3 2026"]:
        check(f"text:{s}", s in plain, f"found={s in plain}")

    # 2. Heading styles (Heading1/Heading2 present in document.xml pStyle)
    h1 = len(re.findall(r'<w:pStyle w:val="Heading1"', doc))
    h2 = len(re.findall(r'<w:pStyle w:val="Heading2"', doc))
    check("heading1_uses_style", h1 >= 1, f"Heading1 paragraphs={h1}")
    check("heading2_uses_style", h2 >= 1, f"Heading2 paragraphs={h2}")

    # 3. Bold runs (w:b present, excluding w:bCs which is complex script)
    # NOTE: the primary regex does not match <w:bCs>/<w:iCs>, so subtracting
    # their counts here would produce a negative total and falsely fail a
    # correctly formatted document.
    bold = len(re.findall(r"<w:b(?:\s[^>]*)?/?>", doc))
    check("bold_run_present", bold >= 1, f"bold run markers={bold}")

    # 4. Italic runs
    italic = len(re.findall(r"<w:i(?:\s[^>]*)?/?>", doc))
    check("italic_run_present", italic >= 1, f"italic run markers={italic}")

    # 5. Colored runs: any w:color w:val that is not 'auto'/000000
    colors = re.findall(r'<w:color w:val="([0-9A-Fa-f]{6})"', doc)
    colored = [c for c in colors if c.lower() not in ("000000", "ffffff")]
    check("colored_text", len(colored) >= 1, f"non-black colors={sorted(set(colored))[:6]}")

    # 6. Font size: the task requires 16pt or larger, i.e. w:sz >= 32
    # half-points (the old threshold of 28 was only 14pt).
    sizes = [int(x) for x in re.findall(r'<w:sz w:val="(\d+)"', doc)]
    check("enlarged_font_16pt", any(s >= 32 for s in sizes), f"sizes(half-pt)={sorted(set(sizes))[:10]}")

    # 7. Highlight
    hl = re.findall(r'<w:highlight w:val="(\w+)"', doc)
    check("highlight", len(hl) >= 1, f"highlights={sorted(set(hl))}")

    # 8. Image embedded
    check("image_embedded", len(media) >= 1, f"media files={media}")

    # 9. Table present
    tables = doc.count("<w:tbl>")
    check("table_present", tables >= 1, f"tables={tables}")

    # 10. Alignment (center/right) used
    align = re.findall(r'<w:jc w:val="(\w+)"', doc)
    check("alignment_used", any(a in ("center", "right") for a in align), f"alignments={sorted(set(align))}")

    total = len(results)
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"SCORE {passed}/{total}\n")
    for name, ok, ev in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<24} {ev}")
    print(f"\nplain text length={len(plain)}  media={media}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
