import clsx from "clsx";

type NpcTone = "programmer" | "marketing";

const NPC_META: Record<NpcTone, { hair: string; shirt: string; skin: string; seat: string }> = {
  programmer: {
    hair: "bg-[#2A2A2A]",
    shirt: "bg-pixel-blue",
    skin: "bg-[#F0B88D]",
    seat: "bg-[#6B7280]",
  },
  marketing: {
    hair: "bg-[#6D3E2E]",
    shirt: "bg-pixel-orange",
    skin: "bg-[#F4C39A]",
    seat: "bg-[#8B5CF6]",
  },
};

function NpcSprite({ tone, flip = false }: { tone: NpcTone; flip?: boolean }) {
  const meta = NPC_META[tone];

  return (
    <div
      aria-hidden="true"
      className={clsx("relative h-8 w-8 pixel-render", flip && "-scale-x-100")}
    >
      <span className={clsx("absolute left-[9px] top-[2px] h-3 w-4 border-2 border-stroke-ink", meta.hair)} />
      <span className={clsx("absolute left-[10px] top-[8px] h-3 w-4 border-2 border-stroke-ink", meta.skin)} />
      <span className="absolute left-[20px] top-[11px] h-1 w-1 bg-ink-1" />
      <span className={clsx("absolute left-[8px] top-[17px] h-3 w-5 border-2 border-stroke-ink", meta.shirt)} />
      <span className={clsx("absolute left-[5px] top-[24px] h-2 w-6 border-2 border-stroke-ink", meta.seat)} />
    </div>
  );
}

function SpeechDots() {
  return (
    <div
      aria-label="NPC thinking"
      className="absolute -top-11 left-1/2 flex h-8 w-12 -translate-x-1/2 items-center justify-center border-2 border-stroke-ink bg-panel shadow-hard-sm"
    >
      <span className="font-pixel text-px-md leading-none text-ink-1">...</span>
      <span className="absolute -bottom-[6px] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-stroke-ink bg-panel" />
    </div>
  );
}

function Cup({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={clsx("absolute h-4 w-4 border-2 border-stroke-ink bg-panel shadow-hard-sm", className)}
    >
      <span className="absolute -right-[5px] top-[3px] h-2 w-2 border-2 border-l-0 border-stroke-ink bg-panel" />
    </span>
  );
}

function TableSprite() {
  return (
    <div aria-hidden="true" className="absolute left-[494px] top-[252px] h-[188px] w-[284px]">
      <div className="absolute left-[34px] top-[20px] h-[132px] w-[216px] border-4 border-stroke-ink bg-[#B96F45] shadow-hard" />
      <div className="absolute left-[62px] top-[44px] h-[84px] w-[160px] border-4 border-stroke-ink bg-[#D28A57]" />
      <div className="absolute left-[58px] top-[152px] h-8 w-8 border-2 border-stroke-ink bg-[#704527]" />
      <div className="absolute right-[58px] top-[152px] h-8 w-8 border-2 border-stroke-ink bg-[#704527]" />
      <Cup className="left-[78px] top-[58px]" />
      <Cup className="left-[172px] top-[62px]" />
      <Cup className="left-[130px] top-[104px]" />
      <div className="absolute left-[122px] top-[52px] h-9 w-9 border-2 border-stroke-ink bg-[#7A5130]">
        <span className="absolute left-[12px] top-[14px] h-4 w-2 bg-pixel-green" />
        <span className="absolute left-[7px] top-[7px] h-3 w-3 border-2 border-stroke-ink bg-pixel-green" />
        <span className="absolute right-[7px] top-[5px] h-3 w-3 border-2 border-stroke-ink bg-pixel-green" />
      </div>
    </div>
  );
}

function WaterMachine() {
  return (
    <div aria-hidden="true" className="absolute right-[88px] top-[156px] h-[216px] w-[96px]">
      <div className="h-full border-4 border-stroke-ink bg-[#E8EEF4] shadow-hard">
        <div className="mx-auto mt-4 h-14 w-12 border-2 border-stroke-ink bg-[#A8D5FF]" />
        <div className="mx-auto mt-4 h-9 w-16 border-2 border-stroke-ink bg-panel-dim" />
        <div className="mx-auto mt-4 h-16 w-12 border-2 border-stroke-ink bg-[#4B5563]" />
      </div>
      <div className="mx-auto h-5 w-20 border-4 border-t-0 border-stroke-ink bg-[#C7D2DE]" />
    </div>
  );
}

function CoffeeMachine() {
  return (
    <div aria-hidden="true" className="absolute left-[88px] top-[178px] h-[164px] w-[108px]">
      <div className="h-full border-4 border-stroke-ink bg-[#4A342B] shadow-hard">
        <div className="mx-auto mt-4 h-9 w-16 border-2 border-stroke-ink bg-[#1F2937]" />
        <div className="mx-auto mt-4 h-6 w-12 border-2 border-stroke-ink bg-pixel-orange" />
        <div className="mx-auto mt-2 h-10 w-14 border-2 border-stroke-ink bg-panel" />
      </div>
      <div className="h-6 border-4 border-t-0 border-stroke-ink bg-[#6B4B3C]" />
    </div>
  );
}

export function SceneStage() {
  return (
    <div
      className="relative h-[640px] w-[1280px] overflow-hidden border-4 border-stroke-ink bg-[#DDE8DD] shadow-hard pixel-render"
      style={{
        backgroundImage: "url('/sprites/scenes/tearoom_bg.png')",
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <div className="absolute left-5 top-5 border-2 border-stroke-ink bg-panel px-px-md py-px-sm shadow-hard">
        <span className="font-pixel text-px-md leading-none text-ink-1">📍 茶水间 TEA ROOM</span>
      </div>

      <div aria-hidden="true" className="absolute inset-x-0 bottom-0 h-[188px] border-t-4 border-stroke-ink bg-floor" />
      <div aria-hidden="true" className="absolute left-[272px] top-[116px] h-[92px] w-[420px] border-4 border-stroke-ink bg-[#F3F0E6] shadow-hard" />
      <div aria-hidden="true" className="absolute left-[300px] top-[140px] h-9 w-[72px] border-2 border-stroke-ink bg-panel-dim" />
      <div aria-hidden="true" className="absolute left-[392px] top-[140px] h-9 w-[88px] border-2 border-stroke-ink bg-pixel-blue" />
      <div aria-hidden="true" className="absolute left-[504px] top-[140px] h-9 w-[132px] border-2 border-stroke-ink bg-panel-dim" />

      <CoffeeMachine />
      <WaterMachine />
      <TableSprite />

      <div className="absolute left-[456px] top-[342px]">
        <NpcSprite tone="programmer" />
      </div>
      <div className="absolute left-[784px] top-[330px]">
        <SpeechDots />
        <NpcSprite flip tone="marketing" />
      </div>
    </div>
  );
}
