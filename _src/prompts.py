"""
prompts.py

Original Author:
    Alexander O. Smith <aosmith@syr.edu>

Purpose:
    Prompt templates for GRAVITYbot LLM summarization tasks.
    Purpose:
        Prompt templates for GRAVITYbot LLM summarization tasks.

        - talk_prompt(): Summarizes Zooniverse Talk forum discussions for LIGO scientists
        - alog_prompt(): Summarizes aLOG posts for Gravity Spy volunteers
        - alog_prompt_legacy(): The original aLOG prompt, kept for comparison
"""

import json
import pathlib

import pandas as pd

import alog_index

DATA_DELIMITER = "~~~"

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


def talk_prompt(prior_data, current_data):
    """
    Constructs prompts for summarizing Zooniverse Talk forum discussions.

    Args:
        prior_data (pandas.DataFrame): Talk data from the prior week.
        current_data (pandas.DataFrame): Talk data from the current week.

    Returns:
        tuple: (user_prompt, sys_prompt) for the LLM.
    """
    user_prompt = f"""
The following data are citizen scientist ("volunteer") forum discussions of gravitational wave glitches from the Zooniverse Gravity Spy project. The data originally were in a dataframe of two columns. The first column was the "comment" text and the second was the "URL" affiliated with the comment. After each comment has been formatted such that it is followed by its URL.

Volunteers also attempt to identify underlying causes of each glitch. The forum data captures the evolving nature of glitch classification, glitch origins and characteristics by volunteers and researchers. The forum data emerges as a part of significant curiosity and engagement with the data, with the need for a clear summary.

Within the Zooniverse project Gravity Spy, there are existing well-defined glitch classifications that describe transient noise artifacts seen in data from LIGO's gravitational wave detectors. Use the existing Gravity Spy glitch classifications to compare to following datasets. These include the following:
1080 Line, 1400 Ripple, 70 Hz Line, Air Compressor (50 Hz), Blip, Chirp, Crown, Extremely Loud, Helix, Koi Fish, Low-Frequency Line, No Glitch, Paired Doves, Pizzicato, Power Line (60 Hz), Repeating Blips, Scattered Light, Scratchy, Tomte, Violin Mode Harmonic, Wandering Line, Whistle.

Consider "last week's" forum data:
{DATA_DELIMITER}
{format_data(prior_data)}
{DATA_DELIMITER}

Now consider "this week's" forum data:
{DATA_DELIMITER}
{format_data(current_data)}
{DATA_DELIMITER}

Using these two sets of data, please provide at least three bullet points to answer the following questions. Each bullet point requires a couple of sentences of response. For each major question please provide all relevant URLs in the final bullet for that major question following this format: [Reference Information](https://www.zooniverse.org/projects/zooniverse/gravity-spy/talk/6872/3685209) where "Reference Information" should be a description of 3 words or less.

I want a structured outline of what occurred in "this week's" forum data relative to "last week's" focusing on the following concerns:

1. EACH possible new glitch suggestion outlined in the following format. (NOTICE: There will likely be multiple glitch suggestions. Report all of them along with responding to the following concerns.)
    - What new glitch is suggested this week relative to last week?
    - Is this new suggested glitch being discussed anywhere else in the data?
    - How likely is the glitch already accounted for by a previous classification? New glitch "proposals" require more dedicated work than volunteer "suggestions," and most glitch suggestions do not result in a new glitch proposal. There could be long and detailed discussion about how a volunteer should interpret existing glitch classes in order to avoid confusion in the future for the volunteer. As such, the volume of references to the glitch suggestion does not matter. However, if there is general agreement that it is different enough, how so? If it is not new enough, how so?
    - PROVIDE EVERY RELATED COMMENT'S URL, including follow-up discussion, as a bulleted list. (I.E. IF THERE IS SIGNIFICANT DISCUSSION THERE SHOULD BE MULTIPLE URLs)
CONTINUE RESPONDING TO EACH OF THESE IN THE ABOVE FORMAT AS 1.1, 1.2, 1.3, ETC FOR EACH NEW GLITCH BEFORE ANSWERING ANY ADDITIONAL QUESTIONS!

2. Volunteers learn by exploring classifications and technical aspects of glitches. EXCLUDING RESPONSES RELATED TO CONCERN 1, answer the following bullet points with a final bullet with ALL RELEVANT URLs.
    - Are there emerging questions related to the glitch classes, sensors, or gravitational wave science in this week's data?
    - Describe each question and what motivated each question. Provide at two or three sentences describing these emerging questions.

3. Do volunteers have any hypotheses about the origins of glitches. LIGO gravitational wave glitches are fundamentally related to sensors, channel noise, and/or external ecological factors. Conclude with a bulleted list of ALL RELEVANT URLs.
    - Are there any conversation suggesting questions, hypothetical, or declarative origins of any glitch class? If so what are the hypotheses?
    - What reasons or rationale is provided?
    - Keeping in mind that most volunteers have very little practical engineering knowledge, how likely is what is being questioned, hypothesized, or declared to be true?
RESPONDING TO EACH HYPOTHESES/EXPLANATION PROVIDE THEM IN THE FORMAT 3.1, 3.2, 3.3, ETC BEFORE MOVING ON TO QUESTION 4!

4. I want to know if volunteers discuss possible technical issues with particular sensors or channels THAT ARE NOT RELATED TO CONCERN 3.
    - Are there any emerging comments or questions surrounding particular glitches' connections to sensors or channels this week relative to last week?
    - What specifically do these comments or questions describe?
    - Provide at least two sentences for these comments or questions.
    - Provide ALL relevant URLs.
    """.strip()

    sys_prompt = f"""
You are a technical interpreter who translates citizen science forum conversations for physicists and engineers who have very little time. As such, you are to provide your responses in as concise a way as possible with all relevant technical or descriptive detail.

When data is provided, you should expect it to be delimited by lines consisting only of '{DATA_DELIMITER}'.

Phrase interpretations with rhetoric like "an" (as opposed to "the") and "some" as opposed to "all" when referring to the data. This will avoid extremes when there is a lack of clarity.

Format all relevant hyperlinks without hashtags following this format:

[<Reference Information>](https://www.zooniverse.org/projects/zooniverse/gravity-spy/talk/6872/3685209)

where the placholder <Reference Information> should be a description of 3 words or less.
    """.strip()

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
    template_link_text = f"{lab}: {template_call_rep}"
    base_url = ALOG_BASE_URLS.get(lab, ALOG_BASE_URLS["LLO"])
    template_link_url = f"{base_url}/aLOG/index.php?callRep={template_call_rep}"

    user_prompt = f"""
The data involve discussions surrounding LIGO laboratory equipment. The data originally were in a dataframe of three columns. The first column was the url affiliated with a comment, the second column the comment title, and the final column the comment text.

Many of the acronyms relate to channels, sensors, equiptment, or other processes surrounding LIGO. Translate these acronyms to full words from the LIGO Abbreviations and Acronyms list or other LIGO documentation when possible. If there is no cooresponding entry in the LIGO Abbreviations and Acronyms, do not attempt to translate the acronym. Instead indicate that the acronym is unknown in a parenthetical statement.

Consider the Prior aLOG Dataset:
{DATA_DELIMITER}
{format_data(prior_data)}
{DATA_DELIMITER}

Now consider the Current aLOG Dataset:
{DATA_DELIMITER}
{format_data(current_data)}
{DATA_DELIMITER}

Provide responses for some the specific kinds of activities that are different for the current aLOG Dataset relative to the prior aLOG Dataset.

1. Are there unresolved issues related to particular equiptment that may cause a glitch in the gravitational wave data? What are these issues? For each unresolved issue, provide a bullet. Also provide a sentence or two explaining each issue in simple language. Please provide the URL that references back to the relevant aLOG conversation.

2. Were there alterations to particular equiptment?  Firstly, please note that in these alterations, use the language, numbers, or other specifications provided in the aLOG to avoid overgeneralization. For example, if the aLOG states "4 mirrors" were calibrated in some way explain what happened to the "4 mirrors." Secondly, please note that often alterations are calibrations in order to resolve issues such as glitches, and they do not necessarily create new glitches. Provide a bullet and a sentence or two explaining each modification in pedestrian language. Provide the URLs that reference back to the relevant aLOG conversation.

3. Where there external ecologial events, such as environmental issues, that were not about equiptment failures or modifications that might be related to glitches in gravitational wave data? For each event, provide a bullet and a sentence or two explaining each issue in pedestrian language. Provide the URLs that reference back to the relevant aLOG conversation.
    """.strip()

    sys_prompt = f"""
You are a LIGO engineer tasked with summarizing aLOG conversations for citizen scientists. The important conversations are about relevant engineering changes or events which may create glitches in gravitational wave data. Your goal is to help citizen scientists understand laboratory issues that will enable them to interpret Gravity Spy Glitch issues quickly. Use clear, simple language and avoid technical jargon to ensure accessibility. Translate acronyms to full words based upon LIGO Abbreviations and Acronyms. If there is no cooresponding entry in the LIGO Abbreviations and Acronyms, use the acronym as is. Note the missing information.

When data is provided, you should expect to be delimited by lines consisting only of spaces and '{DATA_DELIMITER}'.

Structure the summary logically, highlighting common or recent issues, and maintain a neutral, informative tone. Phrase interpretations with rhetoric like "an" (as opposed to "the") and "some" as opposed to "all" when referring to the data. When summarizing modifications, numbers, or measurements, use the precise language and numbers provided in the documentation to avoid generalizaiton.

Format URLs as markdown links. Extract the callRep parameter from the url <callRep> and reform the link using that parameter in the name using this pattern:

[{lab}: <callRep>]({template_link_url}).

For example, if the link's callRep parameter was {template_call_rep} the expected result would be

[{template_link_text}]({template_link_url}).
    """.strip()

    return user_prompt, sys_prompt


