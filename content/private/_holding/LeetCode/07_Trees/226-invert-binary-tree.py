# LeetCode 226 — invert-binary-tree
# Patrón: 07_Trees
# https://leetcode.com/problems/invert-binary-tree/

class Solution:
    def invertTree(self, root: Optional[Treenode]) -> Optional[TreeNode]:
        if not root:
            return None
        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root
