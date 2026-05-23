import clsx from "clsx";

import { PixelCard, PixelPortrait, type PortraitId } from "@/components/pixel";

export interface BoardCommentItem {
  name: string;
  portraitId: PortraitId;
  comment: string;
}

interface Props {
  items: BoardCommentItem[];
}

const trimComment = (text: string): string => {
  const clean = text.trim();
  return clean.length > 30 ? clean.slice(0, 30) : clean || "-";
};

export const BoardCommentCard = ({ items }: Props) => {
  const visibleItems = items.slice(0, 3);

  return (
    <PixelCard title="董事评论" titleColor="ghost" badge={<span className="font-retro text-[9px]">3</span>}>
      <div className="space-y-2">
        {visibleItems.map((item, index) => (
          <div
            key={`${item.name}-${index}`}
            className={clsx("grid grid-cols-[48px_minmax(0,1fr)] gap-2 border-b-2 border-panel-dim pb-2 last:border-b-0")}
          >
            <div className="h-[64px] w-[48px] overflow-hidden border-2 border-stroke-ink bg-panel-dim">
              <div className="scale-[0.5] origin-top-left">
                <PixelPortrait expression="neutral" id={item.portraitId} size="sm" />
              </div>
            </div>

            <div className="min-w-0">
              <div className="truncate font-retro text-[10px] leading-none text-ink-1">{item.name || "-"}</div>
              <div className="mt-1 break-words text-px-sm leading-normal text-ink-2">{`“${trimComment(item.comment)}”`}</div>
            </div>
          </div>
        ))}
      </div>
    </PixelCard>
  );
};

