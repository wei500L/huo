import { PixelCard } from "@/components/pixel";
import type { PromiseDTO } from "@/protocol/types";
import { useGameStore } from "@/store/gameStore";

import { PromiseRow } from "./PromiseRow";

interface Props {
  promises: PromiseDTO[];
  rating?: string;
  expectedReturnPerQuarter?: number;
}

const formatMoney = (value: number): string => {
  const sign = value >= 0 ? "+" : "-";
  return `${sign}¥${Math.abs(value).toLocaleString("zh-CN")}/季度`;
};

export const PromiseLedger = ({ promises, rating = "B+", expectedReturnPerQuarter = 12000 }: Props) => {
  const pushToast = useGameStore((state) => state.pushToast);
  const visiblePromises = promises.slice(0, 4);

  return (
    <PixelCard className="h-full min-h-[520px]" kind="default" title="画饼总账">
      <div className="flex h-full flex-col gap-px-lg">
        <section className="border-b-2 border-stroke-ink pb-px-md">
          <div className="text-px-sm text-ink-2">当前画饼评级</div>
          <div className="mt-px-sm font-retro text-px-xxl leading-none text-exp-gold">{rating}</div>
          <div className="mt-px-md text-px-sm text-ink-2">预期收益</div>
          <div className="font-retro text-[13px] leading-tight text-pixel-green">
            {formatMoney(expectedReturnPerQuarter)}
          </div>
        </section>

        <section className="min-h-0 flex-1">
          <div className="mb-px-sm flex items-center justify-between">
            <h3 className="font-retro text-[10px] leading-none text-ink-1">你说过的话</h3>
            <span className="font-retro text-[10px] text-ink-3">({visiblePromises.length}/4)</span>
          </div>

          <div className="space-y-px-xs">
            {visiblePromises.map((promise) => (
              <PromiseRow key={promise.id} promise={promise} />
            ))}
          </div>
        </section>

        <button
          type="button"
          className="mt-auto border-t-2 border-stroke-ink pt-px-md text-left font-retro text-[10px] leading-none text-pixel-blue hover:text-ink-1"
          onClick={() =>
            pushToast({
              id: `promise-ledger-history-${Date.now()}`,
              level: "info",
              message: "历史记录 v2 即将开放",
            })
          }
        >
          查看更多历史记录 →
        </button>
      </div>
    </PixelCard>
  );
};
