---
description: Claude의 답변 위에 직접 메모를 다는 후속 질문 도구. 긴 답변을 읽다가 궁금한 부분에 브라우저에서 메모를 달면, Keropin이 메모의 위치와 맥락을 자동으로 Claude에게 전달합니다. Use when the user invokes /keropin or asks to annotate a previous answer.
disable-model-invocation: true
allowed-tools: Bash(python3 *) Bash(open http://localhost:*) Bash(rm -f /tmp/keropin_*) Bash(cat /tmp/keropin_*) Bash(while*keropin_export*) Bash(pkill -f*server.py*) Bash(sleep *) Read(/tmp/keropin_*) Write(/tmp/keropin_*)
---

The user invoked `/keropin`. This opens the **most recent Claude answer** in the Keropin UI so the user can highlight text and add inline memos (questions).

ARGUMENTS: $ARGUMENTS

IMPORTANT: Do NOT output step labels like "Step 0:", "Step 1:" etc. Just talk naturally.

## Answering principle (read before Step 2.9)

The fact that `/keropin` was invoked is itself a signal that the **previous answer was too difficult for the user**. So when answering follow-up questions, do not simply supplement that specific part. Re-explain it from one level lower.

**Audience setting and tone**
- Assume the audience is a 17-year-old learner. Treat them as having almost no prior knowledge of the field.
- Minimize metaphors. Instead of escaping into analogies, explain step by step how the concept actually works.
- Write in a flowing storyline format. Avoid dictionary-like structures such as definition → list → conclusion. Instead, make it flow naturally, like: “At first there was this problem → so people created this → and now it works like this.”

**What should be filled in — answers that bridge the gaps**
The user’s question is only the tip of the iceberg. Infer the *missing assumptions, context, and terminology* between the user and the question they asked, fill those gaps first, and then answer the question. In particular, try to include these four things whenever possible:
1. **Origin** — Where did this concept/tool/pattern come from, and why was it created?
2. **Problem it tried to solve** — What difficulties did people face before it existed?
3. **Connection to the bigger picture** — Where does this fit inside the overall system or ecosystem?
4. **Immediate explanation of new terms** — If an unfamiliar word appears, explain it on the spot before moving to the next sentence.

**Judging the user’s level and adjusting depth**
The user’s follow-up question itself is diagnostic data.
- If the question is like “What does this word mean?” → restart from terminology and origin.
- If the question is like “Why B instead of A?” → the user understands the concept itself but not the reason for the choice, so answer through comparison with alternatives.
- If `/keropin` is invoked a second or third time within the same topic area, break things down into even smaller units. Do not repeat the same explanation at the same depth.


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
   python3 ${CLAUDE_SKILL_DIR}/server.py
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
