import { PixelButton, PixelCard, PixelIcon, type IconName } from "@/components/pixel";

export interface HighlightsItem {
  iconName: IconName;
  title: string;
  subtitle: string;
}

interface Props {
  items: HighlightsItem[];
}

const MAX_ITEMS = 5;

export const HighlightsPanel = ({ items }: Props) => {
  const visibleItems = items.slice(0, MAX_ITEMS);
  const hasMore = items.length > MAX_ITEMS;

  return (
    <PixelCard kind="info" title="本周重点事项" className="h-[248px]">
      <div className="flex h-full min-h-0 flex-col">
        <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-hidden">
          {visibleItems.map((item) => (
            <div key={item.title} className="flex items-start gap-2 border-2 border-stroke-ink bg-panel px-2 py-2">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center border border-stroke-ink bg-panel-dim">
                <PixelIcon name={item.iconName} size={16} ariaLabel={item.title} />
              </span>
              <div className="min-w-0">
                <div className="truncate text-px-sm leading-none text-ink-1">{item.title}</div>
                <div className="mt-1 break-words text-px-xs leading-snug text-ink-2">{item.subtitle}</div>
              </div>
            </div>
          ))}
        </div>

        {hasMore ? (
          <div className="pt-2">
            <div className="w-full max-w-[104px]">
              <PixelButton size="sm" variant="ghost" icon={<PixelIcon name="forward" size={16} ariaLabel="更多" />}>
                更多
              </PixelButton>
            </div>
          </div>
        ) : null}
      </div>
    </PixelCard>
  );
};

export default HighlightsPanel;
