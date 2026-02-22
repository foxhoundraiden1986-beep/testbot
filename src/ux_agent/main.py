from __future__ import annotations

import argparse
import json

from ux_agent.executor import make_executor
from ux_agent.models import Platform, Screen, UXRule
from ux_agent.planner import TaskPlanner
from ux_agent.rules import UXRuleEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="APP UX agent prototype")
    parser.add_argument("--platform", choices=["android", "ios"], default="android")
    parser.add_argument("--task", required=True, help="Natural-language task")
    parser.add_argument(
        "--entry-screen-texts",
        nargs="*",
        default=[],
        help="Observed entry-screen texts/icons",
    )
    parser.add_argument(
        "--first-page-texts",
        nargs="*",
        default=[],
        help="Observed first-page texts/icons",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    platform = Platform(args.platform)
    planner = TaskPlanner()
    steps = planner.plan(args.task)

    # execute steps (simulated in this prototype)
    executor = make_executor(platform)
    _ = executor.run(steps)

    entry = Screen(id="entry", visible_texts=args.entry_screen_texts)
    first_page = Screen(id="first", visible_texts=args.first_page_texts)

    rule = UXRule(
        name="promo_consistency_99",
        when_screen_contains="活动",
        when_image_contains="小保养99元",
        then_first_page_must_contain="99元小保养",
    )

    result = UXRuleEngine().evaluate(entry, first_page, rule)
    print(
        json.dumps(
            {
                "platform": platform.value,
                "steps": [step.__dict__ for step in steps],
                "passed": result.passed,
                "summary": result.summary,
                "evidence": result.evidence,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
