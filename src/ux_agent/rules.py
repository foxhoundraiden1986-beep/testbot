from __future__ import annotations

from ux_agent.models import RunResult, Screen, UXRule
from ux_agent.vision import ScreenRecognizer


class UXRuleEngine:
    def __init__(self, recognizer: ScreenRecognizer | None = None) -> None:
        self.recognizer = recognizer or ScreenRecognizer()

    def evaluate(self, entry_screen: Screen, first_page: Screen, rule: UXRule) -> RunResult:
        evidence: list[str] = []
        entry_has_screen_signal = self.recognizer.contains(entry_screen, rule.when_screen_contains)
        entry_has_image_signal = self.recognizer.contains(entry_screen, rule.when_image_contains)

        evidence.append(f"entry_screen_contains={entry_has_screen_signal}")
        evidence.append(f"entry_image_contains={entry_has_image_signal}")

        if not (entry_has_screen_signal and entry_has_image_signal):
            return RunResult(
                passed=True,
                summary=(
                    "Rule not triggered: entry conditions were not fully met, "
                    "so no mandatory homepage assertion is required."
                ),
                evidence=evidence,
            )

        homepage_has_expected = self.recognizer.contains(first_page, rule.then_first_page_must_contain)
        evidence.append(f"first_page_contains_expected={homepage_has_expected}")

        if homepage_has_expected:
            return RunResult(
                passed=True,
                summary=f"Rule '{rule.name}' passed.",
                evidence=evidence,
            )

        return RunResult(
            passed=False,
            summary=(
                f"Rule '{rule.name}' failed: entry contains '{rule.when_image_contains}', "
                f"but first page missing '{rule.then_first_page_must_contain}'."
            ),
            evidence=evidence,
        )
