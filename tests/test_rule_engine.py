from ux_agent.models import Screen, UXRule
from ux_agent.rules import UXRuleEngine


RULE = UXRule(
    name="promo_consistency_99",
    when_screen_contains="活动",
    when_image_contains="小保养99元",
    then_first_page_must_contain="99元小保养",
)


def test_rule_passes_when_triggered_and_homepage_matches() -> None:
    entry = Screen(id="entry", visible_texts=["春季活动", "小保养99元活动"])
    first = Screen(id="first", visible_texts=["首页", "99元小保养"])

    result = UXRuleEngine().evaluate(entry, first, RULE)

    assert result.passed is True


def test_rule_fails_when_triggered_but_homepage_missing_expected_text() -> None:
    entry = Screen(id="entry", visible_texts=["春季活动", "小保养99元活动"])
    first = Screen(id="first", visible_texts=["首页", "其他套餐"])

    result = UXRuleEngine().evaluate(entry, first, RULE)

    assert result.passed is False


def test_rule_skips_when_not_triggered() -> None:
    entry = Screen(id="entry", visible_texts=["春季活动", "轮胎折扣"])
    first = Screen(id="first", visible_texts=["首页", "其他套餐"])

    result = UXRuleEngine().evaluate(entry, first, RULE)

    assert result.passed is True
    assert "not triggered" in result.summary
