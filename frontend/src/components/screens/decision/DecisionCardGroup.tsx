import { useEffect } from "react";
import clsx from "clsx";

import { PixelCard, PixelIcon, type IconName, type Variant } from "@/components/pixel";
import type { DecisionCardDTO, StatsDTO } from "@/protocol/types";

interface Props {
  cards: DecisionCardDTO[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

type MetricKey = keyof StatsDTO;

const CATEGORY_STYLE: Record<string, { color: Variant; icon: IconName; label: string }> = {
  finance: { color: "blue", icon: "handshake", label: "融资方案" },
  people: { color: "orange", icon: "scissors", label: "组织方案" },
  pr: { color: "red", icon: "megaphone", label: "公关方案" },
  brand: { color: "red", icon: "megaphone", label: "公关方案" },
};

const METRICS: Array<{ key: MetricKey; icon: IconName; label: string }> = [
  { key: "CASH", icon: "money", label: "现金流" },
  { key: "MORALE", icon: "morale", label: "士气" },
  { key: "BOARD", icon: "board", label: "董事会信任" },
  { key: "FACE", icon: "face", label: "公司体面" },
];

const isEditableTarget = (target: EventTarget | null): boolean => {
  return target instanceof HTMLElement
    ? Boolean(target.closest("input,textarea,select,[contenteditable='true']"))
    : false;
};

const getCardStyle = (card: DecisionCardDTO) =>
  CATEGORY_STYLE[card.category] ?? { color: "orange" as const, icon: "target" as const, label: card.category };

const formatDelta = (key: MetricKey, value = 0): string => {
  const sign = value > 0 ? "+" : "";
  if (key === "CASH") {
    return `${sign}${value >= 0 ? "¥" : "-¥"}${Math.abs(value).toLocaleString("zh-CN")}`;
  }

  return `${sign}${value}`;
};

export const DecisionCardGroup = ({ cards, selectedId, onSelect }: Props) => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey || isEditableTarget(event.target)) {
        return;
      }

      const index = Number.parseInt(event.key, 10) - 1;
      const card = cards[index];
      if (!card || index < 0 || index > 2) {
        return;
      }

      event.preventDefault();
      onSelect(card.id);
    };

    window.addEventListener("keydown", handleKeyDown, true);
    return () => window.removeEventListener("keydown", handleKeyDown, true);
  }, [cards, onSelect]);

  return (
    <div className="grid grid-cols-1 gap-px-lg lg:grid-cols-3" role="radiogroup" aria-label="季度决策">
      {cards.slice(0, 3).map((card, index) => {
        const style = getCardStyle(card);
        const selected = selectedId === card.id;
        const dimmed = Boolean(selectedId && !selected);

        return (
          <PixelCard
            key={card.id}
            className={clsx("min-h-[360px]", selected && "border-exp-gold")}
            dimmed={dimmed}
            kind="decision"
            selected={selected}
            title={`${index + 1}. ${style.label}`}
            titleColor={style.color}
            onClick={() => onSelect(card.id)}
          >
            <div
              aria-checked={selected}
              className="flex h-full flex-col gap-px-md"
              role="radio"
              tabIndex={-1}
            >
              <div className="flex items-start gap-px-md">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim">
                  <PixelIcon color="currentColor" name={style.icon} size={48} />
                </span>
                <div className="min-w-0">
                  <h3 className="text-px-md leading-tight text-ink-1">{card.title}</h3>
                  <p className="mt-px-sm text-px-sm leading-normal text-ink-2">{card.description}</p>
                </div>
              </div>

              <div className="mt-auto border-t-2 border-stroke-ink pt-px-md">
                <div className="mb-px-sm font-retro text-[10px] leading-none text-ink-2">效果预览:</div>
                <div className="space-y-px-sm">
                  {METRICS.map((metric) => {
                    const value = card.immediateEffect[metric.key] ?? 0;
                    return (
                      <div key={metric.key} className="flex items-center gap-px-sm text-px-sm">
                        <PixelIcon name={metric.icon} size={16} />
                        <span className="min-w-0 flex-1 truncate text-ink-2">{metric.label}</span>
                        <span className={clsx("font-retro text-[10px]", value >= 0 ? "text-pixel-green" : "text-pixel-red")}>
                          {formatDelta(metric.key, value)}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </PixelCard>
        );
      })}
    </div>
  );
};
