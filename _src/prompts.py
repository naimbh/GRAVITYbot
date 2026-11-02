"""
prompts.py

Original Author:
    Alexander O. Smith <aosmith@syr.edu>

Purpose:
    Prompt templates for GRAVITYbot LLM summarization tasks.
    Purpose:
        Prompt templates for GRAVITYbot LLM summarization tasks.

        - talk_prompt(): Summarizes Zooniverse Talk forum discussions for LIGO scientists
        - alog_prompt(): picks the aLOG prompt set by GRAVITYBOT_ALOG_PROMPT
        - alog_prompt_interface(): written for what volunteers see in the Gravity Spy interface (default)
        - alog_prompt_volunteer(): the first volunteer-first prompt
        - alog_prompt_legacy(): The original aLOG prompt, kept for comparison

    The prompt texts are Markdown files in resources/prompts/, so they can be edited
    without changing code. {{name}} marks where the code fills in a value.
"""

import json
import os
import pathlib
import re

import pandas as pd

import alog_acronyms
import alog_index

DATA_DELIMITER = "~~~"

RESOURCES = pathlib.Path(__file__).resolve().parent / "resources"
PROMPTS_DIR = RESOURCES / "prompts"
GLOSSARY_PATH = RESOURCES / "volunteer_glossary.md"
GLITCH_CLASSES_PATH = RESOURCES / "glitch_classes.md"

ALOG_BASE_URLS = {
    "LHO": "https://alog.ligo-wa.caltech.edu",
    "LLO": "https://alog.ligo-la.caltech.edu",
}


def format_data(data):
    """
    Converts a pandas DataFrame to a JSON-formatted string of records.

    Args:
        data (pandas.DataFrame or any): The data to format.

    Returns:
        str: A JSON-like string representation of the DataFrame records if `data` is a DataFrame;
             otherwise, returns `data` unchanged.
    """
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient="records")
        records = ",\n ".join(map(json.dumps, records))
        return f"[\n {records}\n]"

    return data



def render(template_name, **values):
    """
    Fill a prompt template from resources/prompts/.

    Each {{name}} in the template is replaced by values[name]. Inserted values are
    not scanned again, so log text that happens to contain braces is left alone.

    Raises:
        KeyError: if the template uses a name that has no value.
    """
    template = (PROMPTS_DIR / template_name).read_text(encoding="utf-8").strip()
    missing = sorted(set(re.findall(r"\{\{(\w+)\}\}", template)) - values.keys())
    if missing:
        raise KeyError(f"{template_name}: no value for {missing}")
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), template)


def _load_glossary():
    return GLOSSARY_PATH.read_text(encoding="utf-8").strip()


def talk_prompt(prior_data, current_data):
    """
    Constructs prompts for summarizing Zooniverse Talk forum discussions.

    Args:
        prior_data (pandas.DataFrame): Talk data from the prior week.
        current_data (pandas.DataFrame): Talk data from the current week.

    Returns:
        tuple: (user_prompt, sys_prompt) for the LLM.
    """
    user_prompt = render("talk_user.md", data_delimiter=DATA_DELIMITER,
                         prior_data=format_data(prior_data), current_data=format_data(current_data))
    sys_prompt = render("talk_system.md", data_delimiter=DATA_DELIMITER)
    return user_prompt, sys_prompt


# Legacy alias for backward compatibility
def ligo_prompt(talk_dat0, talk_dat1):
    """Deprecated: Use talk_prompt() instead."""
    return talk_prompt(talk_dat0, talk_dat1)


def alog_prompt_legacy(prior_data, current_data, lab):
    """
    Original aLOG prompt, kept for comparison. alog_prompt() below replaces it.

    Args:
        prior_data (pandas.DataFrame): aLOG entries from the prior 5-day period.
        current_data (pandas.DataFrame): aLOG entries from the current 5-day period.
        lab (str): Lab identifier ("LHO" or "LLO") used in prompt context.

    Returns:
        tuple: (user_prompt, sys_prompt) for the LLM.
    """
    template_call_rep = "75875"
    base_url = ALOG_BASE_URLS.get(lab, ALOG_BASE_URLS["LLO"])

    user_prompt = render("alog_legacy_user.md", data_delimiter=DATA_DELIMITER,
                         prior_data=format_data(prior_data), current_data=format_data(current_data))
    sys_prompt = render("alog_legacy_system.md", data_delimiter=DATA_DELIMITER, lab=lab,
                        template_call_rep=template_call_rep,
                        template_link_text=f"{lab}: {template_call_rep}",
                        template_link_url=f"{base_url}/aLOG/index.php?callRep={template_call_rep}")
    return user_prompt, sys_prompt


def alog_prompt_volunteer(prior_data, current_data, lab):
    """
    Volunteer-first prompt, version 1 (kept for comparison; alog_prompt_interface replaces it).
    Constructs prompts for summarizing LIGO aLOG posts for Gravity Spy volunteers.

    The summary reports what a volunteer needs to interpret glitches, in a fixed
    order (detector status, locklosses, glitches and noise, environment, tests and
    injections, the DetChar report, changes that may change the noise), with a
    short plain explanation per important item. Script-built indexes
    (alog_index.py) give the model complete lists of locklosses, key entries and
    environment mentions to verify.

    Args:
        prior_data (pandas.DataFrame): prior-period entries (posted_utc, comment_url, comment_title, comment).
        current_data (pandas.DataFrame): current-period entries, same columns.
        lab (str): Lab identifier ("LHO" or "LLO").

    Returns:
        tuple: (user_prompt, sys_prompt) for the LLM.
    """
    base_url = ALOG_BASE_URLS.get(lab, ALOG_BASE_URLS["LLO"])
    link = f"[{lab}: 75875]({base_url}/aLOG/index.php?callRep=75875)"

    sys_prompt = render("alog_volunteer_system.md", data_delimiter=DATA_DELIMITER, lab=lab,
                        link=link, glossary=_load_glossary())
    user_prompt = render("alog_volunteer_user.md", data_delimiter=DATA_DELIMITER,
                         lockloss_index=alog_index.lockloss_index(current_data, lab),
                         key_entries=alog_index.key_index(current_data, lab),
                         environment_mentions=alog_index.env_index(current_data, lab),
                         prior_data=format_data(alog_index.brief(prior_data)),
                         current_data=format_data(current_data))
    return user_prompt, sys_prompt


