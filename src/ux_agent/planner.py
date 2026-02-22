from __future__ import annotations

import re

from ux_agent.models import Step


class TaskPlanner:
    """Turn natural-language tasks into executable UI steps.

    This is intentionally lightweight and deterministic; teams can later
    replace it with an LLM planner that emits the same Step schema.
    """

    _CLICK_PATTERNS = [
        r"点击(?P<target>[\w\u4e00-\u9fff]+)",
        r"tap\s+(?P<target>[\w\-]+)",
        r"click\s+(?P<target>[\w\-]+)",
    ]

    def plan(self, task_text: str) -> list[Step]:
        for pattern in self._CLICK_PATTERNS:
            match = re.search(pattern, task_text, re.IGNORECASE)
            if match:
                return [Step(action="click", target=match.group("target"))]

        return [Step(action="observe", target="current_screen")]
