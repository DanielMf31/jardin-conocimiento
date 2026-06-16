## Solucion de fuerza bruta

from ast import List


class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] == nums[j]:
                    return True
        return False

## Solucion 2 - Ordenar primero, comparar adyacentes

class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        nums.sort()
        for i in range(1, len(nums)):
            if nums[i] == nums[i-1]:
                return True
        return False
    
## Solucion 3 

class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        vistos = set()
        for num in nums:
            if num in vistos:
                return True
            vistos.add(num)
        return False
    
## Solución 4

class Solution:
    def hasDuplicate(self, nums: List[int]) -> bool:
        return len(set(nums)) < len(nums)
    



