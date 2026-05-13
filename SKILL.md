---
description: Claude의 답변 위에 직접 메모를 다는 후속 질문 도구. 긴 답변을 읽다가 궁금한 부분에 브라우저에서 메모를 달면, Keropin이 메모의 위치와 맥락을 자동으로 Claude에게 전달합니다. Use when the user invokes /keropin or asks to annotate a previous answer.
disable-model-invocation: true
allowed-tools: Bash(python3 *) Bash(python *) Bash(open http://localhost:*) Bash(start http://localhost:*) Bash(xdg-open http://localhost:*) Bash(rm -f /tmp/keropin_*) Bash(cat /tmp/keropin_*) Bash(while*keropin_export*) Bash(pkill -f*server.py*) Bash(kill *) Bash(taskkill *) Bash(sleep *) Read(/tmp/keropin_*) Write(/tmp/keropin_*)
---

The user invoked `/keropin`. This opens the **most recent Claude answer** in the Keropin UI so the user can highlight text and add inline memos (questions).

ARGUMENTS: $ARGUMENTS

IMPORTANT: Do NOT output step labels like "Step 0:", "Step 1:" etc. Just talk naturally.

## Step 1: Prepare the content

Find the most recent answer you gave in this conversation (the last substantial response before `/keropin` was invoked). Write that answer to `/tmp/keropin_response.md`.

If `$ARGUMENTS` is not empty, treat it as a NEW question: answer it thoroughly in the terminal first, THEN write that answer to `/tmp/keropin_response.md` and continue to Step 2.

IMPORTANT: To write `/tmp/keropin_response.md`, use the Write tool (not Bash). If the Write tool requires reading first, use the Read tool on `/tmp/keropin_response.md` to satisfy the read requirement, then use Write. If the file doesn't exist yet, use `cat /tmp/keropin_response.md` via Bash (no extra flags or pipes — just the bare cat command to match the permission pattern), then use Write.

> **Windows users**: On Windows, the Bash tool typically runs under Git Bash (MSYS), which maps `/tmp/` to `%TEMP%`. The server (`server.py`) uses `tempfile.gettempdir()` to resolve the same directory, so both paths refer to the same physical location. If the Write tool on Windows cannot resolve `/tmp/`, fall back to the absolute Windows temp path (e.g. `C:\Users\<you>\AppData\Local\Temp\keropin_response.md`).

## Step 2: Start the Keropin session

IMPORTANT: Each command below MUST be a separate, individual Bash tool call. NEVER combine commands with `&&`, `;`, newlines, or `&`. This ensures each command matches the registered permission patterns exactly.

1. Remove the export file (single command):
   ```
   rm -f /tmp/keropin_export.txt
   ```

2. Start the keropin server. Run this as a single background command:
   ```
   python3 ${CLAUDE_SKILL_DIR}/server.py
   ```
   Use `run_in_background: true` for this command.
   > **Windows**: If `python3` is not found, use `python` (or `py`) instead.

3. Wait for the server to start (single command):
   ```
   sleep 1
   ```

4. Read the server log to get the URL (single command):
   ```
   cat /tmp/keropin_server.log
   ```
   Capture the URL from the output.

5. Open the browser. Use the command appropriate for the current platform:
   - **macOS**: `open <URL>`
   - **Linux**: `xdg-open <URL>`
   - **Windows**: `start <URL>`

6. Tell the user: "Keropin이 열렸습니다. 텍스트를 선택하고 메모를 달아주세요. 다 되면 'Done - Send to Claude'를 클릭하세요."

7. Poll for the export file (single command, up to 5 minutes timeout):
   ```
   while [ ! -f /tmp/keropin_export.txt ]; do sleep 3; done
   ```

8. Once the file exists, read `/tmp/keropin_export.txt` using the Read tool (not Bash).

9. Answer each question in the export, using the Section and Paragraph context to understand exactly which part of the response the user is asking about. If the same word appears multiple times, use the paragraph context to disambiguate.

## Step 3: After answering follow-up questions
Ask the user:

"추가로 궁금한 부분이 있나요?
1. **Keropin으로 계속** — 지금 답변을 Keropin UI에 다시 띄워서 메모를 달 수 있어요.
2. **여기서 계속** — 서버를 종료하고 터미널에서 대화를 이어가요."

- If **option 1**: Write the follow-up answers to `/tmp/keropin_response.md`, remove the export file, and repeat from Step 2.6 (tell user → poll → read → answer). Do NOT restart the server if it's already running.
- If **option 2**: Stop the server. The server writes its PID to `/tmp/keropin_server.pid`, so use that for a precise, cross-platform termination:
  - **macOS/Linux**: `kill $(cat /tmp/keropin_server.pid)`
  - **Windows**: `taskkill //F //PID $(cat /tmp/keropin_server.pid)`

  Then continue in the terminal.
