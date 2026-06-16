// LeetCode 49 — Group Anagrams (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 49-group-anagrams.cpp -o s && ./s
#include <algorithm>
#include <cassert>
#include <string>
#include <unordered_map>
#include <vector>

class Solution {
 public:
  std::vector<std::vector<std::string>> groupAnagrams(
      std::vector<std::string>& strs) {
    std::unordered_map<std::string, std::vector<std::string>> groups;
    for (const std::string& s : strs) {
      std::string key = s;
      std::sort(key.begin(), key.end());  // clave = string ordenado
      groups[key].push_back(s);
    }
    std::vector<std::vector<std::string>> out;
    out.reserve(groups.size());
    for (auto& [key, group] : groups) out.push_back(std::move(group));
    return out;
  }
};

int main() {
  Solution s;
  std::vector<std::string> in = {"eat", "tea", "tan", "ate", "nat", "bat"};
  auto res = s.groupAnagrams(in);
  std::size_t total = 0;
  for (auto& g : res) total += g.size();
  assert(res.size() == 3);  // {eat,tea,ate} {tan,nat} {bat}
  assert(total == 6);
  return 0;
}
