## Solucion 1

class Solution:
    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        result =  []
        for i in range(len(nums) - k +1):
            result.append(max(nums[i:i+k]))
        return result
    
## SOlción 2 - Max heap con limpieza peresza

import heapq
class Solution:
    def maxSlidingWindow(self, nums: List[int], k:int) -> List[int]:
        heap = []
        result = []
        for right, num in enumerate(nums):
            heapq.heappush(heap, (-num, right))
            while heap[0][1] <= right - k:
                heapq.heappop(heap)
            if right >= k - 1:
                result.append(-heap[0][0])
        return result

## Solución 3 - dequeu monotónica decrececiente

from collections import deque

class Solution:
    def maxSlidignWndow(self, nums: List[int], k: int) -> List[int]:
        dq = deque()
        result = []
        for right, num in enumerate(nums):
            while dq and nums[dq[-1]] <= num:
                dp.pop()
            dq.append(right)
            if dq[0] <= right - k:
                dq.popleft()
            if right >= k - 1:
                result.append(nums[dq[0]])
        return result