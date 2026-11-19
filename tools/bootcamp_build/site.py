"""Build the pages published at hub.senzing.com/bootcamp/.

``site/`` holds the landing page and one template, ``_install.html``, for the page that tells
a bootcamper how to install the bootcamp in their assistant. The template is rendered once
per host, so every assistant's page has the same sections in the same order and says the same
things about the bootcamp itself; only the steps that really differ come from the host
(``hosts/<id>/fragments/site-*.html`` and the ``site`` block of its profile).

The landing page's list of assistants is generated from the same profiles, so a host cannot
have a package without a page, or a page without a link to it.
"""

from __future__ import annotations

import dataclasses
import html
import shutil
from pathlib import Path

from .model import BuildError, Host
from .render import render_text

TEMPLATE = "_install.html"
SITE_KEYS = ("name", "kind", "plan", "plan_url", "note", "lead", "description", "commands_note", "order")
COUNT_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}


def site_hosts(hosts: list[Host]) -> list[Host]:
    """The hosts that have a page, in the order the site lists them."""
    listed = [host for host in hosts if host.site]
    for host in listed:
        for key in SITE_KEYS:
            if key not in host.site:
                raise BuildError(f"hosts/{host.id}/host.json: site.{key} is missing")
    return sorted(listed, key=lambda host: (host.site["order"], host.id))


def _assistant_list(hosts: list[Host]) -> str:
    names = [host.site["name"] for host in hosts]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]


def _cards(hosts: list[Host], indent: str) -> str:
    lines = []
    for host in hosts:
        site = {key: html.escape(str(value)) for key, value in host.site.items()}
        lines += [
            f'{indent}<li class="card" id="platform-{host.id}">',
            f'{indent}  <h3>{site["name"]}</h3>',
            f'{indent}  <p class="card__kind">{site["kind"]}</p>',
            f'{indent}  <p class="card__plan">Plan minimum <strong><a href="{site["plan_url"]}">{site["plan"]}</a></strong></p>',
            f'{indent}  <p class="card__note">{site["note"]}</p>',
            f'{indent}  <a class="btn btn--flat" href="{host.id}/">Start with {site["name"]}</a>',
            f"{indent}</li>",
        ]
    return "\n".join(lines) + "\n"


def _buttons(hosts: list[Host], indent: str, prefix: str) -> str:
    return "".join(
        f'{indent}<a class="btn btn--outline" href="{prefix}{host.id}/">{html.escape(host.site["name"])}</a>\n'
        for host in hosts
    )


def verification_note(host: Host, version: str, indent: str) -> str:
    """One paragraph saying how far this version has really been run on this assistant.

    A page whose steps nobody has followed on the real assistant says so, rather than reading
    as tested. The wording comes from the check records in ``hosts/<id>/checks.json``.
    """
    name = html.escape(host.site["name"])
    passed = [check for check in host.checks if check["release"] == version and check["result"] == "pass"]
    full = [check for check in passed if check["scope"] == "full"]
    installed = [check for check in passed if check["scope"] in ("install", "full")]
    if full:
        latest = max(full, key=lambda check: check["date"])
        body = f"Checked end to end in {html.escape(latest['client'])} on {latest['date']}."
        kind = "note note--checked"
    elif installed:
        latest = max(installed, key=lambda check: check["date"])
        body = (f"<strong>Preview.</strong> Version {version} was installed and started in "
                f"{html.escape(latest['client'])} on {latest['date']}. It has not yet been walked through to graduation in {name}.")
        kind = "note note--preview"
    elif passed:
        latest = max(passed, key=lambda check: check["date"])
        body = (f"<strong>Preview.</strong> Version {version} was started in {html.escape(latest['client'])} on "
                f"{latest['date']}, from a local build. These install steps have not yet been followed end to end in {name}.")
        kind = "note note--preview"
    else:
        body = (f"<strong>Preview.</strong> These steps follow the documentation for {name}. "
                f"Version {version} of the bootcamp has not yet been run in {name}.")
        kind = "note note--preview"
    return f'{indent}<p class="{kind}">{body}</p>\n'


