## Solucion 1 - Fuerza bruta

class Solution:
    def trap(self, height: List[ìnt]) -> int:
        n = len(height)
        total = 0
        for i in range(n):
            max_left = max(height[:i+1]) if i > 0 else height[i]
            max_right = max(height[i:]) if i < n-1 else height[i]
            agua = min(max_left, max_right) - height[i]
            total += max(0, agua)
            return total

## Tiempo - O(n²) ya que cada slicing cuesta O(n) por cada i.
## Espacio - O(1)

## Solucion 2 - Prefix max + Suffix max

## No entiendo exáctamente lo del Preffix Suffix tengo que mirarlo más

def trap(self, height: List[int]) -> int:
    n = len(height)
    if n == 0:
        return 0
    
    max_left = [0] * n
    max_right = [0] * n

    max_left[0] = height[0]
    for i in range(1,n):
        max_left[i] = max(max_left[i-1], height[i])

    max_right[n-1] = height[n-1]
    for i in range(n-2, -1, -1):
        max_right[i] = max(max_right[i+1], height[i])

    total = 0
    for i in range(n):
        total += min(max_left[i], max_right[i+1]) -  height[i]

    return total

## Tiempo - O(n)
## Espacio - O(n)



## Solución 3 - Two Pointers

class Solution:
    def trap(self, height: List[int]) -> int:
        if not height:
            return 0
        
        left, right = 0, len(height) - 1
        max_left, max_right = height[left], height[right]

        while left < right:
            if max_left < max_right:
                left += 1
                max_left = max(max_left, height[left])
                total += max_left - height[left]
            else:
                right -= 1
                max_right = max(max_right, height[right])
                total += max_right - height[right]
        return total
    
## Tiempo O(n) porque el hay un sólo bucle y el resto es con punteros
## Espacio O(1) ya que no necesita array de memoria



