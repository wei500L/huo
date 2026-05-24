import { PixelIcon } from "@/components/pixel";

const RESOURCES = [
  {
    title: "Pixel UI Pack",
    meaning: "按钮、面板、HUD 骨架",
    note: "把界面控件统一成同一套像素语法，适合顶栏、主按钮和卡片标题。",
    accent: "bg-pixel-blue",
    preview: (
      <div className="grid grid-cols-2 gap-2">
        <span className="h-8 border-2 border-stroke-ink bg-pixel-blue" />
        <span className="h-8 border-2 border-stroke-ink bg-panel-dim" />
        <span className="col-span-2 h-4 border-2 border-stroke-ink bg-pixel-orange" />
      </div>
    ),
  },
  {
    title: "Office Space Tileset",
    meaning: "工位、走廊、墙面、门窗",
    note: "更适合做办公室场景层和背景条，不会抢掉角色和按钮的注意力。",
    accent: "bg-pixel-green",
    preview: (
      <img
        alt="Office Space Tileset preview"
        className="block h-full w-full object-cover object-left-top pixel-render"
        src="/sprites/resources/office-space-tileset.png"
      />
    ),
  },
  {
    title: "Portrait Pack",
    meaning: "头像、对话锚点、情绪表达",
    note: "适合董事会、员工反馈和结算页里的发言人视图，强化角色语义。",
    accent: "bg-pixel-orange",
    preview: (
      <img
        alt="Portrait Pack preview"
        className="block h-full w-full object-cover pixel-render"
        src="/sprites/resources/portrait-pack-thumb.jpg"
      />
    ),
  },
] as const;

export const ResourceShelf = () => {
  return (
    <section className="space-y-3">
      <div className="flex items-center gap-2">
        <PixelIcon name="star" size={16} ariaLabel="热门素材" />
        <h2 className="text-px-lg leading-none text-ink-1">热门像素资源</h2>
      </div>

      <div className="grid gap-3 lg:grid-cols-3">
        {RESOURCES.map((resource) => (
          <article key={resource.title} className="border-2 border-stroke-ink bg-panel px-3 py-3 shadow-hard-sm">
            <div className="mb-3 h-[92px] overflow-hidden border-2 border-stroke-ink bg-panel-dim">
              {resource.preview}
            </div>

            <div className="flex items-start gap-2">
              <span aria-hidden="true" className={`mt-1 h-3 w-3 shrink-0 border border-stroke-ink ${resource.accent}`} />
              <div className="min-w-0">
                <div className="truncate text-px-md leading-tight text-ink-1">{resource.title}</div>
                <div className="mt-1 text-[10px] leading-tight text-ink-2">{resource.meaning}</div>
              </div>
            </div>

            <p className="mt-2 text-px-sm leading-snug text-ink-2">{resource.note}</p>
          </article>
        ))}
      </div>
    </section>
  );
};

export default ResourceShelf;