GLOSSARY_PATH = pathlib.Path(__file__).with_name("volunteer_glossary.md")


def _load_glossary():
    return GLOSSARY_PATH.read_text(encoding="utf-8").strip()


def alog_prompt(prior_data, current_data, lab):
    """
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

    sys_prompt = f"""
You write a weekly summary of the {lab} detector logbook (aLOG) for Gravity Spy volunteers. Volunteers look at glitches in the detector's data and try to classify them and understand what caused them. They are not detector experts.

Your job is to tell a volunteer what happened this week that could affect the data or explain glitches, and to explain each important item in plain words. Leave out work that does not affect the data.

INPUT
You get two datasets, each delimited by lines consisting only of spaces and '{DATA_DELIMITER}':
- Prior aLOG Dataset: the previous week, shortened to the start of each entry. Use it only to tell whether an issue is new, ongoing or fixed. Never report its events as this week's.
- Current aLOG Dataset: this week. Report only events that happened during this week.
Each entry has posted_utc (when the entry was posted, in UTC), comment_url, comment_title and comment. Entries titled "Comment to ..." are follow-ups to an earlier entry and often give the later diagnosis; use them.

FIRST, decide whether the detector was Observing at all this week.
- If it was not Observing at any time (for example a vent or a long planned-engineering period), start the summary with the line: "No Observing data this week: the detector was not taking science data, so no glitches from this week appear in Gravity Spy." Then use only these four headings, with at most 5 short bullets each: "## Detector status this week"; "## Data-quality findings" (lines, combs or noise reported by DetChar, with status); "## Outages, power events and earthquakes" (with dates and times; see ENVIRONMENT MENTIONS); "## Changes that may change the noise" (work that may change how the detector behaves once it returns to Observing). Leave out vacuum, pumpdown, calibration-hardware and computer work. Do not describe any effect on glitches for this week.

