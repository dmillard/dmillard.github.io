#!/usr/bin/env python3

import io
import os
import shutil

import markdown
import pystache

# TODO bibtex parsing

IN_DIR = "src"
OUT_DIR = os.path.dirname(os.path.realpath(__file__))
ENCODING = "utf-8"


def decode(b):
    return b.decode(ENCODING)


def in_dir(path):
    return os.path.join(IN_DIR, path)


def out_dir(path):
    return os.path.join(OUT_DIR, path)


def copy_tree(src, dst):
    assert os.path.exists(src)

    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def convert(markdown_path):
    html = io.BytesIO()
    md = markdown.Markdown()
    md.convertFile(input=markdown_path, output=html)

    return decode(html.getvalue())


def render(template_path, template_args=None):
    with open(template_path) as f:
        r = pystache.Renderer(escape=lambda u: u)
        return r.render(f.read(), template_args)


def output(output_path, html):
    with open(output_path, "w") as f:
        f.write(html)


def main():
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)

    if os.path.exists(in_dir("assets")):
        copy_tree(in_dir("assets"), out_dir("assets"))

    content = convert(in_dir("index.md"))
    html = render(in_dir("templates/base.mustache"), {'content': content})
    output(out_dir("index.html"), html)


if __name__ == '__main__':
    main()
