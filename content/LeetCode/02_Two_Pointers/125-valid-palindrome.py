## Solución 1: Limpiar y comparar con reverse (No usa 2 pointers)

class Solution:
    def isPalindrome(self, s: str) -> bool:
        limpio = "".join(c.lower() for c in s if c.isalnum())
        return limpio == limpio[::-1]
    
## Solución 2: Two Pointers sobre string limpio

class Solution:
    def isPalindrome(self, s: str) -> bool:
        limpio = "".join(c.lower() for c in s if c.isalnum())
        left, right = 0, len(s) - 1
        while left < right:
            if limpio[left] != limpio[right]:
                return False
            left += 1
            right -= 1
        return True
    
## Solución 3: Two pointers sobre string original saltándonos carácteres

class Solution:
    def isPalindrome(self, s: str) -> bool:
        left, right = 0, len(s) - 1
        while left < right:
            while left < right and not s[left].isalnum():
                left += 1
            while left < right and not s[right].isalnum():
                right -= 1
            if s[left].lower() != s[right].lower():
                return False
            left += 1
            right -= 1
        return True
    
