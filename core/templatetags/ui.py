"""Presentation helpers: score colors and the score ring."""

from django import template

register = template.Library()

RING_CIRCUMFERENCE = 251.33  # 2 * pi * r, r = 40

_BADGE = {
    "good": "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
    "mid": "bg-amber-50 text-amber-700 ring-amber-600/20",
    "low": "bg-rose-50 text-rose-700 ring-rose-600/20",
    "none": "bg-slate-100 text-slate-500 ring-slate-500/20",
}
_STROKE = {"good": "#10b981", "mid": "#f59e0b", "low": "#f43f5e", "none": "#cbd5e1"}


@register.filter
def score_tone(score: int | None) -> str:
    if score is None:
        return "none"
    if score >= 75:
        return "good"
    if score >= 50:
        return "mid"
    return "low"


@register.filter
def score_badge(score: int | None) -> str:
    return _BADGE[score_tone(score)]


@register.filter
def score_stroke(score: int | None) -> str:
    return _STROKE[score_tone(score)]


_AVATARS = [
    "from-indigo-500 to-violet-500",
    "from-sky-500 to-cyan-400",
    "from-emerald-500 to-teal-400",
    "from-amber-500 to-orange-400",
    "from-rose-500 to-pink-400",
    "from-fuchsia-500 to-purple-500",
    "from-blue-600 to-indigo-400",
]


@register.filter
def initials(name: str) -> str:
    parts = [p for p in str(name).replace("_", " ").split() if p[:1].isalpha()]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


@register.filter
def avatar(name: str) -> str:
    """Stable gradient per name, so the same person always has the same color."""
    return _AVATARS[sum(map(ord, str(name))) % len(_AVATARS)]


@register.filter
def ring_offset(score: int | None) -> float:
    return round(RING_CIRCUMFERENCE * (1 - (score or 0) / 100), 2)
