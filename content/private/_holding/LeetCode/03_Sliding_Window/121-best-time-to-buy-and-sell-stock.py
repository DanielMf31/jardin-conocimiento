## Solución 1- Fuerza bruta

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        n = len(prices)
        best = 0
        for i in range(n):
            for j in range(n+1,n):
                best = max(best, prices[j] - prices[i])
            return best
        
## Tiempo - O(n²) porque hay dos bucles
## Espacio - O(1)

# Solución 2 - One-pass tracking del mínimo

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        min_price = float("inf")
        best = 0
        for price in prices:
            min_price = min(min_price, price)
            best = max(best, price - min_price)
        return best
    
# Tiempo - O(n)
# Espacio - O(1)

# Solución 3 - Two Pointers / sliding window explícito

class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        left, right = 0, 1
        best = 0
        while right < len(prices):
            if prices[left] < prices[right]:
                best = max(best, prices[right] - prices[left])
            else:
                left = right
            right += 1
        return best
    
    