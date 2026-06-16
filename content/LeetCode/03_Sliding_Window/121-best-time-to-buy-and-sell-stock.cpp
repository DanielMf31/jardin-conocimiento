// LeetCode 121 — Best Time to Buy and Sell Stock (C++). Contraste con .py.
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 121-best-time-to-buy-and-sell-stock.cpp -o s && ./s
#include <algorithm>
#include <cassert>
#include <climits>
#include <vector>

class Solution {
 public:
  int maxProfit(std::vector<int>& prices) {
    int min_price = INT_MAX;  // Python: float('inf')
    int best = 0;
    for (int p : prices) {
      min_price = std::min(min_price, p);
      best = std::max(best, p - min_price);
    }
    return best;
  }
};

int main() {
  Solution s;
  std::vector<int> a = {7, 1, 5, 3, 6, 4};
  std::vector<int> b = {7, 6, 4, 3, 1};
  assert(s.maxProfit(a) == 5);
  assert(s.maxProfit(b) == 0);
  return 0;
}
