// LeetCode 226 — Invert Binary Tree (C++). Contraste con la versión Python (.py).
// Recursión sobre árbol con punteros + gestión de memoria (en Python: GC).
// g++ -std=c++20 -Wall -Wextra -fsanitize=address 226-invert-binary-tree.cpp -o s && ./s
#include <cassert>
#include <utility>
#include <vector>

struct TreeNode {
  int val;
  TreeNode* left;
  TreeNode* right;
  explicit TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}
};

class Solution {
 public:
  TreeNode* invertTree(TreeNode* root) {
    if (root == nullptr) return nullptr;  // caso base
    std::swap(root->left, root->right);   // intercambiar hijos
    invertTree(root->left);               // recursión
    invertTree(root->right);
    return root;
  }
};

static std::vector<int> inorder(TreeNode* n) {
  if (!n) return {};
  std::vector<int> out = inorder(n->left);
  out.push_back(n->val);
  auto r = inorder(n->right);
  out.insert(out.end(), r.begin(), r.end());
  return out;
}
static void free_tree(TreeNode* n) {
  if (!n) return;
  free_tree(n->left);
  free_tree(n->right);
  delete n;
}

int main() {
  //        4
  //      /   \
  //     2     7
  auto* root = new TreeNode(4);
  root->left = new TreeNode(2);
  root->right = new TreeNode(7);
  Solution s;
  TreeNode* inv = s.invertTree(root);
  assert((inorder(inv) == std::vector<int>{7, 4, 2}));
  free_tree(inv);
  assert(s.invertTree(nullptr) == nullptr);
  return 0;
}
