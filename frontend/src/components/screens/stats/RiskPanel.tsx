import { PixelButton, PixelIcon } from "@/components/pixel";

import { RiskCard, type Risk } from "./RiskCard";

interface RiskPanelProps {
  risks: Risk[];
  onViewAll: () => void;
}

export const RiskPanel = ({ risks, onViewAll }: RiskPanelProps) => {
  const visibleRisks = risks.slice(0, 5);

  return (
    <aside className="flex h-full min-w-0 flex-col border-2 border-stroke-ink bg-panel shadow-hard">
      <div className="flex h-10 items-center justify-between border-b-2 border-stroke-ink bg-pixel-red px-px-md text-px-sm text-white">
        <span>风险预警</span>
        <PixelIcon name="alarm" size={24} ariaLabel="风险预警" />
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-px-md p-px-md">
        <div className="flex min-h-0 flex-1 flex-col gap-px-md overflow-y-auto">
          {visibleRisks.map((risk) => (
            <RiskCard key={risk.id} risk={risk} />
          ))}
        </div>

        <PixelButton
          fullWidth
          size="md"
          variant="danger"
          icon={<PixelIcon name="forward" size={24} ariaLabel="查看全部风险" />}
          onClick={onViewAll}
        >
          查看全部风险
        </PixelButton>
      </div>
    </aside>
  );
};
