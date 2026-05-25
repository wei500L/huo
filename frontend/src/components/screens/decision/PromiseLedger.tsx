import { PixelCard } from "@/components/pixel";
import type { PromiseDTO } from "@/protocol/types";

import { PromiseRow } from "./PromiseRow";

interface Props {
  promises: PromiseDTO[];
}

export const PromiseLedger = ({ promises }: Props) => {
  const visiblePromises = promises.slice(0, 4);

  return (
    <PixelCard className="h-full min-h-[420px] lg:min-h-[520px]" kind="default" title="画饼总账">
      <div className="flex h-full flex-col gap-px-lg">
        <section className="border-b-2 border-stroke-ink pb-px-md">
          <div className="text-px-sm text-ink-2">后端承诺记录</div>
          <div className="mt-px-sm font-retro text-px-xxl leading-none text-exp-gold">{promises.length}</div>
        </section>

        <section className="min-h-0 flex-1">
          <div className="mb-px-sm flex items-center justify-between">
            <h3 className="font-retro text-[10px] leading-none text-ink-1">你说过的话</h3>
            <span className="font-retro text-[10px] text-ink-3">({visiblePromises.length}/4)</span>
          </div>

          <div className="space-y-px-xs">
            {visiblePromises.length > 0 ? (
              visiblePromises.map((promise) => <PromiseRow key={promise.id} promise={promise} />)
            ) : (
              <div className="border-2 border-stroke-ink bg-panel-dim px-px-sm py-px-md text-center text-px-sm text-ink-2">
                后端暂无承诺
              </div>
            )}
          </div>
        </section>
      </div>
    </PixelCard>
  );
};
