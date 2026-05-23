import { PRESS_REPORTERS } from "./constants";

type Tone = "neutral" | "friendly" | "hostile" | "mocking";

export interface ReporterListProps {
  items?: { outlet: string; tone: Tone }[];
}

const TONE_META: Record<Tone, { label: string; dot: string }> = {
  neutral: { label: "中性", dot: "bg-ink-3" },
  friendly: { label: "友好", dot: "bg-pixel-green" },
  hostile: { label: "敌意", dot: "bg-pixel-red" },
  mocking: { label: "嘲讽", dot: "bg-pixel-orange" },
};

export function ReporterList({ items = [...PRESS_REPORTERS] }: ReporterListProps) {
  return (
    <section className="border-2 border-stroke-ink bg-panel shadow-hard">
      <div className="border-b-2 border-stroke-ink bg-pixel-green px-px-md py-px-sm text-white">
        <h2 className="text-px-md leading-none">在场记者</h2>
      </div>

      <ul className="space-y-px-xs px-px-md py-px-md">
        {items.slice(0, 5).map((item) => {
          const meta = TONE_META[item.tone];
          return (
            <li key={item.outlet} className="flex items-center gap-px-sm border-2 border-panel-dim bg-panel-dim px-px-sm py-px-sm text-px-sm leading-none">
              <span aria-hidden="true" className={`h-3 w-3 shrink-0 border-2 border-stroke-ink ${meta.dot}`} />
              <span className="min-w-0 flex-1 truncate text-ink-1">{item.outlet}</span>
              <span className="shrink-0 font-retro text-[10px] text-ink-2">{meta.label}</span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export default ReporterList;