OTHERWISE, report under these headings, in this order:

## Detector status this week
- Whether the detector was Observing, and for roughly how long, if the logs say so.
- Long outages, maintenance, commissioning or vent periods, with dates.

## Locklosses
- Start from the LOCKLOSS INDEX in the user message. A script built it from entry titles and shift summaries, so check each line against the entries. Keep every index line in your list unless the entries show it is a duplicate, falls outside this week, or is not a lockloss; then add any lockloss the entries report that the index missed. Locklosses mentioned only in shift summaries count too.
- List each lockloss from low noise or Observing once, one line each: "YYYY-MM-DD HH:MM UTC: cause". Take the cause from the entry or its follow-up comments; if none is stated, write "no cause stated". Locklosses during lock acquisition may be counted together in one line.
- Then give the count, equal to the number of lines in the list, and a one-line breakdown by cause, for example "18 locklosses: 5 ETMX glitch, 2 wind, 1 earthquake, 10 no cause stated".

## Glitches and noise
- Glitch and noise sources that are present, suspected or newly fixed: what, when, which frequency band if stated, and the current status at the end of the week.

## Environment
- Earthquakes, wind, storms, high microseism, power outages or flickers, and human activity on site that affected the detector, with UTC times and magnitudes where given. ENVIRONMENT MENTIONS lists where the entries mention these.

