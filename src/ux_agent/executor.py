from __future__ import annotations

from abc import ABC, abstractmethod

from ux_agent.models import Platform, Screen, Step


class DriverExecutor(ABC):
    """Device automation executor.

    Adapter layer so we can start with Android and later add iOS while
    keeping planner/rules reusable.
    """

    @abstractmethod
    def run(self, steps: list[Step]) -> Screen:
        raise NotImplementedError


class AndroidExecutor(DriverExecutor):
    def run(self, steps: list[Step]) -> Screen:
        # Placeholder for Appium + UiAutomator2 integration.
        # In real runs this would return the screen after executing steps.
        labels = [f"executed:{step.action}:{step.target}" for step in steps]
        return Screen(id="android_after_steps", visible_texts=labels)


class IOSExecutor(DriverExecutor):
    def run(self, steps: list[Step]) -> Screen:
        # Placeholder for Appium + XCUITest integration.
        labels = [f"executed:{step.action}:{step.target}" for step in steps]
        return Screen(id="ios_after_steps", visible_texts=labels)


def make_executor(platform: Platform) -> DriverExecutor:
    if platform == Platform.ANDROID:
        return AndroidExecutor()
    if platform == Platform.IOS:
        return IOSExecutor()
    raise ValueError(f"Unsupported platform: {platform}")