def alog_prompt_interface(prior_data, current_data, lab):
    """Build (user_prompt, sys_prompt). Data frames carry posted_utc, comment_url, comment_title, comment."""
    base_url = ALOG_BASE_URLS.get(lab, ALOG_BASE_URLS["LLO"])
    link = f"[{lab}: 75875]({base_url}/aLOG/index.php?callRep=75875)"

    sys_prompt = render("alog_interface_system.md", data_delimiter=DATA_DELIMITER, lab=lab, link=link,
                        glitch_classes=GLITCH_CLASSES_PATH.read_text(encoding="utf-8").strip(),
                        glossary=_load_glossary())
    user_prompt = render("alog_interface_user.md", data_delimiter=DATA_DELIMITER,
                         locklosses_per_day=alog_index.locklosses_per_day(current_data, lab),
                         key_entries=alog_index.key_index(current_data, lab),
                         environment_mentions=alog_index.env_index(current_data, lab),
                         acronyms=alog_acronyms.acronym_block(current_data),
                         prior_data=format_data(alog_index.brief(prior_data)),
                         current_data=format_data(current_data))
    return user_prompt, sys_prompt


def alog_prompt(prior_data, current_data, lab):
    """
    Build the aLOG prompts with the version chosen by GRAVITYBOT_ALOG_PROMPT:
    "interface" (default; written for what volunteers see in the Gravity Spy interface),
    "volunteer" (the first volunteer-first prompt) or "legacy" (the original prompt).
    """
    choice = os.environ.get("GRAVITYBOT_ALOG_PROMPT", "interface").strip().lower()
    builder = {"interface": alog_prompt_interface, "volunteer": alog_prompt_volunteer,
               "legacy": alog_prompt_legacy}.get(choice)
    if builder is None:
        raise ValueError(f"GRAVITYBOT_ALOG_PROMPT must be interface, volunteer or legacy, not {choice!r}")
    return builder(prior_data, current_data, lab)


def alog_postprocess(summary, period=None):
    """Remove instruction text or closing filler the model sometimes adds, and fold stray "Status:" lines into the bullet above.
    Bare citations ([LHO:85709]) become links to the aLOG entry.
    With period (e.g. "2025-07-12 to 2025-07-18"), the dates are added to the "Detector status this week" heading."""
    import re
    out = []
    for line in summary.splitlines():
        if re.match(r"^\s*\(?(Omit (a|this) heading|Omitted heading|If more details|For more details|No (other )?items? (this week )?under)", line, re.I):
            continue
        m = re.match(r"^\s*(?:[-*]\s*)?Status:\s*(.*)$", line)
        if m and out and out[-1].lstrip().startswith(("-", "*")):
            out[-1] = out[-1].rstrip() + f" Status: {m.group(1).strip()}"
        else:
            out.append(line)
    while out and re.match(r"^\s*\(.*\)\s*$", out[-1]) or (out and not out[-1].strip()):
        out.pop()                       # closing parenthetical filler
    text = "\n".join(out).rstrip() + "\n"
    # Link bare citations such as [LHO:85709] or LHO:85709 to the aLOG entry, so readers can check them.
    def _link(m):
        site, rep = m.group(1).upper(), m.group(2)
        return f"[{site}: {rep}]({ALOG_BASE_URLS[site]}/aLOG/index.php?callRep={rep})"
    text = re.sub(r"\[(LHO|LLO):\s*(\d{4,6})\](?!\()", _link, text)
    text = re.sub(r"(?<![\[\w/=])(LHO|LLO):\s?(\d{5,6})\b(?!\]|\))", _link, text)
    text = format_explanations(text)
    if period:
        text = re.sub(r"^(#+\s*Detector status this week)\b[^\n]*$", lambda m: f"{m.group(1)} ({period})", text, flags=re.M)
    return text


def format_explanations(text):
    """Put every "What this means:" on its own line under its item, with only the label in bold."""
    import re
    label = re.compile(r"(?<!\*\*)\bWhat this means:")
    bullet = re.compile(r"^(\s*)([-*]|\d+\.)\s+")
    out = []
    for line in text.split("\n"):
        m = label.search(line)
        if not m:
            out.append(line)
            continue
        before, after = line[:m.start()], line[m.end():].strip()
        b = bullet.match(line)
        if before.strip() in ("", "-", "*"):          # already on its own line or written as a sub-bullet
            indent = re.match(r"\s*", before).group(0)
            if not indent and out and bullet.match(out[-1]):
                bm = bullet.match(out[-1]); indent = bm.group(1) + " " * (len(bm.group(2)) + 1)
            if out and out[-1].strip():
                out[-1] = out[-1].rstrip() + "  "     # Markdown line break
        else:                                           # inline after the item's text
            indent = (b.group(1) + " " * (len(b.group(2)) + 1)) if b else re.match(r"\s*", line).group(0)
            out.append(before.rstrip() + "  ")
        out.append(f"{indent}**What this means:** {after}")
    return "\n".join(out)
