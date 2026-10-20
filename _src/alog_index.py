"""
alog_index.py

Deterministic helpers for the volunteer prompt (version 3 on):
    lockloss_index(current)  - one line per lockloss entry, with its UTC time
                               and the start of its text and follow-up comments.
    key_index(current)       - data-quality, calibration, injection, earthquake,
                               power and weather entries,
                               which the model tends to miss in a long dump.
    brief(prior)             - the prior week cut to titles and the start of
                               each entry, since it is only used to judge
                               whether an issue is new, ongoing or fixed.
The data frames carry posted_utc, comment_url, comment_title, comment. If any of
these columns is missing, the indexes are skipped.
"""
import datetime
import re

_TIME = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):?([0-5]\d)(?::\d\d)?\s*UTC", re.I)
_STAMP = re.compile(r"(\d{4}-\d\d-\d\d)\s+([01]?\d|2[0-3]):([0-5]\d)(?::\d\d)?\s*UTC")
NEEDED = ("posted_utc", "comment_url", "comment_title", "comment")
SKIPPED = "(not available: the input lacks posting times or titles)"


def _usable(df):
    return all(c in df.columns for c in NEEDED)


_KEY = re.compile(r"\bDQ\b|DetChar|data quality|calibration|\bcal\b|sweep|injection|\bPEM\b|hardware inj"
                  r"|earthquake|\bEQ\b|power (outage|glitch|failure|loss|flicker)|\bwind\b|storm|lightning|\bcomb\b", re.I)


def _rep(url):
    m = re.search(r"callRep=(\d+)", url or "")
    return m.group(1) if m else "?"


