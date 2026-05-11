You received a question from the user via the /keropin command.

ARGUMENTS: $ARGUMENTS

Follow these steps:

## Step 1: Answer the question
Answer the user's question thoroughly in markdown. Write your full answer as you normally would.

## Step 2: Assess complexity
After writing your answer, evaluate whether the answer is likely to generate many follow-up questions. Consider:
- Does the answer cover multiple concepts that each need deeper explanation?
- Are there technical terms or jargon that the user might want clarified?
- Is the answer long with distinct sections the user might want to drill into?
- Does the topic have layers of depth beyond the surface explanation?

## Step 3: Branch based on complexity

### If the answer is SIMPLE (few follow-up questions expected):
- Just show the answer as normal text. Done.

### If the answer is COMPLEX (many follow-up questions expected):
- After your answer, ask the user:
  "이 답변에 추가 질문이 있을 수 있을 것 같아요. keropin을 열어서 궁금한 부분에 직접 메모를 달아볼까요?"
- Then STOP and wait for the user's response.

## Step 4: If the user agrees to open keropin
Only proceed with these steps after the user says yes:

1. Write your answer (the full markdown from Step 1) to `/tmp/keropin_response.md`.

2. Remove the export file: `rm -f /tmp/keropin_export.txt`

3. Start the keropin server in the background:
   ```
   KEROPIN_DIR=$(find ~/.claude -type f -name "server.py" -path "*/keropin*/server.py" -exec dirname {} \; 2>/dev/null | head -1)
   python3 "$KEROPIN_DIR/server.py"
   ```
   The server prints a URL like `http://localhost:XXXXX`. Capture this URL.

4. Open the browser: `open <URL>`

5. Tell the user: "keropin이 열렸습니다. 텍스트를 선택하고 메모를 달아주세요. 다 되면 'Done - Send to Claude'를 클릭하세요."

6. Poll for the export file every 3 seconds (up to 5 minutes):
   ```
   while [ ! -f /tmp/keropin_export.txt ]; do sleep 3; done
   ```

7. Once the file exists, read `/tmp/keropin_export.txt`.

8. Stop the server (kill the background process).

9. Answer each question in the export, using the Section and Paragraph context to understand exactly which part of the response the user is asking about. If the same word appears multiple times, use the paragraph context to disambiguate.
