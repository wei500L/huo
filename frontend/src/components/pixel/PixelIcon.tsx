import { memo, lazy, Suspense, useMemo, type CSSProperties, type ComponentType, type SVGProps } from "react";

import { EMOJI_FALLBACK, ICON_EXPORT_NAMES, ICON_MAP, type IconName } from "./iconCatalog";

export type PixelIconSize = 16 | 24 | 32 | 48 | 64 | 72 | 96;

export interface PixelIconProps {
  name: IconName;
  size?: PixelIconSize;
  color?: string;
  className?: string;
  ariaLabel?: string;
}

type IconModule = {
  [key: string]: ComponentType<SVGProps<SVGSVGElement>>;
};

const ALLOWED_SIZES = new Set<PixelIconSize>([16, 24, 32, 48, 64, 72, 96]);
const warnedMessages = new Set<string>();

const warnDev = (message: string): void => {
  if (!import.meta.env.DEV || warnedMessages.has(message)) {
    return;
  }

  warnedMessages.add(message);
  console.warn(`[PixelIcon] ${message}`);
};

const isIconName = (value: string): value is IconName => {
  return Object.prototype.hasOwnProperty.call(ICON_MAP, value);
};

const normalizeSize = (size: unknown): PixelIconSize => {
  if (typeof size !== "number" || !Number.isFinite(size) || !ALLOWED_SIZES.has(size as PixelIconSize)) {
    warnDev(`Invalid size "${String(size)}". Use one of 16, 24, 32, 48, 64, 72, 96.`);
    return 24;
  }

  return size as PixelIconSize;
};

const createEmojiFallback = (emoji: string): ComponentType<SVGProps<SVGSVGElement>> => {
  const EmojiFallbackIcon = (_props: SVGProps<SVGSVGElement>) => {
    return (
      <span
        aria-hidden="true"
        className="flex h-full w-full items-center justify-center bg-panel-dim text-center leading-none select-none"
        style={{
          fontFamily: '"Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif',
          fontSize: "0.9em",
        }}
      >
        {emoji}
      </span>
    );
  };

  EmojiFallbackIcon.displayName = "PixelIconEmojiFallback";

  return EmojiFallbackIcon;
};

const loadIcon = (name: IconName): Promise<{ default: ComponentType<SVGProps<SVGSVGElement>> }> => {
  const loader = ICON_MAP[name];
  const exportName = ICON_EXPORT_NAMES[name];
  const emoji = EMOJI_FALLBACK[name] ?? "❓";

  return loader()
    .then((module) => {
      const iconModule = module as unknown as IconModule;
      const candidate = iconModule[exportName] ?? iconModule.default;

      if (!candidate) {
        warnDev(`Icon "${name}" is missing export "${exportName}". Using emoji fallback.`);
        return { default: createEmojiFallback(emoji) };
      }

      return { default: candidate };
    })
    .catch((error: unknown) => {
      const reason = error instanceof Error ? error.message : String(error);
      warnDev(`Failed to load icon "${name}": ${reason}. Using emoji fallback.`);
      return { default: createEmojiFallback(emoji) };
    });
};

function PixelIconImpl({ name, size = 24, color, className, ariaLabel }: PixelIconProps) {
  const resolvedName = isIconName(name) ? name : undefined;
  const normalizedSize = normalizeSize(size);
  const label = ariaLabel ?? name;
  const rootStyle: CSSProperties = {
    color,
    width: normalizedSize,
    height: normalizedSize,
    display: "inline-grid",
    placeItems: "center",
    imageRendering: "pixelated",
    lineHeight: 0,
  };
  const iconStyle: CSSProperties = {
    display: "block",
    width: "100%",
    height: "100%",
    imageRendering: "pixelated",
  };
  const LazyIcon = useMemo(() => {
    if (!resolvedName) {
      warnDev(`Icon "${String(name)}" is not in the catalog. Using emoji fallback.`);
      return null;
    }

    return lazy(() => loadIcon(resolvedName));
  }, [name, resolvedName]);

  const emoji = resolvedName ? EMOJI_FALLBACK[resolvedName] : "❓";

  return (
    <span aria-label={label} className={className} role="img" style={rootStyle}>
      {LazyIcon ? (
        <Suspense
          fallback={
            <span aria-hidden="true" className="block h-full w-full bg-panel-dim" />
          }
        >
          <LazyIcon aria-hidden="true" style={iconStyle} width={normalizedSize} height={normalizedSize} />
        </Suspense>
      ) : (
        <span
          aria-hidden="true"
          className="flex h-full w-full items-center justify-center bg-panel-dim text-center leading-none"
        >
          {emoji}
        </span>
      )}
    </span>
  );
}

PixelIconImpl.displayName = "PixelIcon";

export const PixelIcon = memo(PixelIconImpl);
PixelIcon.displayName = "PixelIcon";