def _expand_markers(text: str, hosts: list[Host], current: Host | None, version: str = "") -> str:
    """Replace the site's own markers, each alone on its line, keeping the line's indentation.

    The `site-before.html` fragment each host gives here states `python3` on the `PATH`
    (INV-433), and its install fragment names every interface the host's naming table names,
    disclaiming one it has no steps for (INV-443). Its tips fragment holds the one
    `update-uninstall` tip every page links to (INV-444).
    """
    count = COUNT_WORDS.get(len(hosts), str(len(hosts)))
    text = text.replace("{{site.assistant_count}}", count)
    text = text.replace("{{site.assistant_list}}", html.escape(_assistant_list(hosts)))
    output = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        indent = line[: len(line) - len(line.lstrip())]
        if stripped == "<!-- site:assistant-cards -->":
            output.append(_cards(hosts, indent))
        elif stripped == "<!-- site:assistant-buttons -->":
            output.append(_buttons(hosts, indent, ""))
        elif stripped == "<!-- site:verification-note -->" and current is not None:
            output.append(verification_note(current, version, indent))
        elif stripped == "<!-- site:other-assistants -->":
            others = [host for host in hosts if current is None or host.id != current.id]
            output.append(_buttons(others, indent, "../"))
        else:
            output.append(line)
    rendered = "".join(output)
    if "site:" in rendered and "<!-- site:" in rendered:
        raise BuildError("site: an unknown '<!-- site:... -->' marker is left in a page")
    return rendered


def build_site(site_dir: Path, hosts: list[Host], declaration: dict, out_dir: Path) -> list[str]:
    """Write the site under ``out_dir`` and return the files written."""
    listed = site_hosts(hosts)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    written: list[str] = []
    known = {host.id for host in hosts}
    for path in sorted(site_dir.rglob("*")):
        relative = path.relative_to(site_dir)
        if not path.is_file() or relative.name.startswith("_"):
            continue
        target = out_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.suffix == ".html":
            target.write_text(_expand_markers(path.read_text(encoding="utf-8"), listed, None), encoding="utf-8")
        else:
            shutil.copyfile(path, target)
        written.append(relative.as_posix())

    template = site_dir / TEMPLATE
    if listed and not template.is_file():
        raise BuildError(f"{template} is missing")
    for host in listed:
        variables = dict(host.vars)
        variables.update({f"site_{key}": str(value) for key, value in host.site.items()})
        variables["site_version"] = declaration["version"]
        variables["site_id"] = host.id
        page_host = dataclasses.replace(host, vars=variables)
        text = _expand_markers(template.read_text(encoding="utf-8"), listed, host, declaration["version"])
        rendered = render_text(text, page_host, f"site/{TEMPLATE}", directives=True, known_hosts=known)
        target = out_dir / host.id / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
        written.append(f"{host.id}/index.html")
    return sorted(written)


def assistant_table(hosts: list[Host]) -> str:
    """A Markdown table of the assistants, for the public README."""
    rows = ["| Assistant | Package | Plan minimum | Install steps |", "| --- | --- | --- | --- |"]
    for host in site_hosts(hosts):
        site = host.site
        rows.append(
            f"| {site['name']} | {site['kind']} | [{site['plan']}]({site['plan_url']}) "
            f"| <https://hub.senzing.com/bootcamp/{host.id}/> |"
        )
    return "\n".join(rows) + "\n"


def build_public(public_dir: Path, hosts: list[Host], out_dir: Path) -> list[str]:
    """Files that go to the root of the public repository as they are, such as its README.

    A Markdown file may hold the line ``<!-- site:assistant-table -->``, which becomes the table
    of assistants, so the README can never list an assistant the build does not produce.
    """
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    written: list[str] = []
    for path in sorted(public_dir.rglob("*")) if public_dir.is_dir() else []:
        if not path.is_file():
            continue
        relative = path.relative_to(public_dir)
        target = out_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            text = text.replace("<!-- site:assistant-table -->\n", assistant_table(hosts))
            if "<!-- site:" in text:
                raise BuildError(f"public/{relative.as_posix()}: an unknown '<!-- site:... -->' marker is left")
            target.write_text(text, encoding="utf-8")
        else:
            shutil.copyfile(path, target)
        written.append(relative.as_posix())
    return written
