import { PixelIcon } from "@/components/pixel";

export interface Props {
  day: number;
  time: string;
  weekday: string;
  date: string;
}

export const DateCard = ({ day, time, weekday, date }: Props) => {
  const hasDay = Number.isFinite(day) && day > 0 && time !== "-/-";
  const firstLine = hasDay ? `第${day}天 ${time}` : "-/-";
  const secondLine = hasDay ? `${weekday} ${date}` : "-/-";

  return (
    <article className="flex h-12 w-[220px] shrink-0 items-center border-2 border-stroke-ink bg-panel px-2 shadow-hard sm:h-14 sm:w-[280px]">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim shadow-hard-sm sm:h-9 sm:w-9">
        <PixelIcon name="calendar" size={16} />
      </div>

      <div className="min-w-0 flex-1 leading-none">
        <div className="truncate text-[10px] text-ink-1 sm:text-px-sm">{firstLine}</div>
        <div className="mt-1 truncate text-[10px] text-ink-2 sm:text-px-sm">{secondLine}</div>
      </div>
    </article>
  );
};
