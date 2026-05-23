"""Tests for transcript cleaning."""

from __future__ import annotations

from app.safety.transcript_cleaner import (
    POLITICS_EXTREME_PATTERNS,
    PROFANITY_PATTERNS,
    clean_transcript,
)


def test_clean_transcript_covers_thirty_samples() -> None:
    samples: list[tuple[str, str]] = [
        (
            "brand",
            "我们今天和Google、OpenAI、Tencent 都聊过合作，"
            "后续会继续推进供应链和产品节奏，并把沟通结果同步给董事会。",
        ),
        ("brand", "Apple、Microsoft 和百度都会参与新的技术交流，团队会在本周完成对齐。"),
        ("brand", "我们正在和Alibaba、JD.com 讨论渠道合作，目标是提升交付效率。"),
        ("brand", "Meta、Bilibili 和Kuaishou 都会出现在这次传播名单里。"),
        ("brand", "NVIDIA 与 Intel 的采购沟通已经启动，采购部会继续跟进。"),
        ("brand", "Sam Altman 会在会后收到纪要，Sundar Pichai 也会看到版本说明。"),
        ("brand", "Satya Nadella 和 Tim Cook 的名字都出现在联系人列表中。"),
        ("brand", "Elon Musk、Mark Zuckerberg 和 Jeff Bezos 都被提到了。"),
        ("brand", "Jensen Huang、Larry Ellison 和 Shantanu Narayen 也在名单里。"),
        ("brand", "Arvind Krishna 与 Oracle、Salesforce 的合作备忘录已经整理完毕。"),
        (
            "profanity",
            f"这段话里出现了 {PROFANITY_PATTERNS[0].pattern}，所以需要屏蔽，"
            "并且后面的说明还要继续保留。",
        ),
        (
            "profanity",
            f"我们已经记录了 {PROFANITY_PATTERNS[1].pattern} 和 "
            f"{PROFANITY_PATTERNS[2].pattern}，并准备继续核对上下文。",
        ),
        (
            "profanity",
            f"现场还提到了 {PROFANITY_PATTERNS[3].pattern}，需要进一步处理，"
            "但不能改变原意。",
        ),
        (
            "profanity",
            f"旁边那句包含 {PROFANITY_PATTERNS[4].pattern}，请直接替换并保留其他说明，"
            "同时继续说明当前事实。",
        ),
        (
            "politics",
            f"这段包含 {POLITICS_EXTREME_PATTERNS[0].pattern}，因此要拒绝整段，"
            "并要求重新提交，同时保留其余说明。",
        ),
        (
            "politics",
            f"系统检测到 {POLITICS_EXTREME_PATTERNS[1].pattern}，必须整段拒绝，"
            "不允许进入后续处理，也不要继续扩写。",
        ),
        (
            "politics",
            f"现场还有 {POLITICS_EXTREME_PATTERNS[2].pattern} 的痕迹，"
            "直接拒绝并提示重发，避免进入记录。",
        ),
        ("short", "短句只有二十多个字，不够长。"),
        ("short", "          "),
        (
            "normal",
            "我们将按计划推进产品发布、客户沟通和内部协作，并在本周完成关键节点，"
            "同时把对外口径统一到同一版本。",
        ),
        (
            "normal",
            "本次说明会重点回应收入节奏、成本结构和现金储备，避免误解被放大，"
            "并确保问题都能得到完整解释。",
        ),
        (
            "normal",
            "团队已经把问题拆成三步：核对事实、补充证据、更新对外口径，"
            "这样后续沟通就能保持一致。",
        ),
        (
            "normal",
            "接下来的重点是稳定节奏，减少反复沟通带来的时间损耗，"
            "并让执行动作更容易对齐。",
        ),
        (
            "normal",
            "我们会在不夸大结果的前提下，清楚说明当前进展和后续安排，"
            "避免把不确定内容包装成结论。",
        ),
        (
            "normal",
            "纪要里会记录所有已确认内容，但不会追加任何多余解读，"
            "也不会改变原始意思。",
        ),
        (
            "normal",
            "媒体问答部分会优先讲清楚事实，然后再回答执行层面的安排，"
            "让现场信息保持一致。",
        ),
        (
            "normal",
            "这段说明没有触发任何过滤规则，输出应该保持原样，"
            "并且不会丢失原本的表达。",
        ),
        (
            "normal",
            "同步稿会在会后发出，确保各方收到一致的版本，"
            "而且不会加入额外推测。",
        ),
        (
            "normal",
            "我们会把风险点拆开讲，避免用模糊表达代替实际内容，"
            "让听众知道当前边界。",
        ),
        (
            "normal",
            "最终版会保留原意，不做额外扩写，也不删掉关键事实，"
            "保证各方看到相同信息。",
        ),
    ]

    assert len(samples) == 30

    for category, transcript in samples:
        result = clean_transcript(transcript)
        if category == "brand":
            assert result.rejected is False
            assert "brand_replaced" in result.flags
            assert result.replaced_count > 0
            assert "[品牌]" in result.cleaned
        elif category == "profanity":
            assert result.rejected is False
            assert "profanity_filtered" in result.flags
            assert result.replaced_count > 0
            assert "[屏蔽]" in result.cleaned
        elif category == "politics":
            assert result.rejected is True
            assert result.flags == ["politics_rejected"]
            assert result.cleaned == transcript
        elif category == "short":
            assert result.rejected is True
            assert result.flags == ["too_short"]
            assert result.cleaned == transcript
        else:
            assert result.rejected is False
            assert result.flags == []
            assert result.replaced_count == 0
            assert result.cleaned == transcript


def test_clean_transcript_replaces_three_brands() -> None:
    transcript = "Google、OpenAI 和 Tencent 都出现在同一句里，说明名单里有三个品牌。"

    result = clean_transcript(transcript)

    assert result.rejected is False
    assert result.flags == ["brand_replaced"]
    assert result.replaced_count == 3
    assert result.cleaned.count("[品牌]") == 3
