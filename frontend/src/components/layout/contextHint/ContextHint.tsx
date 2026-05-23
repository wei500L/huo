import { PixelPortrait, PixelSpeechBubble, type PortraitId } from "@/components/pixel";

export interface Props {
  speaker?: PortraitId;
  text: string;
}

export const ContextHint = ({ speaker = "advisor", text }: Props) => {
  return (
    <div className="flex min-w-0 max-w-[360px] items-center gap-2">
      <div
        aria-hidden="true"
        className="relative h-8 w-8 shrink-0 overflow-hidden border-2 border-stroke-ink bg-panel shadow-hard-sm"
      >
        <div className="absolute left-0 top-0 scale-[0.3333] origin-top-left">
          <PixelPortrait id={speaker} size="sm" />
        </div>
      </div>

      <div className="min-w-0 flex-1">
        <PixelSpeechBubble className="max-w-full" text={text} tone="neutral" arrow="none" />
      </div>
    </div>
  );
};
