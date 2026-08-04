## Solución 1 - Fuerza bruta con set (NO recomendada)

class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        n = len(nums)
        resultado = set()
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    if nums[i] + nums[j] + nums[k] == 0:
                        triplete = tuple(sorted([nums[i], nums[j], nums[k]]))
                        resultado.add(triplete)
        return [list(t) for t in resultado]
    
## Solución 2 - Sort + fix one `two pointers (la canónica)

class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        nums.sort()
        n = len(nums)
        resultado = []

        for i in range(n-2):
            if i > 0 and nums[i] == nums[i-1]:
                continue
            if nums[i] > 0:
                break

            left, right = i + 1, n - 1
            while left < right:
                suma = nums[i] + nums[left] + nums[right]
                if suma == 0:
                    resultado.append([nums[i], nums[left], nums[right]])
                    while left < right and nums[left] == nums[left + 1]:
                        left +=1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    left += 1
                    right -= 1
                elif suma < 0:
                    left += 1
                else:
                    right -= 1
        return resultado
    
    S
