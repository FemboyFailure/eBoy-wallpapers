#!/usr/bin/env python3
"""
Scans the repository for wallpaper images and rewrites the gallery
section of README.md between the GALLERY:START / GALLERY:END markers.

Run from the repo root:
    python generate_gallery.py
"""

import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(REPO_ROOT, "README.md")

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
EXCLUDE_DIRS = {".git", ".github", "node_modules"}

START_MARKER = "<!-- GALLERY:START -->"
END_MARKER = "<!-- GALLERY:END -->"

# GitHub org/repo, e.g. "FemboyFailure/eBoy-wallpapers"
REPO_SLUG = "FemboyFailure/eBoy-wallpapers"
BRANCH = "main"


def find_images():
    images = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXTS:
                rel_path = os.path.relpath(os.path.join(dirpath, name), REPO_ROOT)
                rel_path = rel_path.replace(os.sep, "/")
                images.append(rel_path)
    return sorted(images, key=str.lower)


def build_gallery_markdown(images):
    if not images:
        return "_No wallpapers yet — push an image to see it here!_\n"

    raw_base = f"https://raw.githubusercontent.com/{REPO_SLUG}/{BRANCH}/"
    blob_base = f"https://github.com/{REPO_SLUG}/blob/{BRANCH}/"

    cells = []
    for path in images:
        name = os.path.splitext(os.path.basename(path))[0]
        img_url = raw_base + path
        link_url = blob_base + path
        cells.append(
            f'<a href="{link_url}"><img src="{img_url}" width="220" alt="{name}" /></a>'
        )

    # 3 wallpapers per row, in a simple HTML table so it renders in GitHub's markdown
    rows = []
    per_row = 3
    for i in range(0, len(cells), per_row):
        row_cells = cells[i:i + per_row]
        row_html = "".join(f"<td>{c}</td>" for c in row_cells)
        rows.append(f"<tr>{row_html}</tr>")

    table = "<table>\n" + "\n".join(rows) + "\n</table>\n"
    return table


def update_readme(gallery_md):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise SystemExit(
            f"README.md is missing {START_MARKER} / {END_MARKER} markers. "
            "Add them where you want the gallery to appear."
        )

    before = content.split(START_MARKER)[0]
    after = content.split(END_MARKER)[1]

    new_content = f"{before}{START_MARKER}\n\n{gallery_md}\n{END_MARKER}{after}"

    if new_content != content:
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md gallery updated.")
    else:
        print("No changes needed.")


if __name__ == "__main__":
    imgs = find_images()
    gallery = build_gallery_markdown(imgs)
    update_readme(gallery)
