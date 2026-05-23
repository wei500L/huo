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
    <article className="flex h-14 w-[280px] shrink-0 items-center border-2 border-stroke-ink bg-panel px-2 shadow-hard">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim shadow-hard-sm">
        <PixelIcon name="calendar" size={16} />
      </div>

      <div className="min-w-0 flex-1 leading-none">
        <div className="truncate text-px-sm text-ink-1">{firstLine}</div>
        <div className="mt-1 truncate text-px-sm text-ink-2">{secondLine}</div>
      </div>
    </article>
  );
};
