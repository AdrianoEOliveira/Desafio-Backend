interface TimeseriesValue {
  value: number;
  date: Date;
}

interface EntityWithPower {
  power: TimeseriesValue[];
}

function calcInvertersGeneration(entitiesWithPower: EntityWithPower[]): number {
  if (!entitiesWithPower || entitiesWithPower.length === 0) {
    return 0;
  }

  let totalGeneration = 0;

  for (const entity of entitiesWithPower) {
    if (!entity.power || entity.power.length < 2) {
      continue;
    }

    for (let i = 0; i < entity.power.length - 1; i++) {
      try {
        const currentPower = entity.power[i].value;
        const nextPower = entity.power[i + 1].value;

        if (
          currentPower < 0 ||
          nextPower < 0 ||
          isNaN(currentPower) ||
          isNaN(nextPower)
        ) {
          continue;
        }

        const currentDate = entity.power[i].date;
        const nextDate = entity.power[i + 1].date;

        if (!(currentDate instanceof Date) || !(nextDate instanceof Date)) {
          continue;
        }

        const timeDelta =
          (nextDate.getTime() - currentDate.getTime()) / (1000 * 3600);

        if (timeDelta <= 0 || timeDelta > 24) {
          continue;
        }

        const generation = ((nextPower + currentPower) / 2) * timeDelta;
        totalGeneration += generation;
      } catch (error) {
        continue;
      }
    }
  }

  return parseFloat(totalGeneration.toFixed(6));
}
