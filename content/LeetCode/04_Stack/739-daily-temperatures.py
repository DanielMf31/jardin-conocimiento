class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        n = len(temperatures)
        answer = [0] * n
        stack = []

        for i, temp in enumerate(temperatures):
            while stack and temperatures[stack[-1]] > temp:
                prev_i = stack.pop()
                answer[prev_i] = i - prev_i
            stack.append(i)

        return answer