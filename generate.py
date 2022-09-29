#!/usr/bin/env python3

import io
import os
import shutil

import markdown
import pystache
import bibparser

# TODO bibtex parsing

IN_DIR = "src"
OUT_DIR = os.path.dirname(os.path.realpath(__file__))
ENCODING = "utf-8"


def in_dir(path):
    return os.path.join(IN_DIR, path)


def out_dir(path):
    return os.path.join(OUT_DIR, path)


def copy_tree(src, dst):
    assert os.path.exists(src)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def convert(markdown_str):
    html = io.BytesIO()
    md = markdown.Markdown()
    return md.convert(markdown_str)


def render(template_str, template_args=None):
    r = pystache.Renderer(escape=lambda u: u)
    return r.render(template_str, template_args)


def output(output_path, html):
    with open(output_path, "w") as f:
        f.write(html)


def oftype(typestr):

    def f(e):
        return e.keyvals["note"]["type"] == typestr

    return f


def main():
    bib = bibparser.Bib(in_dir("assets/dmillard.bib"))

    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)

    if os.path.exists(in_dir("assets")):
        copy_tree(in_dir("assets"), out_dir("assets"))

    with open(in_dir("index.md")) as f:
        content = convert(f.read())

    tmpldir = in_dir("templates")
    content = render(
        content, {
            'confs': bib.html(tmpldir, oftype("conference")),
            'workshops': bib.html(tmpldir, oftype("workshop")),
            'preprints': bib.html(tmpldir, oftype("preprint")),
        })

    with open(in_dir("templates/base.mustache")) as f:
        html = render(f.read(), {'content': content})

    output(out_dir("index.html"), html)


if __name__ == '__main__':
    main()
