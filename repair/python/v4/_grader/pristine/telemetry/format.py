"""Formatting helper (correct)."""


def format_summary(log) -> str:
    return f"{len(log.all_events())} events, total {log.total()}"
