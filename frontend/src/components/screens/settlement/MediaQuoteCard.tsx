import { PixelCard, PixelIcon } from "@/components/pixel";

interface Props {
  headline: string;
  source: string;
}

const fallback = "-";

export const MediaQuoteCard = ({ headline, source }: Props) => {
  const quote = headline?.trim() ? headline : fallback;
  const outlet = source?.trim() ? source : fallback;

  return (
    <PixelCard title="媒体头条" titleColor="ghost" badge={<PixelIcon ariaLabel="媒体头条" name="news" size={16} />}>
      <div className="space-y-2">
        <p className="break-words font-pixel text-[14px] leading-[1.7] text-ink-1">{`"${quote}"`}</p>
        <div className="text-right text-px-sm leading-none text-ink-2">{`—— ${outlet}`}</div>
      </div>
    </PixelCard>
  );
};

