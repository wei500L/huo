import type { GossipLeadDTO } from "@/protocol/types";

export const GOSSIP_LEADS_BY_SCENE: Record<string, GossipLeadDTO[]> = {
  tearoom: [
    { id: "gossip-tearoom-1", quarter: 1, scene: "tearoom", speakerId: "employee_lin_xiaoman", text: "PR 说发布会先别讲愿景，先把现金说清楚。", reliability: "LIKELY", linkedEmployeeIds: ["employee_lin_xiaoman"], apCost: 1 },
    { id: "gossip-tearoom-2", quarter: 2, scene: "tearoom", speakerId: "employee_ken_li", text: "有人说食堂预算都快比研发预算高了。", reliability: "RUMOR", linkedEmployeeIds: ["employee_ken_li"], apCost: 1 },
    { id: "gossip-tearoom-3", quarter: 3, scene: "tearoom", speakerId: "employee_mei_song", text: "董事会在问，这季度到底还有没有真实进展。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_ada_gu"], apCost: 1 },
    { id: "gossip-tearoom-4", quarter: 4, scene: "tearoom", speakerId: "employee_mara_chen", text: "大家都在猜，谁会先把门卡留在工位上。", reliability: "LIKELY", linkedEmployeeIds: ["employee_mara_chen"], apCost: 1 },
  ],
  elevator: [
    { id: "gossip-elevator-1", quarter: 1, scene: "elevator", speakerId: "employee_ada_gu", text: "董事会已经开始重新算人头成本。", reliability: "LIKELY", linkedEmployeeIds: ["employee_ada_gu"], apCost: 1 },
    { id: "gossip-elevator-2", quarter: 2, scene: "elevator", speakerId: "employee_sam_wu", text: "法务让所有新合同都多了一页免责声明。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_sam_wu"], apCost: 1 },
    { id: "gossip-elevator-3", quarter: 3, scene: "elevator", speakerId: "employee_iris_zhao", text: "媒体那边已经准备好追问清单了。", reliability: "LIKELY", linkedEmployeeIds: ["employee_iris_zhao"], apCost: 1 },
    { id: "gossip-elevator-4", quarter: 4, scene: "elevator", speakerId: "employee_victor_han", text: "如果今天再失手，明天会议室就会安静得可怕。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_victor_han"], apCost: 1 },
  ],
  meeting_room: [
    { id: "gossip-meeting-1", quarter: 1, scene: "meeting_room", speakerId: "employee_zhou_qiao", text: "CFO 说现金只够再撑两个动作。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_zhou_qiao"], apCost: 1 },
    { id: "gossip-meeting-2", quarter: 2, scene: "meeting_room", speakerId: "employee_jade_tang", text: "产品线已经开始偷偷删需求。", reliability: "LIKELY", linkedEmployeeIds: ["employee_jade_tang"], apCost: 1 },
    { id: "gossip-meeting-3", quarter: 3, scene: "meeting_room", speakerId: "employee_bo_ren", text: "测试组说，这版要是再拖，回归清单会爆。", reliability: "LIKELY", linkedEmployeeIds: ["employee_bo_ren"], apCost: 1 },
    { id: "gossip-meeting-4", quarter: 4, scene: "meeting_room", speakerId: "employee_ada_gu", text: "董事会已经在问继任者名单了。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_ada_gu"], apCost: 1 },
  ],
  workstation: [
    { id: "gossip-work-1", quarter: 1, scene: "workstation", speakerId: "employee_owen_xu", text: "研发不怕改方向，怕的是没有方向。", reliability: "LIKELY", linkedEmployeeIds: ["employee_owen_xu"], apCost: 1 },
    { id: "gossip-work-2", quarter: 2, scene: "workstation", speakerId: "employee_mara_chen", text: "大家都在等一个足够不难看的版本。", reliability: "RUMOR", linkedEmployeeIds: ["employee_mara_chen"], apCost: 1 },
    { id: "gossip-work-3", quarter: 3, scene: "workstation", speakerId: "employee_ken_li", text: "现在连咖啡机都在降本。", reliability: "LIKELY", linkedEmployeeIds: ["employee_ken_li"], apCost: 1 },
    { id: "gossip-work-4", quarter: 4, scene: "workstation", speakerId: "employee_lin_xiaoman", text: "公关文案已经写到结局了。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_lin_xiaoman"], apCost: 1 },
  ],
  rooftop: [
    { id: "gossip-roof-1", quarter: 1, scene: "rooftop", speakerId: "employee_iris_zhao", text: "风声很大，消息也很大。", reliability: "RUMOR", linkedEmployeeIds: ["employee_iris_zhao"], apCost: 1 },
    { id: "gossip-roof-2", quarter: 2, scene: "rooftop", speakerId: "employee_mei_song", text: "外面的人已经开始按失败定价了。", reliability: "LIKELY", linkedEmployeeIds: ["employee_mei_song"], apCost: 1 },
    { id: "gossip-roof-3", quarter: 3, scene: "rooftop", speakerId: "employee_sam_wu", text: "只要董事会开口，故事就会变得更短。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_sam_wu"], apCost: 1 },
    { id: "gossip-roof-4", quarter: 4, scene: "rooftop", speakerId: "employee_victor_han", text: "下一轮谁留下，谁离开，大家都心里有数。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_victor_han"], apCost: 1 },
  ],
  smoking_area: [
    { id: "gossip-smoke-1", quarter: 1, scene: "smoking_area", speakerId: "employee_ken_li", text: "有人说董事会只想要一个能解释亏损的人。", reliability: "LIKELY", linkedEmployeeIds: ["employee_ken_li"], apCost: 1 },
    { id: "gossip-smoke-2", quarter: 2, scene: "smoking_area", speakerId: "employee_zhou_qiao", text: "现金曲线再下去，所有故事都得改结尾。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_zhou_qiao"], apCost: 1 },
    { id: "gossip-smoke-3", quarter: 3, scene: "smoking_area", speakerId: "employee_lin_xiaoman", text: "媒体已经在等一个可以引用的失误。", reliability: "LIKELY", linkedEmployeeIds: ["employee_lin_xiaoman"], apCost: 1 },
    { id: "gossip-smoke-4", quarter: 4, scene: "smoking_area", speakerId: "employee_ada_gu", text: "如果今天倒下，明天就会有人写复盘。", reliability: "CONFIRMED", linkedEmployeeIds: ["employee_ada_gu"], apCost: 1 },
  ],
};
