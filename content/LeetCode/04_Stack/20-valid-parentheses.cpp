// LeetCode 20 — Valid Parentheses (C++). Contraste con la versión Python (.py).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 20-valid-parentheses.cpp -o s && ./s
#include <cassert>
#include <stack>
#include <string>
#include <unordered_map>

class Solution {
 public:
  bool isValid(std::string s) {
    std::unordered_map<char, char> close_to_open = {
        {')', '('}, {']', '['}, {'}', '{'}};
    std::stack<char> st;
    for (char c : s) {
      if (c == '(' || c == '[' || c == '{') {
        st.push(c);
      } else {
        if (st.empty() || st.top() != close_to_open[c]) return false;
        st.pop();
      }
    }
    return st.empty();
  }
};

int main() {
  Solution s;
  assert(s.isValid("()[]{}") == true);
  assert(s.isValid("(]") == false);
  assert(s.isValid("([{}])") == true);
  assert(s.isValid("(") == false);
  return 0;
}
