export interface Props {
  value: string;
  onChange: (v: string) => void;
  minWords: number;
  maxWords: number;
}

const countUnits = (value: string): number => value.replace(/\s+/g, "").length;

const getToneClass = (count: number, minWords: number, maxWords: number): string => {
  if (count > maxWords) {
    return "text-pixel-red";
  }

  if (count >= Math.max(minWords, Math.floor(maxWords * 0.9))) {
    return "text-pixel-orange";
  }

  if (count >= minWords) {
    return "text-pixel-green";
  }

  return "text-ink-3";
};

export function PressTranscriptInput({ value, onChange, minWords, maxWords }: Props) {
  const count = countUnits(value);
  const toneClass = getToneClass(count, minWords, maxWords);
  const statusLabel =
    count < minWords ? "再说点" : count > maxWords ? "超出上限" : count >= Math.max(minWords, Math.floor(maxWords * 0.9)) ? "接近上限" : "可提交";

  return (
    <section className="border-2 border-stroke-ink bg-panel shadow-hard">
      <div className="border-b-2 border-stroke-ink bg-pixel-orange px-px-md py-px-sm text-white">
        <h2 className="text-px-md leading-none">发言稿</h2>
      </div>

      <div className="space-y-px-sm p-px-md">
        <textarea
          aria-label="发言稿输入框"
          className="min-h-[156px] w-full resize-none border-2 border-stroke-ink bg-panel px-px-md py-px-sm text-px-md leading-normal text-ink-1 shadow-[4px_4px_0_0_var(--stroke-ink)] outline-none placeholder:text-ink-3 focus:bg-panel-dim"
          placeholder="新官上任要说什么？"
          rows={6}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Escape") {
              return;
            }
          }}
        />

        <div className="flex flex-wrap items-center justify-between gap-px-sm text-px-sm leading-none">
          <span className={toneClass}>
            字数 {count}/{maxWords}
          </span>
          <span className="text-ink-2">{statusLabel}</span>
        </div>
      </div>
    </section>
  );
}

export default PressTranscriptInput;
