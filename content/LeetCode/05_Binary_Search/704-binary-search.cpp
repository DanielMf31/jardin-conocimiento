// LeetCode 704 — Binary Search (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 704-binary-search.cpp -o s && ./s
#include <cassert>
#include <vector>

class Solution {
 public:
  int search(std::vector<int>& nums, int target) {
    int lo = 0, hi = static_cast<int>(nums.size()) - 1;
    while (lo <= hi) {
      int mid = lo + (hi - lo) / 2;  // evita overflow vs (lo+hi)/2
      if (nums[mid] == target) return mid;
      if (nums[mid] < target)
        lo = mid + 1;
      else
        hi = mid - 1;
    }
    return -1;
  }
};

int main() {
  Solution s;
  std::vector<int> n = {-1, 0, 3, 5, 9, 12};
  assert(s.search(n, 9) == 4);
  assert(s.search(n, 2) == -1);
  return 0;
}
