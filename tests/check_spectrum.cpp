#include "../Spectro18_V_Flu/SpectrumStats.h"
#include <cassert>
#include <cmath>

int main() {
  SpectrumStats varying, constant;
  for (int i = 1; i <= 10; i++) {
    varying.add(i);
    constant.add(123.5f);
  }
  assert(varying.count == 10);
  assert(std::fabs(varying.mean - 5.5f) < 0.00001f);
  assert(std::fabs(varying.sd() - std::sqrt(82.5f / 9)) < 0.00001f);
  assert(constant.mean == 123.5f && constant.sd() == 0);
  varying = SpectrumStats{};
  assert(varying.count == 0 && varying.sd() == 0);
}
