# Working in this repository

Two coding agents change this repository: Claude Code, which works on a
`claude/*` branch and merges through pull requests, and Google Antigravity,
which commits directly to `main`. Either one may have changed the code since
you last saw it.

- Fetch `main` and start from its latest commit before making changes, and
  fetch again before you push or merge.
- Leave changes you did not make alone unless the user asks you to change
  them; if something looks wrong, say so instead of reverting it.

Frontend-specific rules live in `frontend/AGENTS.md`.

## Code map (graphify)

`graphify-out/` holds a graph of the backend and frontend code: every module,
class, function and component, with what calls, imports or extends what. Use it
to find code before reading files; it costs far fewer tokens than grepping and
opening whole files.

- Start a question about the code with `graphify query "<question>"`. It
  returns the relevant symbols with `file:line` in about 2,000 tokens. Use
  `graphify explain "<symbol>"` for one class or function, and
  `graphify path "<A>" "<B>"` for how two pieces connect. Then open only the
  lines it points to.
- Read `graphify-out/GRAPH_REPORT.md` only when you need the overall
  architecture.
- The graph can lag the code, so check the file before you edit it.
- After changing code, run `graphify update .` (a few seconds, no API cost) and
  commit `graphify-out/` along with your change. If `graphify-out/` conflicts in
  a merge, don't merge it by hand: take either side, then rerun
  `graphify update .`.
- If the `graphify` command is missing, install it with `pip install graphifyy`.
  If it can't be installed, work without it.
