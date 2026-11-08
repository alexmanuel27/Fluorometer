#pragma once
#include <stdint.h>
#include "SpectrumStats.h"

constexpr uint8_t SAMPLE_COUNT = 10;
constexpr uint8_t CHANNEL_COUNT = 18;

struct WhiteReference {
  float readings[SAMPLE_COUNT][CHANNEL_COUNT] = {};

  SpectrumStats stats(uint8_t channel) const {
    SpectrumStats result;
    for (uint8_t i = 0; i < SAMPLE_COUNT; i++) result.add(readings[i][channel]);
    return result;
  }

  bool valid(bool requireSignal = true) const {
    for (const auto &reading : readings)
      for (float value : reading)
        if (!isfinite(value) || value < 0) return false;
    return !requireSignal || (stats(1).mean > 0 && stats(9).mean > 0);
  }
};
