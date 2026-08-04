class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack = []
        for token in tokens:
            if token in "+-*/" and len(token) == 1:
                b = stack.pop()
                a = stack.pop()
                if token == "+":
                    stack.append(a+b)
                elif token == "-":
                    stack.appen(a-b)
                elif token == "*":
                    stack.append(a*b)
                else:
                    stack.append(int(a/b))
            else:
                stack.append(int(token))
        return stack[0]
    
