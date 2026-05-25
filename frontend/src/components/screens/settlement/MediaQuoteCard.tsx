import { PixelCard, PixelIcon } from "@/components/pixel";

interface Props {
  headline?: string;
  source?: string;
}

export const MediaQuoteCard = ({ headline, source }: Props) => {
  const quote = headline?.trim() ?? "";
  const outlet = source?.trim() ?? "";

  return (
    <PixelCard title="媒体头条" titleColor="ghost" badge={<PixelIcon ariaLabel="媒体头条" name="news" size={16} />}>
      {quote || outlet ? (
        <div className="space-y-2">
          {quote ? <p className="break-words font-pixel text-[14px] leading-[1.7] text-ink-1">{`"${quote}"`}</p> : null}
          {outlet ? <div className="text-right text-px-sm leading-none text-ink-2">{`-- ${outlet}`}</div> : null}
        </div>
      ) : (
        <div className="border-2 border-stroke-ink bg-panel-dim px-3 py-4 text-center text-px-sm text-ink-2">
          后端暂无媒体头条
        </div>
      )}
    </PixelCard>
  );
};
