# Prompt files

The texts sent to the model live here, so they can be edited without changing code.
Each prompt has two parts:
- **System prompt** (`*_system.md`): the standing instructions, such as who the summary is for, which sections to write, and the rules.
- **User prompt** (`*_user.md`): this week's data, with the script-built lists placed in front of it.

| File | Used by |
|---|---|
| `alog_interface_system.md`, `alog_interface_user.md` | aLOG summary, interface prompt (the default) |
| `alog_volunteer_system.md`, `alog_volunteer_user.md` | aLOG summary, first volunteer prompt |
| `alog_legacy_system.md`, `alog_legacy_user.md` | aLOG summary, original prompt |
| `talk_system.md`, `talk_user.md` | Talk forum summary |

`GRAVITYBOT_ALOG_PROMPT` in the `.env` file picks the aLOG prompt: `interface`, `volunteer` or `legacy`.

## Background files (one folder up, in `resources/`)
- `glitch_classes.md`: the Gravity Spy glitch classes and what each looks like. It is inserted at `{{glitch_classes}}`.
- `volunteer_glossary.md`: plain explanations of detector terms. It is inserted at `{{glossary}}`.

## Placeholders
`{{name}}` marks where the code fills in a value when the prompt is built. Keep each placeholder's name exactly as it is. A placeholder can be moved or deleted, but a new name needs a matching value in `prompts.py`; otherwise the bot stops with an error instead of sending the placeholder to the model.

| Placeholder | Filled with |
|---|---|
| `{{lab}}` | LHO or LLO |
| `{{link}}`, `{{template_link_text}}`, `{{template_link_url}}`, `{{template_call_rep}}` | an example citation link for the lab's aLOG |
| `{{data_delimiter}}` | `~~~`, the line that marks where each dataset starts and ends |
| `{{prior_data}}`, `{{current_data}}` | last week's and this week's entries |
| `{{locklosses_per_day}}`, `{{lockloss_index}}`, `{{key_entries}}`, `{{environment_mentions}}` | lists built by `alog_index.py` |
| `{{acronyms}}` | this week's acronyms, from `alog_acronyms.py` |
| `{{glitch_classes}}`, `{{glossary}}` | the background files above |
