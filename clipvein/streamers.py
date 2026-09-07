"""The streamer roster shown in the 'Choose a streamer' picker.

Each entry maps a display name to the handles / search terms ClipVein uses
when it walks the feed. Add your own — the UI reads this list directly.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Streamer:
    name: str                       # display name in the picker
    handles: tuple[str, ...]        # X handles to match (without @)
    aliases: tuple[str, ...] = ()   # extra search terms / nicknames
    accent: str = "#c5f82a"         # UI accent for this streamer's card

    @property
    def primary_handle(self) -> str:
        return self.handles[0] if self.handles else ""

    def search_terms(self) -> list[str]:
        """All strings worth searching the feed for."""
        terms: list[str] = [f"@{h}" for h in self.handles]
        terms += [f"from:{h}" for h in self.handles]
        terms += list(self.aliases)
        return terms


# The default roster. Handles are best-effort public handles; edit freely.
ROSTER: tuple[Streamer, ...] = (
    Streamer(
        name="Clavicular",
        handles=("Clavicular",),
        aliases=("clav", "clavicular clip"),
        accent="#c5f82a",
    ),
    Streamer(
        name="iShowSpeed",
        handles=("ishowspeedsui", "ISHOWSPEED"),
        aliases=("speed", "ishowspeed clip", "speed reacts"),
        accent="#ff4d4d",
    ),
    Streamer(
        name="Kai Cenat",
        handles=("KaiCenat",),
        aliases=("kai", "kai cenat clip", "AMP"),
        accent="#8b5cf6",
    ),
    Streamer(
        name="N3on",
        handles=("N3onwastaken", "N3on"),
        aliases=("n3on", "neon clip"),
        accent="#22d3ee",
    ),
    Streamer(
        name="Adin Ross",
        handles=("adinross",),
        aliases=("adin", "adin ross clip"),
        accent="#f59e0b",
    ),
    Streamer(
        name="Jack Doherty",
        handles=("JackDohertyYT", "jackdoherty"),
        aliases=("jack doherty clip",),
        accent="#38bdf8",
    ),
    Streamer(
        name="Sketch",
        handles=("sketch",),
        aliases=("sketch streamer", "whatup sketch"),
        accent="#34d399",
    ),
    Streamer(
        name="Fanum",
        handles=("Fanum",),
        aliases=("fanum tax", "AMP fanum"),
        accent="#fb7185",
    ),
)


def by_name(name: str) -> Streamer | None:
    for s in ROSTER:
        if s.name.lower() == name.lower():
            return s
    return None


def names() -> list[str]:
    return [s.name for s in ROSTER]
