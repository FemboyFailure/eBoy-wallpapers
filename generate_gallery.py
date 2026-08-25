#!/usr/bin/env python3
"""
Scans the repository for wallpaper images and rewrites the gallery
section of README.md between the GALLERY:START / GALLERY:END markers.

Images are grouped by their top-level folder (e.g. Anime/, Cats-Pets/),
with each folder name rendered as a section heading. Images directly in
the repo root (no subfolder) are rendered first, with no heading.

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
    """Returns a dict of {category: [rel_paths]}. Images directly in the repo
    root (no subfolder) are grouped under the "" category and rendered first,
    without a heading. Images in a first-level subfolder are grouped by that
    folder name, which becomes a section heading in the gallery."""
    images_by_category = {}
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dirpath, REPO_ROOT)
        category = "" if rel_dir == "." else rel_dir.split(os.sep)[0]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in IMAGE_EXTS:
                rel_path = os.path.relpath(os.path.join(dirpath, name), REPO_ROOT)
                rel_path = rel_path.replace(os.sep, "/")
                images_by_category.setdefault(category, []).append(rel_path)

    for cat in images_by_category:
        images_by_category[cat] = sorted(images_by_category[cat], key=str.lower)
    return images_by_category


def _table_for(images):
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

    return "<table>\n" + "\n".join(rows) + "\n</table>\n"


def build_gallery_markdown(images_by_category):
    if not images_by_category:
        return "_No wallpapers yet — push an image to see it here!_\n"

    parts = []

    # Root-level images (no folder) first, no heading.
    if images_by_category.get(""):
        parts.append(_table_for(images_by_category[""]))

    # Then each folder as its own section, alphabetically, folder name as heading.
    for category in sorted(k for k in images_by_category if k != ""):
        parts.append(f"### {category}\n")
        parts.append(_table_for(images_by_category[category]))

    return "\n".join(parts)


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