def _clip(text, n):
    text = " ".join(str(text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _is_followup(title):
    return " - Comment to " in title or title.startswith("Comment to ")


_TXT = [re.compile(r"(?:(?P<d>\d{4}-\d\d-\d\d)\s+)?(?<![\d:])(?P<h>[01]?\d|2[0-3]):(?P<m>[0-5]\d)(?::\d\d)?\s*(?:UTC)?\s*[-\u2013:]?\s*(?:lock\s?loss|lost lock)", re.I),
        re.compile(r"(?:lock\s?loss|lost lock)\s+(?:at|@)\s+(?:(?P<d>\d{4}-\d\d-\d\d)\s+)?(?P<h>[01]?\d|2[0-3]):(?P<m>[0-5]\d)", re.I),
        re.compile(r"lock\s?loss\s+(?P<d>\d{4}-\d\d-\d\d)\s+(?P<h>[01]?\d|2[0-3]):(?P<m>[0-5]\d)", re.I),          # "Unknown Lockloss 2025-07-18 23:23:49"
        re.compile(r"(?<![\d:.])(?P<h>[01]\d|2[0-3])(?P<m>[0-5]\d)(?![\d:])\s*(?:UTC)?\s*[-\u2013:]?\s*lock\s?loss", re.I)]  # "1732 LOCKLOSS"


def _when(posted, hh, mm, date=None):
    if date:
        return datetime.datetime.strptime(f"{date} {hh}:{mm}", "%Y-%m-%d %H:%M")
    w = posted.replace(hour=int(hh), minute=int(mm))
    return w - datetime.timedelta(days=1) if w > posted + datetime.timedelta(minutes=10) else w


def lockloss_index(current, lab):
    if not _usable(current):
        return SKIPPED
    rows = sorted(current.to_dict("records"), key=lambda r: r["posted_utc"])
    # Attach each follow-up to the latest earlier entry with the parent's title.
    # Titles such as "Lockloss" repeat, so matching by title alone mixes events.
    follow, last = {}, {}
    for r in rows:
        t = r["comment_title"]
        if _is_followup(t):
            parent = t.split("Comment to ", 1)[1].strip()
            if parent in last:
                follow.setdefault(last[parent], []).append(r)
        else:
            last[t.split(" - ", 1)[1].strip() if " - " in t else t] = r["comment_url"]
    out, seen = [], set()
    for r in rows:
        t = r["comment_title"]
        if _is_followup(t) or not re.search(r"lock\s?loss", t, re.I):
            continue
        m = _TIME.search(t) or _TIME.search(str(r["comment"])[:200])
        posted = datetime.datetime.strptime(r["posted_utc"], "%Y-%m-%d %H:%M UTC")
        if not m:
            if re.match(r"^\S+ \S+ - (H1 )?lock\s?loss\b", t, re.I):     # a lockloss entry with no time in it
                out.append(f"- time not given, posted {r['posted_utc']} [{lab}:{_rep(r['comment_url'])}] {_clip(r['comment'], 220)}")
            continue     # otherwise an analysis entry about locklosses, not a single lockloss
        hh, mm = int(m.group(1)), int(m.group(2))
        when = posted.replace(hour=hh, minute=mm)
        if when > posted + datetime.timedelta(minutes=10):
            when -= datetime.timedelta(days=1)      # posted after midnight UTC
        k = when.strftime("%Y-%m-%d %H:%M")
        if k in seen:
            continue
        seen.add(k)
        parent = t.split(" - ", 1)[1].strip() if " - " in t else t
        fu = " | ".join(f"[{lab}:{_rep(f['comment_url'])}] {_clip(f['comment'], 140)}" for f in follow.get(r["comment_url"], [])[:4])
        out.append(f"- {k} UTC [{lab}:{_rep(r['comment_url'])}] {_clip(r['comment'], 220)}" + (f" || follow-ups: {fu}" if fu else ""))
    # Locklosses mentioned only inside shift summaries or comments.
    times = [datetime.datetime.strptime(k, "%Y-%m-%d %H:%M") for k in seen]
    for r in rows:
        posted = datetime.datetime.strptime(r["posted_utc"], "%Y-%m-%d %H:%M UTC")
        text = " ".join(str(r["comment"]).split())
        hits = [m for rx in _TXT for m in rx.finditer(text)]
        if re.search(r"lock\s?losses", text, re.I):      # "Two locklosses last night: 2025-09-01 06:55 UTC - ..."
            hits += list(_STAMP.finditer(text))
        for m in hits:
            if True:
                g = m.groupdict()
                w = _when(posted, g.get("h") or m.group(2), g.get("m") or m.group(3), g.get("d") if "h" in g else m.group(1))
                if any(abs((w - t).total_seconds()) <= 300 for t in times):
                    continue
                times.append(w)
                ctx = _clip(text[max(0, m.start() - 60): m.end() + 100], 170)
                out.append(f"- {w:%Y-%m-%d %H:%M} UTC (mentioned in [{lab}:{_rep(r['comment_url'])}] {r['comment_title']}) ...{ctx}...")
    if rows:
        start = min(r["posted_utc"] for r in rows)[:10]
        out = [x for x in out if x.startswith("- time not given") or x[2:12] >= start]
    return "\n".join(sorted(out)) if out else "(no lockloss entries found)"


def key_index(current, lab):
    if not _usable(current):
        return SKIPPED
    out = [f"- {r['posted_utc']} [{lab}:{_rep(r['comment_url'])}] {r['comment_title']}"
           for r in current.to_dict("records")
           if not _is_followup(r["comment_title"]) and _KEY.search(r["comment_title"])]
    return "\n".join(out) if out else "(none found by title)"


def brief(prior, n=300, links=True):
    df = prior.copy()
    if "comment" not in df.columns:
        return df
    df["comment"] = df["comment"].map(lambda x: _clip(x, n))
    return df if links else df.drop(columns=["comment_url"])


_ENV = re.compile(r"earthquake|\bEQ\b|power (?:outage|glitch|failure|loss|flicker)|lightning|(\d+)\s*mph", re.I)


def env_index(current, lab, limit=30):
    """Sentences that mention earthquakes, power events, lightning or wind of 30 mph or more, one per entry and kind."""
    if not _usable(current):
        return SKIPPED
    out, seen = [], set()
    for r in sorted(current.to_dict("records"), key=lambda r: r["posted_utc"]):
        text = " ".join(str(r["comment"]).split())
        for m in _ENV.finditer(text):
            if m.group(1) is not None:
                if int(m.group(1)) < 30:
                    continue          # routine wind readings in every shift report
                kind = "wind"
            else:
                kind = m.group(0).lower().split()[0]
            if (r["comment_url"], kind) in seen:
                continue
            seen.add((r["comment_url"], kind))
            out.append(f"- posted {r['posted_utc']} [{lab}:{_rep(r['comment_url'])}] ...{_clip(text[max(0, m.start() - 90): m.end() + 90], 200)}...")
            if len(out) >= limit:
                return "\n".join(out)
    return "\n".join(out) if out else "(none found)"
