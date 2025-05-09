from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class TimeSeriesValue:
    value: float
    date: datetime


class EntityWithPower(Protocol):
    power: list[TimeSeriesValue]


def calc_inverters_generation(entities_with_power: list[EntityWithPower]) -> float:
    if not entities_with_power:
        return 0.0

    total_generation = 0.0

    for entity in entities_with_power:
        if len(entity.power) < 2:
            continue

        for i in range(len(entity.power) - 1):
            try:
                cur_power = entity.power[i].value
                next_power = entity.power[i + 1].value

                if cur_power < 0 or next_power < 0:
                    continue

                delta_time = (
                    entity.power[i + 1].date - entity.power[i].date
                ).total_seconds() / 3600

                if delta_time <= 0 or delta_time > 24:
                    continue

                generation = (cur_power + next_power) / 2 * delta_time
                total_generation += generation

            except (AttributeError, TypeError):
                continue

    return total_generation
