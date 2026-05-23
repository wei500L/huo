# Add 8bit Components

Run these commands in the frontend workspace:

```sh
pnpm dlx shadcn@latest add @8bitcn/button
pnpm dlx shadcn@latest add @8bitcn/card
pnpm dlx shadcn@latest add @8bitcn/dialog
```

The generated files should land at:

- `src/components/ui/8bit/button.tsx`
- `src/components/ui/8bit/card.tsx`
- `src/components/ui/8bit/dialog.tsx`

This task does not execute the CLI.

If the generated components are unavailable or the command fails, `PixelButton`, `PixelCard`, and `PixelDialog` fall back to the local compatibility layer in `src/components/ui/8bit/index.tsx`.
