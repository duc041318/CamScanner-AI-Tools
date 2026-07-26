# CamScanner-AI-Tools

Personal toolkit for a real-estate broker business (đất nền / land-lot sales in Sóc Sơn, Hà Nội). The repo mixes business documents (pricing plans, Zalo post templates) with a Python desktop automation tool for Zalo.

## Repo layout

- `zalo-tool/` — the only code project in this repo. A Tkinter desktop app that automates Zalo PC via UI automation (no official Zalo API).
- `ke-hoach-ban-dat-30-ngay.txt`, `mau-bai-dang-zalo.txt` — business content (30-day sales plan, message/post templates) for the Sóc Sơn land-lot listings. Reference these when drafting Zalo copy so tone and facts (lot sizes, prices, location) stay consistent.
- `.claude/agents/`, `.claude/skills/` — a broad, mostly generic set of subagents/skills (marketing, legal, fintech, OCR, web3, etc.) installed for this account, not curated specifically for this repo. Only a few are actually relevant here: `python-pro`, `debugger`, `code-reviewer`, `document-structure-analyzer`/`ocr-*` (if OCR work resumes), `content-marketer`/`social-media-copywriter` (for Zalo post copy). Don't assume the rest apply.

## `zalo-tool/`

Automates three flows against the Zalo PC desktop client using `pyautogui` + `pywinauto` (UI automation, not an API — Zalo must be open and logged in):

- `features/bulk_message.py` — send a templated message (+ optional image) to a list of phone numbers.
- `features/auto_post.py` — post to Zalo Timeline (Nhật ký), either immediately or on a schedule (`schedule` lib polling loop).
- `features/add_friend.py` — send friend requests from a phone list, with a persisted daily quota (`data/daily_friend_count.json`).
- `utils/zalo_controller.py` — all the raw UI automation (click coordinates relative to the main window, clipboard-based text entry for Vietnamese input support, PowerShell clipboard tricks for pasting images/files).
- `utils/file_reader.py` — reads `.txt` (one phone per line) or `.csv` (header `sdt` + extra template variables) contact lists; `apply_template()` does `{key}` substitution.
- `utils/logger.py` — every action logs a row to `logs/<feature>_<date>.csv`.
- `main.py` — the Tkinter GUI (4 tabs: bulk message, auto post, add friend, view log). Run with `python main.py` from `zalo-tool/`.

### Conventions to follow

- UI text, docstrings, and log messages are in Vietnamese — keep new code consistent with that.
- Every long-running feature (`BulkMessageSender`, `AutoPoster`, `FriendAdder`) follows the same shape: runs in a daemon `threading.Thread`, uses a `threading.Event` (`stop_event`) for cancellation, takes `progress_callback`/`status_callback` for GUI updates, and logs each item via `Logger`. Match this pattern when adding a new automated flow instead of inventing a new one.
- Random delays between actions (`random.uniform(min, max)`) are intentional (anti-spam-detection pacing) — don't remove them when refactoring.
- Message/post templates use `{ho_ten}`, `{du_an}`, `{gia}`, `{dien_tich}` as the standard variable names (see `mau-bai-dang-zalo.txt`); reuse these names rather than inventing new placeholders.
- No test suite exists. The core logic (`utils/zalo_controller.py`) drives real UI coordinates on a live Zalo window, so it can't be meaningfully unit-tested without a running Zalo instance — keep new logic in `utils/file_reader.py`-style pure functions testable where possible, and note UI-dependent code isn't covered.
- Dependencies are pinned in `zalo-tool/requirements.txt` (Windows-only: `pywinauto`, `pyautogui`). This tool only runs on Windows with Zalo PC installed.

## Working in this repo

- When asked to add a new Zalo automation feature, follow the existing `features/*.py` pattern and wire it into a new tab in `main.py`.
- When asked for Zalo post/message copy, check `mau-bai-dang-zalo.txt` and `ke-hoach-ban-dat-30-ngay.txt` first for the actual lot details and existing tone, rather than inventing generic real-estate copy.
- Recurring manual tasks (e.g., generating a new batch of message variations, drafting a listing report) are good candidates for a `.claude/skills/` skill — see `bao-gia-dat-nen` for the existing pattern.
