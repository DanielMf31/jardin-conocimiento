## Solucion 1 - Fuerza bruta

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        n = len(nums)
        for i in range(n):
            for j in range(i + 1, n):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
    
## Solucion 2 - Hash map en dos pasos

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:

        indices = {num: i for i, num in enumerate(nums)}

        for i, num in enumerate(nums):
            complemento = target - num
            if complemento in indices and indices[complemento] != i:
                return [i, indices[complemento]]
            return []

## Solucion 3 - Has map en una sola pasada (La idiomatica)

class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        visto = {}
        for i, num in enumerate(nums):
            complemento = target - num
            if complemento in visto:
                return [visto[complemento], i]
            visto[num] = i
        return []
    

