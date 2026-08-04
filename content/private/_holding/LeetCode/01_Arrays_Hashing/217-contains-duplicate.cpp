// LeetCode 217 — Contains Duplicate (C++). Contraste con la versión Python (.py).
// Compila: g++ -std=c++20 -Wall -Wextra -fsanitize=address 217-contains-duplicate.cpp -o s && ./s
#include <cassert>
#include <unordered_set>
#include <vector>

class Solution {
 public:
  bool hasDuplicate(std::vector<int>& nums) {
    std::unordered_set<int> seen;  // Python: set()
    for (int n : nums) {
      if (!seen.insert(n).second) return true;  // .second=false si ya estaba
    }
    return false;
  }
};

int main() {
  Solution s;
  std::vector<int> a = {1, 2, 3, 1};
  std::vector<int> b = {1, 2, 3, 4};
  assert(s.hasDuplicate(a) == true);
  assert(s.hasDuplicate(b) == false);
  return 0;
}
