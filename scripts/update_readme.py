"""Fill the README's projects and blog sections from the pushkar.io RSS feed."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = "https://pushkar.io/rss.xml"
README = Path(__file__).resolve().parent.parent / "README.md"
LIMIT = 4


def fetch_items():
    # Cloudflare rejects urllib's default User-Agent
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "pshkrh-readme-bot"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    return [
        {
            "title": item.findtext("title", "").strip(),
            "link": item.findtext("link", "").strip(),
            "description": item.findtext("description", "").strip(),
        }
        for item in root.iter("item")
    ]


def replace_section(text, name, lines):
    pattern = re.compile(
        rf"(<!-- {name}:start -->\n).*?(<!-- {name}:end -->)", re.DOTALL
    )
    body = "".join(f"{line}\n" for line in lines)
    return pattern.sub(lambda m: m.group(1) + body + m.group(2), text)


def main():
    items = fetch_items()
    projects = [i for i in items if "/projects/" in i["link"]][:LIMIT]
    posts = [i for i in items if "/blog/" in i["link"]][:LIMIT]

    project_lines = [
        f"- **[{p['title']}]({p['link']})**: {p['description']}" for p in projects
    ]
    post_lines = [f"- [{p['title']}]({p['link']})" for p in posts]

    text = README.read_text()
    text = replace_section(text, "projects", project_lines)
    text = replace_section(text, "blog", post_lines)
    README.write_text(text)


if __name__ == "__main__":
    main()
