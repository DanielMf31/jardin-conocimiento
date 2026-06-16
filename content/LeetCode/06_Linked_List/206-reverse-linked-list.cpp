// LeetCode 206 — Reverse Linked List (C++). Contraste con la versión Python (.py).
// Aquí se ve la diferencia GRANDE con Python: punteros crudos y gestión de nodos.
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 206-reverse-linked-list.cpp -o s && ./s
#include <cassert>
#include <vector>

struct ListNode {
  int val;
  ListNode* next;
  explicit ListNode(int v) : val(v), next(nullptr) {}
};

class Solution {
 public:
  ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    while (head != nullptr) {
      ListNode* next = head->next;  // guardar el siguiente antes de reapuntar
      head->next = prev;            // invertir el enlace
      prev = head;
      head = next;
    }
    return prev;
  }
};

static ListNode* build(const std::vector<int>& v) {
  ListNode dummy(0);
  ListNode* t = &dummy;
  for (int x : v) {
    t->next = new ListNode(x);
    t = t->next;
  }
  return dummy.next;
}
static std::vector<int> to_vec(ListNode* h) {
  std::vector<int> out;
  for (; h; h = h->next) out.push_back(h->val);
  return out;
}
static void free_list(ListNode* h) {
  while (h) {
    ListNode* n = h->next;
    delete h;  // sin esto: leak (en Python lo haría el GC)
    h = n;
  }
}

int main() {
  ListNode* head = build({1, 2, 3, 4, 5});
  Solution s;
  ListNode* rev = s.reverseList(head);
  assert((to_vec(rev) == std::vector<int>{5, 4, 3, 2, 1}));
  free_list(rev);
  assert(s.reverseList(nullptr) == nullptr);
  return 0;
}
