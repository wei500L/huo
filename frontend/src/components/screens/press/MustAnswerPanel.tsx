export interface MustAnswerPanelProps {
  items: string[];
  transcript?: string;
}

const normalize = (value: string): string => value.toLowerCase().replace(/\s+/g, "");
const CIRCLED = ["①", "②", "③"] as const;

const isMatched = (item: string, transcript: string): boolean => {
  const source = normalize(transcript);
  return source.includes(normalize(item));
};

export function MustAnswerPanel({ items, transcript = "" }: MustAnswerPanelProps) {
  return (
    <section className="border-2 border-stroke-ink bg-panel shadow-hard">
      <div className="border-b-2 border-stroke-ink bg-pixel-blue px-px-md py-px-sm text-white">
        <h2 className="text-px-md leading-none">必答问题</h2>
      </div>

      <ol className="space-y-px-xs px-px-md py-px-md">
        {items.slice(0, 3).map((item, index) => {
          const matched = isMatched(item, transcript);
          return (
            <li
              key={`${index}-${item}`}
              className={[
                "flex gap-px-sm border-2 px-px-sm py-px-sm text-px-sm leading-normal",
                matched ? "border-pixel-green bg-panel text-pixel-green" : "border-panel-dim bg-panel-dim text-ink-3",
              ].join(" ")}
            >
              <span className="w-6 shrink-0 text-center font-retro leading-none">{CIRCLED[index] ?? "①"}</span>
              <span className="min-w-0 flex-1 break-words">{item}</span>
              <span className="shrink-0 font-retro leading-none">{matched ? "✅ 已命中" : "⬜ 未命中"}</span>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

export default MustAnswerPanel;
