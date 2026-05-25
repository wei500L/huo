import { useState } from "react";
import clsx from "clsx";

import { PixelButton, PixelCard, PixelIcon } from "@/components/pixel";
import type { GossipLeadDTO } from "@/protocol/types";

export interface GossipNoteItem {
  id: string;
  lead: GossipLeadDTO;
  notedAt: string;
}

export interface GossipNotesDrawerProps {
  notes: GossipNoteItem[];
}

export function GossipNotesDrawer({ notes }: GossipNotesDrawerProps) {
  const [open, setOpen] = useState(false);

  return (
    <aside className="absolute bottom-px-md right-px-md z-20 w-[320px] max-w-[calc(100vw-32px)]">
      {open ? (
        <PixelCard
          title={`茶水间笔记 ${notes.length}`}
          titleColor="orange"
          badge={
            <button
              aria-label="收起笔记"
              className="flex h-6 w-6 items-center justify-center border-2 border-stroke-ink bg-panel text-ink-1"
              type="button"
              onClick={() => setOpen(false)}
            >
              <PixelIcon ariaLabel="close" name="close-box" size={16} />
            </button>
          }
        >
          <div className="max-h-[260px] space-y-px-sm overflow-y-auto pr-px-xs" data-testid="gossip-notes-list">
            {notes.length === 0 ? (
              <div className="border-2 border-stroke-ink bg-panel-dim p-px-sm text-px-sm text-ink-2">
                暂无笔记
              </div>
            ) : null}
            {notes.map((note) => (
              <article key={note.id} className="border-2 border-stroke-ink bg-panel-dim p-px-sm">
                <div className="mb-px-xs flex items-center justify-between gap-px-sm text-px-xs text-ink-2">
                  <span>Q{note.lead.quarter}</span>
                  <span>{note.lead.reliability}</span>
                </div>
                <p className="break-words text-px-sm leading-normal text-ink-1">{note.lead.text}</p>
              </article>
            ))}
          </div>
        </PixelCard>
      ) : (
        <div className={clsx("ml-auto w-[180px]", notes.length > 0 && "animate-bounce-pixel")}>
          <PixelButton
            fullWidth
            icon={<PixelIcon ariaLabel="notes" name="save" size={24} />}
            size="md"
            variant="ghost"
            onClick={() => setOpen(true)}
          >
            笔记 {notes.length}
          </PixelButton>
        </div>
      )}
    </aside>
  );
}
