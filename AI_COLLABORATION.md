# AI Collaboration Statement

## How AI Helped Build Page Pulse

I built Page Pulse as a deliberately defensible URL audit tool: a FastAPI backend for robust parsing and a Next.js 15 frontend wrapped in a warm, 90s retro-vintage aesthetic. AI tools were part of my workflow, but they were collaborators, not replacements for judgment.

### What I Used AI For

- **Backend boilerplate**: I used AI to accelerate the initial FastAPI route scaffolding, dependency lists, and the pytest fixture structure. This saved setup time and let me move quickly into the fault-tolerant parts of the system.
- **Frontend styling exploration**: I used AI to brainstorm Tailwind CSS patterns for the grain overlay, warm cinematic palette, and the serif-plus-monospace typography pairing. It helped me iterate faster on the retro look I already had in mind.
- **Documentation formatting**: AI assisted in structuring the README and this collaboration note, turning my design reasoning into clean, readable Markdown.

### What I Did Myself

- **Architecture and system reliability**: The strict error-handling boundaries between the Next.js frontend and the Python backend, the custom `AuditFetchError` class, the structured error contracts, and the decision to fail fast on non-HTML responses are all my own.
- **Parser logic and scoring**: The DOM traversal, the flat-field report model, the composite scoring algorithm, and the issue-collection heuristics were designed and tuned by me.
- **UI/UX direction**: The 90s retro aesthetic, the card dashboard layout, the score ring, and the exact footer requirement were intentional choices I drove from the start.
- **Testing strategy**: I decided to mock every external HTTP call and SSL handshake so the suite would be deterministic, fast, and safe for CI. I wrote the test cases and the fake `httpx` client myself.

### Why This Workflow Makes Sense

I see AI agents as force multipliers: they handle repetitive scaffolding and surface options, while I keep ownership of the decisions that affect reliability, user trust, and product feel. For Page Pulse, that meant spending my time on graceful failure modes, clear API contracts, and a UI that feels human rather than generic. The result is a tool I fully understand and can confidently maintain.
