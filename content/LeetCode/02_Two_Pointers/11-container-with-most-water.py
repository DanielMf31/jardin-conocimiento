## Solucion 1 Fuerza Bruta

## O(n²) temporal
## O(1) espacial

class Solution:
    def maxArea(self, height: List[int]) -> int:
        n = len(height)
        mejor = 0
        for i in range(n):
            for j in range(i + 1, n):
                area = min(height[i],height[j]) * (j-i)
                mejor = max(mejor, area)
        return mejor
    
# Solución 2 - Two pointers con greedy local

## Tiempo O(n)
## Espacio O(1)
class Solution:
    def maxArea(self, height: List[int]) -> int:
        left, right = 0, len(height) - 1
        mejor = 0
        while left < right:
            ancho = right - left
            altura = min(height[left], height[right])
            mejor = max(mejor, altura * ancho)
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        return mejor


