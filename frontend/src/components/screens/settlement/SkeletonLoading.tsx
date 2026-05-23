interface Props {
  llmDegraded?: boolean;
}

const SkeletonMetricCard = () => {
  return (
    <div className="min-h-[200px] animate-pulse border-2 border-stroke-ink bg-panel-dim shadow-hard">
      <div className="flex h-8 items-center justify-between border-b-2 border-stroke-ink px-3">
        <span className="h-3 w-24 bg-stroke-ink/30" />
        <span className="h-4 w-16 border border-stroke-ink bg-stroke-ink/20" />
      </div>
      <div className="flex gap-3 px-3 py-3">
        <span className="h-14 w-14 border-2 border-stroke-ink bg-stroke-ink/20" />
        <div className="flex-1 space-y-3">
          <span className="block h-3 w-20 bg-stroke-ink/20" />
          <span className="block h-6 w-28 bg-stroke-ink/25" />
          <span className="block h-3 w-32 bg-stroke-ink/20" />
        </div>
      </div>
    </div>
  );
};

export const SkeletonLoading = ({ llmDegraded = false }: Props) => {
  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2 text-px-md leading-none text-ink-1">
        <span>AI 正在结算...</span>
        {llmDegraded ? (
          <span className="border border-stroke-ink bg-panel-dim px-2 py-1 text-px-sm leading-none text-ink-3">
            AI 失联，已用兜底文案
          </span>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <SkeletonMetricCard />
        <SkeletonMetricCard />
        <SkeletonMetricCard />
        <SkeletonMetricCard />
      </div>
    </section>
  );
};

