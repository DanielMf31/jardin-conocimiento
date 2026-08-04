## SOlucion 1 - Stack con dict de mapeo (la canónica)

class Solution:
    def isValid(self, s: str) -> bool:
        pairs = {")" : "(", "]": "[", "}":"{"}
        stack = []

        for char in s:
            if char in pairs:
                if not stack or stack[-1] != pairs[char]:
                    return False
                stack.pop()
            else:
                stack.append(char)

        return not stack