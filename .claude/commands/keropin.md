The user invoked `/keropin`. This opens the **most recent Claude answer** in the Keropin UI so the user can highlight text and add inline memos (questions).

ARGUMENTS: $ARGUMENTS

IMPORTANT: Do NOT output step labels like "Step 0:", "Step 1:" etc. Just talk naturally.

## Step 0: Check permissions (first run only)
Check if `.claude/settings.json` exists and already contains keropin permissions.

- If it does → skip to Step 1.
- If it does NOT → ask:

  "Keropin이 원활하게 동작하려면 아래 bash 명령어들을 자동 허용해야 합니다:
  - `python3 server.py` (서버 시작)
  - `open http://localhost:*` (브라우저 열기)
  - `rm -f /tmp/keropin_*` (임시 파일 정리)
  - `cat /tmp/keropin_*` (로그/파일 읽기)
  - polling 루프 (export 파일 대기)
  - `pkill` (서버 종료)

  `.claude/settings.json`에 등록할까요? (y/n)"

  Then STOP and wait for the user's response.

- If **yes**: Create or update `.claude/settings.json` with:
  ```json
  {
    "permissions": {
      "allow": [
        "Bash(python3 server.py*)",
        "Bash(open http://localhost:*)",
        "Bash(rm -f /tmp/keropin_*)",
        "Bash(cat /tmp/keropin_*)",
        "Bash(while*keropin_export*)",
        "Bash(pkill -f*server.py*)",
        "Bash(sleep *)",
        "Read(/tmp/keropin_*)",
        "Write(/tmp/keropin_*)"
      ]
    }
  }
  ```
  Merge with existing settings if the file already exists.
  Tell the user: "권한이 등록되었습니다. 적용하려면 세션 재시작이 필요합니다. `/keropin`을 다시 실행해주세요."
  Then STOP. Do NOT proceed to Step 1.

- If **no**: Continue to Step 1 (the user will approve each command manually).

## Step 1: Prepare the content

Find the most recent answer you gave in this conversation (the last substantial response before `/keropin` was invoked). Write that answer to `/tmp/keropin_response.md`.

If `$ARGUMENTS` is not empty, treat it as a NEW question: answer it thoroughly in the terminal first, THEN write that answer to `/tmp/keropin_response.md` and continue to Step 2.

IMPORTANT: To write `/tmp/keropin_response.md`, use the Write tool (not Bash). If the Write tool requires reading first, use the Read tool on `/tmp/keropin_response.md` to satisfy the read requirement, then use Write. If the file doesn't exist yet, use `cat /tmp/keropin_response.md` via Bash (no extra flags or pipes — just the bare cat command to match the permission pattern), then use Write.

## Step 2: Start the Keropin session

IMPORTANT: Each command below MUST be a separate, individual Bash tool call. NEVER combine commands with `&&`, `;`, newlines, or `&`. This ensures each command matches the registered permission patterns exactly.

1. Remove the export file (single command):
   ```
   rm -f /tmp/keropin_export.txt
   ```

2. Start the keropin server. Run this as a single background command:
   ```
   python3 server.py
   ```
   Use `run_in_background: true` for this command.

3. Wait for the server to start (single command):
   ```
   sleep 1
   ```

4. Read the server log to get the URL (single command):
   ```
   cat /tmp/keropin_server.log
   ```
   Capture the URL from the output.

5. Open the browser (single command):
   ```
   open <URL>
   ```

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
- If **option 2**: Stop the server with a single command: `pkill -f "python3.*server.py"` and continue in the terminal.
