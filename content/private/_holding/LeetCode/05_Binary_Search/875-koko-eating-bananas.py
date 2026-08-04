import math

class Solution:
    def minEatingSpeed(self, piles: List[int], h: int) -> int:
        def horas_necesarias(k):
            return sum(math.ceil(p / k) for p in piles)
        
        left, right = 1, max(piles)
        while left < right:
            mid = left + (right - left) // 2
            if horas_necesarias(mid) <= h:
                right = mid
            else:
                left = mid + 1
        return left
    