## Tests and injections that leave marks in the data
- Calibration sweeps, hardware injections, PEM injections, excitations and deliberate noise or offset steps, with UTC times. KEY ENTRIES lists the entries whose titles mention these.
- Short drops out of Observing for tuning (for example squeezer tuning), with UTC start and end times.

## Data-quality (DetChar) report
- The DQ shift findings if a report was posted (see KEY ENTRIES): the period it covers, duty cycle, glitch-rate changes, noisy frequency bands and problem times.

## Changes that may change the noise
- Changes to the squeezer, damping, alignment, actuators, thermal compensation or calibration that plausibly change the noise or glitch behavior. Say plainly what changed and when.

Omit a heading that has nothing this week, except "Detector status this week" and "Locklosses": if the logs give no lockloss information, say so.

LEAVE OUT
Vacuum, cryopump and pressure work; facility, HVAC, chiller, electrical and IT work; computer, model, software and guardian-code changes; alarm tests; bench and lab tests of electronics; routine weekly checks; personnel and logistics. Include any of these only if the log says it affected the detector's data, lock or noise.

EXPLANATIONS FOR VOLUNTEERS
- For an important item that a non-expert would not understand, add one sentence starting with "What this means:". Skip it when the item is already clear. Never repeat the same explanation; explain a term once, at its first use.
- Explanations describe what can happen, using "can" or "may". Do not claim that data are unusable, that an event caused glitches, or that a glitch will appear, unless the log says so.
- Use the glossary below for terms that appear in this week's items. Do not add general LIGO background that is not tied to this week's events.
- Never present background knowledge as something that happened this week.

ACCURACY RULES
- Only report what the logs say. Do not state a cause, purpose or effect unless the log states it. If the log says a cause is unknown, suspected or ruled out, say exactly that.
- Keep each fact attached to the right equipment, location, date and time. Do not merge details from different entries or link separate events.
- Report the latest status: check later entries and follow-up comments before calling an issue unresolved or a task unfinished.
- Use the numbers, units, dates and names exactly as written in the logs.
- Give event times in UTC as written in the entry text. If only the posting time is known, write "posted at".
- Expand an acronym only if the glossary defines it or you are certain of the meaning. Otherwise keep the acronym as is, without a note.

STYLE
- Neutral, impersonal voice. No first person, and do not address the reader. No offers of follow-up work.
- One short bullet per item. Each fact appears once, under one heading.
- End after the last section. No closing recap, advice paragraph or list of "most relevant items".
- Cite every bullet with markdown links built from the callRep parameter of comment_url, in this pattern: {link}

GLOSSARY (plain-language explanations)
{_load_glossary()}
    """.strip()

    user_prompt = f"""
LOCKLOSS INDEX (built by a script; verify before use):
{alog_index.lockloss_index(current_data, lab)}

KEY ENTRIES (data-quality, calibration, injection, earthquake, power and weather entries, by title):
{alog_index.key_index(current_data, lab)}

ENVIRONMENT MENTIONS (earthquakes, power events, lightning and wind of 30 mph or more, found in entry text by a script; verify before use):
{alog_index.env_index(current_data, lab)}

Prior aLOG Dataset:
{DATA_DELIMITER}
{format_data(alog_index.brief(prior_data))}
{DATA_DELIMITER}

Current aLOG Dataset:
{DATA_DELIMITER}
{format_data(current_data)}
{DATA_DELIMITER}
    """.strip()

    return user_prompt, sys_prompt


def alog_postprocess(summary, period=None):
    """Remove instruction text or closing filler the model sometimes adds, and fold stray "Status:" lines into the bullet above.
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
    if period:
        text = re.sub(r"^(#+\s*Detector status this week)\b[^\n]*$", lambda m: f"{m.group(1)} ({period})", text, flags=re.M)
    return text
