# LeetCode 141 — linked-list-cycle
# Patrón: 06_Linked_List
# https://leetcode.com/problems/linked-list-cycle/

class Solution:
    def hasCycle(self, head):
        slow = fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True
        return False
