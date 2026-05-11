# Keropin

**Claude의 답변 위에 직접 메모를 다는 후속 질문 도구**

> 웹 버전: [keropin.vercel.app](https://keropin.vercel.app/)

---

긴 답변을 읽다가 "이 부분이 무슨 뜻이지?"라는 생각이 들 때, 터미널에서 다시 맥락을 설명할 필요 없이 — 브라우저에서 해당 텍스트를 선택하고 메모를 달면 됩니다. Keropin이 메모의 위치와 맥락을 자동으로 Claude에게 전달합니다.

## How it works

```
/keropin TypeScript의 제네릭에 대해 설명해줘
```

1. Claude가 답변을 작성합니다
2. 답변이 복잡하거나 깊은 레이어를 가진 경우, Keropin UI를 열지 묻습니다
3. 브라우저에서 답변을 읽으며 궁금한 부분에 메모를 답니다
4. "Done" 클릭 → Claude가 각 메모에 정확히 답변합니다

## Setup

### Install

```bash
claude skill add /path/to/keropin-skill
```

### Permissions

이 skill을 설치한 뒤, 다음 권한을 허용해야 합니다:

- `Bash(python3:*)` — 서버 실행
- `Bash(open:*)` — 브라우저 열기
- `Bash(pkill -f "python3 server.py")` — 서버 종료
