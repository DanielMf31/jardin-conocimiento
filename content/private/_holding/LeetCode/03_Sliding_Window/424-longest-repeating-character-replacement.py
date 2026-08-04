from collections import Counter

class Solution:
    def characterReplacement(self, s: str, k: int) -> int:
        count = Counter()
        left = 0
        right = 0
        for right, char in enumerate(s):
            count[char] += 1
            while(right-left + 1) - max(count.values()) > k:
                count[s[left]] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best