import type { CompanyDTO } from "@/protocol/types";

export interface CompanyTemplateDTO {
  templateId: string;
  company: CompanyDTO;
}

export const COMPANY_TEMPLATES: CompanyTemplateDTO[] = [
  {
    templateId: "C-01",
    company: {
      id: "company-entropy-noodles",
      name: "灵眸科技",
      business: "计算机视觉芯片",
      employeeCount: 112,
      absurdity: 87,
      foundingMotto: "看得见未来，先看得见现金。",
      deathCauses: [
        { category: "capital", description: "现金流先于芯片量产蒸发。" },
        { category: "board", description: "董事会耐心在第 4 季度耗尽。" },
      ],
      foundedYear: 2021,
    },
  },
  {
    templateId: "C-02",
    company: {
      id: "company-source-voice",
      name: "源语互动",
      business: "独立游戏研发",
      employeeCount: 38,
      absurdity: 74,
      foundingMotto: "把热爱做成可支付的版本。",
      deathCauses: [
        { category: "scope", description: "功能表越写越长，发布窗口越缩越短。" },
        { category: "morale", description: "团队把延期当作默认语言。" },
      ],
      foundedYear: 2023,
    },
  },
  {
    templateId: "C-03",
    company: {
      id: "company-titan-depth",
      name: "钛深智能",
      business: "工业 AI 解决方案",
      employeeCount: 65,
      absurdity: 79,
      foundingMotto: "先落地，再讲平台故事。",
      deathCauses: [
        { category: "execution", description: "交付、合规、销售同时超载。" },
        { category: "face", description: "口碑修复比产品迭代更慢。" },
      ],
      foundedYear: 2022,
    },
  },
];

export const COMPANY_TEMPLATE_BY_ID = Object.fromEntries(
  COMPANY_TEMPLATES.map((item) => [item.templateId, item]),
) as Record<string, CompanyTemplateDTO>;
