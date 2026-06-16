## Solucion 1 - Has map (No cumple la restricción de O(1))

class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        visto = {}
        for i, num in enumerate(numbers):
            comp = target - num
            if comp in visto:
                return [visto[comp] + 1, i+1]
            visto[num] = i
        return []
    
## Solució 2 - Two Pointers convergentes

class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        left, right = 0, len(numbers) - 1
        while left < right:
            suma = numbers[left] + numbers[right]
            if suma == target:
                return [left + 1, right + 1]
            elif suma < target:
                left += 1
            else:
                right += 1
            return []
    