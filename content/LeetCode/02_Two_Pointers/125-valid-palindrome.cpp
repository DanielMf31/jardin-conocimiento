// LeetCode 125 — Valid Palindrome (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 125-valid-palindrome.cpp -o s && ./s
#include <cassert>
#include <cctype>
#include <string>

class Solution {
 public:
  bool isPalindrome(std::string s) {
    int i = 0, j = static_cast<int>(s.size()) - 1;
    while (i < j) {
      // Python: s[i].isalnum(); aquí std::isalnum con cast a unsigned char.
      while (i < j && !std::isalnum(static_cast<unsigned char>(s[i]))) ++i;
      while (i < j && !std::isalnum(static_cast<unsigned char>(s[j]))) --j;
      if (std::tolower(static_cast<unsigned char>(s[i])) !=
          std::tolower(static_cast<unsigned char>(s[j])))
        return false;
      ++i;
      --j;
    }
    return true;
  }
};

int main() {
  Solution s;
  assert(s.isPalindrome("A man, a plan, a canal: Panama") == true);
  assert(s.isPalindrome("race a car") == false);
  assert(s.isPalindrome(" ") == true);
  return 0;
}
