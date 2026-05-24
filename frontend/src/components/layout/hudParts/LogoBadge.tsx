import { Sparkles } from "pixelarticons/react/Sparkles";

export const LogoBadge = () => {
  return (
    <div
      className="relative h-11 w-[148px] shrink-0 overflow-visible border-2 border-stroke-ink bg-exp-gold shadow-hard-sm sm:h-12 sm:w-[176px]"
      style={{ transform: "skewX(-8deg)" }}
    >
      <div
        className="flex h-full w-full items-center justify-between gap-2 px-3"
        style={{ transform: "skewX(8deg)" }}
      >
        <span className="whitespace-nowrap font-retro text-px-lg leading-none text-ink-1 sm:text-px-xl">
          YES,BOSS!
        </span>
      </div>

      <span
        aria-hidden="true"
        className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center border-2 border-stroke-ink bg-panel shadow-hard-sm"
        style={{ transform: "skewX(8deg)" }}
      >
        <Sparkles className="h-4 w-4" />
      </span>
    </div>
  );
};
