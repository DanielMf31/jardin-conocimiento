// LeetCode 1 — Two Sum (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 1-two-sum.cpp -o s && ./s
#include <cassert>
#include <unordered_map>
#include <vector>

class Solution {
 public:
  std::vector<int> twoSum(std::vector<int>& nums, int target) {
    std::unordered_map<int, int> seen;  // valor -> índice (Python: dict)
    for (int i = 0; i < static_cast<int>(nums.size()); ++i) {
      int need = target - nums[i];
      auto it = seen.find(need);
      if (it != seen.end()) return {it->second, i};
      seen[nums[i]] = i;
    }
    return {};
  }
};

int main() {
  Solution s;
  std::vector<int> n = {2, 7, 11, 15};
  assert((s.twoSum(n, 9) == std::vector<int>{0, 1}));
  std::vector<int> m = {3, 2, 4};
  assert((s.twoSum(m, 6) == std::vector<int>{1, 2}));
  return 0;
}
