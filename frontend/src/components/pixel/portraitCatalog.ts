export type PortraitId =
  | "ceo_male_01"
  | "ceo_male_02"
  | "ceo_female_01"
  | "employee_zhang_chi"
  | "employee_lin_xiaoman"
  | "board_chairman"
  | "rival_ceo"
  | "advisor";

export type PortraitExpression =
  | "neutral"
  | "smile"
  | "tired"
  | "angry"
  | "confident"
  | "anxious"
  | "rip";

export interface PortraitMeta {
  id: PortraitId;
  baseSrc: string;
  expressions: PortraitExpression[];
}

const EXPRESSIONS: PortraitExpression[] = [
  "neutral",
  "smile",
  "tired",
  "angry",
  "confident",
  "anxious",
  "rip",
];

const createPortraitMeta = (id: PortraitId): PortraitMeta => ({
  id,
  baseSrc: `/sprites/portraits/${id}/neutral.png`,
  expressions: EXPRESSIONS,
});

const CEO_MALE_01_SRC = "/sprites/portraits/ceo_male_01/neutral.png";

export const PORTRAIT_CATALOG: Record<PortraitId, PortraitMeta> = {
  ceo_male_01: {
    id: "ceo_male_01",
    baseSrc: CEO_MALE_01_SRC,
    expressions: EXPRESSIONS,
  },
  ceo_male_02: createPortraitMeta("ceo_male_02"),
  ceo_female_01: createPortraitMeta("ceo_female_01"),
  employee_zhang_chi: createPortraitMeta("employee_zhang_chi"),
  employee_lin_xiaoman: createPortraitMeta("employee_lin_xiaoman"),
  board_chairman: createPortraitMeta("board_chairman"),
  rival_ceo: createPortraitMeta("rival_ceo"),
  advisor: createPortraitMeta("advisor"),
};

export const getPortraitSrc = (id: PortraitId, expression: PortraitExpression): string => {
  if (id === "ceo_male_01") {
    return CEO_MALE_01_SRC;
  }

  return `/sprites/portraits/${id}/${expression}.png`;
};
