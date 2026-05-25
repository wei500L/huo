import { PixelButton, PixelCard, PixelIcon, type IconName, type Variant } from "@/components/pixel";

export interface Action {
  id: "note" | "probe" | "leave";
  label: string;
  iconName: IconName;
  variant: "blue" | "green" | "orange" | "red" | "ghost";
  apCost: number;
  disabled?: boolean;
  onClick: () => void;
}

export interface ActionPanelProps {
  apRemaining: number;
  actions: Action[];
}

export function ActionPanel({ apRemaining, actions }: ActionPanelProps) {
  const normalizedAP = Math.max(0, Math.trunc(apRemaining));

  return (
    <PixelCard
      title={`行动点 AP ${normalizedAP}`}
      titleColor={normalizedAP > 0 ? "blue" : "red"}
      className="w-full"
    >
      <div className="flex flex-col gap-px-sm">
        {actions.map((action) => {
          const disabled = action.disabled || (normalizedAP <= 0 && action.id !== "leave");
          return (
            <PixelButton
              key={action.id}
              disabled={disabled}
              fullWidth
              icon={<PixelIcon ariaLabel={action.label} name={action.iconName} size={24} />}
              size="lg"
              variant={action.variant as Variant}
              onClick={action.onClick}
            >
              {action.label}
            </PixelButton>
          );
        })}
      </div>
    </PixelCard>
  );
}
