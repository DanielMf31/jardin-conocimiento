class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False

        # Paso 1: binary search en la primera columna para localizar la fila
        top, bottom = 0, len(matrix) - 1
        while top <= bottom:
            mid_row = top + (bottom - top) // 2
            if target < matrix[mid_row][0]:
                bottom = mid_row - 1
            elif target > matrix[mid_row][-1]:
                top = mid_row + 1
            else:
                # target podría estar en esta fila
                # Paso 2: binary search dentro de la fila
                left, right = 0, len(matrix[mid_row]) - 1
                while left <= right:
                    mid_col = left + (right - left) // 2
                    if matrix[mid_row][mid_col] == target:
                        return True
                    elif matrix[mid_row][mid_col] < target:
                        left = mid_col + 1
                    else:
                        right = mid_col - 1
                return False

        return False
