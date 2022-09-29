from pathlib import Path
import pystache
import json


class BibAuthor:

    def __init__(self, s):
        self.lname, self.fname = map(str.strip, s.split(","))
        self.cofirst = False

    def html(self):
        out = f"{self.fname} {self.lname}"
        if self.cofirst:
            out += "*"
        if self.fname == "David" and self.lname == "Millard":
            out = f"<b>{out}</b>"
        return out


class BibEntry:

    def __init__(self, s):
        self.kind = s[s.find("@") + 1:s.find("{")].strip()
        s = s[s.find("{") + 1:s.rfind("}")]
        raw_keyvals = []
        prev_start = 0
        depth = 0
        for i, c in enumerate(s):
            if depth == 0 and c == ',' or i == len(s) - 1:
                raw_keyval = s[prev_start:i].strip()
                if raw_keyval != "":
                    raw_keyvals.append(raw_keyval)
                prev_start = i + 1
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1

        assert depth == 0

        self.key = raw_keyvals.pop(0)
        self.keyvals = {}
        note_i = -1
        for i, keyval in enumerate(map(str.strip, raw_keyvals)):
            k, v = map(str.strip, keyval.split("=", 1))
            if k == "note":
                note_i = i
                self.keyvals[k] = json.loads(v)
            else:
                v = v.replace("{", "").replace("}", "")
                self.keyvals[k] = v

        if note_i >= 0:
            raw_keyvals.pop(note_i)

        self.bibstring = "@"
        self.bibstring += self.kind
        self.bibstring += "{"
        self.bibstring += ",\n  ".join([self.key] + raw_keyvals)
        self.bibstring += "\n}"

        authors = [
            BibAuthor(author)
            for author in self.keyvals["author"].split(" and ")
        ]
        if "cofirst" in self.keyvals["note"]:
            for author in authors[:self.keyvals["note"]["cofirst"]]:
                author.cofirst = True

        self.authorhtml = authors[-1].html()
        if len(authors) > 1:
            self.authorhtml = " and ".join(
                (authors[-2].html(), self.authorhtml))
        if len(authors) > 2:
            self.authorhtml = ", ".join(
                list(map(BibAuthor.html, authors[:-2])) + [self.authorhtml])

    def html(self, template_dir):
        template_path = Path(template_dir) / f"bib/{self.kind}.mustache"
        if not template_path.exists():
            template_path = Path(template_dir) / f"bib/common.mustache"
        with open(template_path) as f:
            r = pystache.Renderer(escape=lambda u: u)
            return r.render(f.read(), {'entry': self})


def bib_entries_lt_date(e):
    months = "jan,feb,mar,apr,may,jun,jul,sep,oct,nov,dec".split(",")
    assert e.keyvals["month"] in months
    ey = int(e.keyvals["year"])
    em = months.index(e.keyvals["month"])
    return ey * 10000 + em


class Bib:

    def __init__(self, filename):
        contents = open(filename).read()
        self.entries = []
        prev_entry_start = 0
        depth = 0
        for i, c in enumerate(contents):
            if depth == 0 and c == '@':
                prev_entry_start = i
            elif c == '{':
                depth += 1
            elif c == '}':
                if depth == 1:
                    entrystr = contents[prev_entry_start:i + 1]
                    entry = BibEntry(entrystr)
                    self.entries.append(entry)
                depth -= 1

        assert depth == 0

    def html(self, template_dir, condition=None):
        entries = self.entries
        if condition != None:
            entries = filter(condition, entries)

        sorted_entries = sorted(entries, key=bib_entries_lt_date, reverse=True)

        items = "\n".join(f"<li>{e.html(template_dir)}</li>"
                          for e in sorted_entries)
        return f"<ul>\n{items}\n</ul>"
