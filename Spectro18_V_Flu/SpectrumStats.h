#pragma once
#include <math.h>

// Welford: sample standard deviation (n - 1), stable for small variations.
struct SpectrumStats {
  float mean = 0;
  float m2 = 0;
  unsigned count = 0;
  void add(float value) {
    count++;
    const float delta = value - mean;
    mean += delta / count;
    m2 += delta * (value - mean);
  }
  float sd() const { return count > 1 ? sqrtf(fmaxf(0, m2 / (count - 1))) : 0; }
};
