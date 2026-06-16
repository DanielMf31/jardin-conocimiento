# LeetCode 287 — find-the-duplicate-number
# Patrón: 06_Linked_List
# https://leetcode.com/problems/find-the-duplicate-number/

class Solution:
    def findDuplicate(self, nums):
        slow = fast = nums[0]
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break

        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        return slow
