## Solucion 1 - Fuerza bruta

# Tiempo O(n²)
# Espacio O(1)

class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        answer = []
        for i in range(n):
            prod = 1
            for j in range(n):
                if j != i:
                    prod *= nums[j]
            answer.append(prod)
        return answer
    
## Solucion 2 - Con división (prohibida)

class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        total = 1
        for i in nums:
            total *= nums
        return [total // n for n in nums]
    
## Solution 3 - Forma canónica (prefix*suffix products)
class Solution:
    def productExceptSelf(self, nums: List[int]) -> List[int]:
        n = len(nums)
        prefix = [1] * n
        suffix = [1] * n
        
        ## prefix[i]
        for i in range(1,n):
            prefix[i] = prefix[i-1] * nums[i-1]
        
        # suffix[i]
        for i in range(n-2, -1, -1):
            suffix[i] = suffix[i+1] * nums[i+1]
    
        return [prefix[i] * suffix[i] for i in range(n)]


