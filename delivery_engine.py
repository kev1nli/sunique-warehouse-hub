"""In-town delivery scheduling rules (pure logic, no network).

A day has 3 fixed time slots. The slots are also the route order for that day,
so choosing a slot for a new order = choosing where it goes in the day's route.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Callable, Optional

# label stored in the schedule sheet, label shown to people, start hour, end hour
SLOTS = [
    ("9:00 AM - 11:00 AM", "9:00-11:00", 9, 11),
    ("11:00 AM - 14:00 PM", "11:00-14:00", 11, 14),
    ("14:00 PM - 17:00 PM", "14:00-17:00", 14, 17),
]

DEPOTS = {
    "Cabinet": ("2045 Westgate Dr Ste 130, Carrollton, TX 75006", (32.9886, -96.8998)),
    "Flooring": ("739 Parkway Dr, Grand Prairie, TX 75051", (32.7072, -97.0096)),
}


@dataclass
class Settings:
    detour_limit_min: float = 25      # max extra drive minutes to add a stop to a day
    horizon_days: int = 10            # business days offered to sales
    far_limit_min: float = 120        # one-way drive above this -> manual scheduling
    day_start_hour: float = 8.0       # truck leaves the warehouse
    service_min: float = 30           # unloading time without handling
    service_handling_min: float = 60  # unloading time with handling


@dataclass
class Booking:
    slot: int                          # 0, 1, 2
    label: str                         # SO number or reservation name
    address: str = ""
    point: Optional[tuple] = None      # (lat, lon); None for reservations / unknown
    reserved: bool = False
    handling: bool = True


@dataclass
class DayPlan:
    day: date
    bookings: list = field(default_factory=list)

    def taken(self) -> set:
        return {b.slot for b in self.bookings}


@dataclass
class Option:
    day: date
    status: str                 # Recommended / Open / Full / Different direction / Not ready / Too far
    slot: Optional[int] = None
    extra_min: Optional[float] = None
    note: str = ""


def norm_address(a: str) -> str:
    return " ".join(str(a or "").lower().replace(",", " ").split())


def _nth_weekday(year, month, weekday, n):
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def _last_weekday(year, month, weekday):
    d = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def company_holidays(year: int) -> set:
    """Days with no delivery. Edit this list to match the company calendar."""
    thanksgiving = _nth_weekday(year, 11, 3, 4)
    return {
        date(year, 1, 1),                    # New Year's Day
        _last_weekday(year, 5, 0),           # Memorial Day
        date(year, 7, 4),                    # Independence Day
        _nth_weekday(year, 9, 0, 1),         # Labor Day
        thanksgiving,                        # Thanksgiving
        thanksgiving + timedelta(days=1),    # Day after Thanksgiving
        date(year, 12, 24),                  # Christmas Eve
        date(year, 12, 25),                  # Christmas Day
    }


EXTRA_CLOSED: set = set()  # one-off closed dates, filled in by the planner page


def is_business_day(d: date) -> bool:
    return d.weekday() < 5 and d not in company_holidays(d.year) and d not in EXTRA_CLOSED


def next_business_day(d: date) -> date:
    d += timedelta(days=1)
    while not is_business_day(d):
        d += timedelta(days=1)
    return d


def business_days(start: date, n: int) -> list:
    out, d = [], start
    while not is_business_day(d):
        d += timedelta(days=1)
    while len(out) < n:
        if is_business_day(d):
            out.append(d)
        d += timedelta(days=1)
    return out


def earliest_date(today: date, order_date: date, assembled: bool, assembly_done: Optional[date]) -> Optional[date]:
    """Flat pack: next business day after the order. Assembled: at least the day after assembly."""
    base = next_business_day(today)
    if assembled:
        if assembly_done is None:
            return None
        return max(base, next_business_day(assembly_done))
    return max(base, next_business_day(order_date))


Dur = Callable[[tuple, tuple], float]  # minutes between two points


def _feasible(seq, depot, dur: Dur, s: Settings) -> bool:
    """seq = [(slot, point, handling)] in slot order. Check each stop can start inside its slot."""
    t = s.day_start_hour * 60
    prev = depot
    for slot, point, handling in seq:
        start, end = SLOTS[slot][2] * 60, SLOTS[slot][3] * 60
        t += dur(prev, point)
        t = max(t, start)
        if t > end:
            return False
        t += s.service_handling_min if handling else s.service_min
        prev = point
    return True


def _route_min(seq, depot, dur: Dur) -> float:
    pts = [depot] + [p for _, p, _ in seq] + [depot]
    return sum(dur(a, b) for a, b in zip(pts, pts[1:]))


def evaluate_day(plan: DayPlan, address: str, point: tuple, handling: bool, depot: tuple,
                 dur: Dur, s: Settings) -> Option:
    # same address already on that day -> ride along in the same slot
    for b in plan.bookings:
        if b.address and norm_address(b.address) == norm_address(address):
            return Option(plan.day, "Open", b.slot, 0.0, f"Same address as {b.label}")

    free = [i for i in range(len(SLOTS)) if i not in plan.taken()]
    if not free:
        return Option(plan.day, "Full", note="All 3 slots taken")

    located = sorted([(b.slot, b.point, b.handling) for b in plan.bookings if b.point], key=lambda x: x[0])
    base = _route_min(located, depot, dur) if located else 0.0

    best = None
    for i in free:
        seq = sorted(located + [(i, point, handling)], key=lambda x: x[0])
        if not _feasible(seq, depot, dur, s):
            continue
        extra = _route_min(seq, depot, dur) - base
        if best is None or extra < best[1]:
            best = (i, extra)

    if best is None:
        return Option(plan.day, "Full", note="No slot fits the drive times")
    if not located:
        return Option(plan.day, "Open", best[0], best[1], "New route day")
    if best[1] <= s.detour_limit_min:
        return Option(plan.day, "Open", best[0], best[1], "On the way")
    return Option(plan.day, "Different direction", best[0], best[1], f"Adds {best[1]:.0f} min of driving")


def plan_options(plans: dict, days: list, earliest: Optional[date], address: str, point: tuple,
                 handling: bool, depot: tuple, dur: Dur, s: Settings) -> list:
    """Evaluate each candidate day and mark one as Recommended."""
    if dur(depot, point) > s.far_limit_min:
        return [Option(d, "Too far", note="Over the in-town drive limit, Kevin schedules by hand") for d in days]

    out = []
    for d in days:
        if earliest is None or d < earliest:
            out.append(Option(d, "Not ready", note="Before the earliest delivery date"))
            continue
        out.append(evaluate_day(plans.get(d, DayPlan(d)), address, point, handling, depot, dur, s))

    open_opts = [o for o in out if o.status == "Open"]
    on_route = [o for o in open_opts if o.note != "New route day"]
    pick = min(on_route, key=lambda o: (o.extra_min, o.day)) if on_route else (open_opts[0] if open_opts else None)
    if pick:
        pick.status = "Recommended"
    return out
