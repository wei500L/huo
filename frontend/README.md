# YES, BOSS! v2 Frontend

Pixel-art React shell for the v2 client of `YES, BOSS!`, wired for later WebSocket backend sync.

`v1` stays in the repo root as the plain DOM fallback. This `frontend/` tree is the new pixel UI shell only.

Bootstrap intent:
`pnpm create vite@latest frontend --template react-ts`
This scaffold is authored directly here, so the command above is documentation only.

## Run

```bash
cd frontend
pnpm install
pnpm dev
pnpm test
pnpm lint
pnpm typecheck
```

## Data Source

Set `VITE_DATA_SOURCE=mock` for local mock mode or `VITE_DATA_SOURCE=ws` for WebSocket mode.
Mock first, then backend integration is handled by task 5 + task 22.

## Fonts

Download Fusion Pixel from:
https://github.com/TakWolf/fusion-pixel-font

Place the font at:
`frontend/public/fonts/fusion-pixel-12px-monospaced-zh_hans.woff2`

## 8bitcn-ui

Add components with the shadcn CLI targeting the configured 8bit path:

```bash
cd frontend
pnpm dlx shadcn@latest add @8bitcn/button
```

The generated files should land under `src/components/ui/8bit/`.

## Notes

- No backend is started from this project.
- No real LLM calls are used here.
- `main.tsx` stays render-only.
