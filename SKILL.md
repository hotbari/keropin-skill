# Keropin

**Claude의 답변 위에 직접 메모를 다는 후속 질문 도구**

긴 답변을 읽다가 "이 부분이 무슨 뜻이지?"라는 생각이 들 때, 터미널에서 다시 맥락을 설명할 필요 없이 — 브라우저에서 해당 텍스트를 선택하고 메모를 달면 됩니다. Keropin이 메모의 위치와 맥락을 자동으로 Claude에게 전달합니다.

### How it works

```
/keropin TypeScript의 제네릭에 대해 설명해줘
```

1. Claude가 답변을 작성합니다
2. 답변이 복잡하거나 깊은 레이어를 가진 경우, Keropin UI를 열지 묻습니다
3. 브라우저에서 답변을 읽으며 궁금한 부분에 메모를 답니다
4. "Done" 클릭 → Claude가 각 메모에 정확히 답변합니다

### Setup

이 skill을 설치한 뒤, 다음 권한을 허용해야 합니다:

- `Bash(python3:*)` — 서버 실행
- `Bash(open:*)` — 브라우저 열기
- `Bash(pkill -f "python3 server.py")` — 서버 종료

---

## Prompt

You received a question from the user via the /keropin command.

ARGUMENTS: $ARGUMENTS

Follow these steps:

### Step 1: Assess complexity (BEFORE writing the answer)
Read the user's question and evaluate whether your answer is likely to be complex. Consider:

- Does the topic cover multiple concepts that each need deeper explanation?
- Will the answer include technical terms or jargon?
- Will the answer be long with distinct sections?
- Does the topic have layers of depth beyond the surface explanation?

### Step 2: Branch based on complexity

**If the answer is SIMPLE** (few follow-up questions expected):
Just answer the question normally in markdown. Done.

**If the answer is COMPLEX** (many follow-up questions expected):
Do NOT write the answer yet. Instead, tell the user:
"이 질문은 답변이 길어질 것 같아요. Keropin을 열어서 답변을 읽으면서 궁금한 부분에 바로 메모를 달아볼까요?"
Then STOP and wait for the user's response.

### Step 3: Based on user's response

**If the user declines Keropin (or says just answer here):**
Answer the question normally in markdown. Done.

**If the user agrees to open Keropin:**

#### Starting a Session

1. Compose your full answer internally but do NOT output it to the terminal. Instead, write it directly to `/tmp/keropin_response.md`.

2. Remove the export file: `rm -f /tmp/keropin_export.txt`

3. Start the keropin server in the background:
   ```
   python3 /Users/yeonsu/2026/keropin-skill/server.py > /tmp/keropin_server.log 2>&1 &
   sleep 1
   cat /tmp/keropin_server.log
   ```
   The server prints a URL like `http://localhost:XXXXX`. Capture this URL.

4. Open the browser: `open <URL>`

5. Tell the user: "Keropin이 열렸습니다. 텍스트를 선택하고 메모를 달아주세요. 다 되면 'Done - Send to Claude'를 클릭하세요."

6. Poll for the export file every 3 seconds (up to 5 minutes):
   ```
   while [ ! -f /tmp/keropin_export.txt ]; do sleep 3; done
   ```

7. Once the file exists, read `/tmp/keropin_export.txt`.

8. Answer each question in the export, using the Section and Paragraph context to understand exactly which part of the response the user is asking about. If the same word appears multiple times, use the paragraph context to disambiguate.

#### After Answering Follow-up Questions

After answering all inline questions, ask the user:

"추가로 궁금한 부분이 있나요?
1. **Keropin으로 계속** — 지금 답변을 Keropin UI에 다시 띄워서 메모를 달 수 있어요.
2. **여기서 계속** — 서버를 종료하고 터미널에서 대화를 이어가요."

- **Option 1**: Write the follow-up answers to `/tmp/keropin_response.md`, remove the export file (`rm -f /tmp/keropin_export.txt`), and repeat from step 5 (tell user to add memos → poll → read → answer). Do NOT restart the server if it's already running.
- **Option 2**: Stop the server (`pkill -f "python3 server.py"`) and continue the conversation normally in the terminal.
