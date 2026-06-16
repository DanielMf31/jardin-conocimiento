// LeetCode 15 — 3Sum (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 15-3sum.cpp -o s && ./s
#include <algorithm>
#include <cassert>
#include <vector>

class Solution {
 public:
  std::vector<std::vector<int>> threeSum(std::vector<int>& nums) {
    std::sort(nums.begin(), nums.end());
    std::vector<std::vector<int>> res;
    int n = static_cast<int>(nums.size());
    for (int i = 0; i < n - 2; ++i) {
      if (i > 0 && nums[i] == nums[i - 1]) continue;  // saltar duplicado del pivote
      int lo = i + 1, hi = n - 1;
      while (lo < hi) {
        int sum = nums[i] + nums[lo] + nums[hi];
        if (sum < 0) {
          ++lo;
        } else if (sum > 0) {
          --hi;
        } else {
          res.push_back({nums[i], nums[lo], nums[hi]});
          ++lo;
          --hi;
          while (lo < hi && nums[lo] == nums[lo - 1]) ++lo;  // saltar duplicados
          while (lo < hi && nums[hi] == nums[hi + 1]) --hi;
        }
      }
    }
    return res;
  }
};

int main() {
  Solution s;
  std::vector<int> n = {-1, 0, 1, 2, -1, -4};
  auto r = s.threeSum(n);
  assert(r.size() == 2);  // {-1,-1,2} y {-1,0,1}
  std::vector<int> empty = {0, 1, 1};
  assert(s.threeSum(empty).empty());
  return 0;
}
