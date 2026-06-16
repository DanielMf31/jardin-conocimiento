class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        # Filas

        for r in range(9):
            seen = set()
            for c in range(9):
                v = board[r][c]
                if v == ".":
                    continue
                if v in seen:
                    return False
                seen.add(v)

        # Columnas

        for c in range(9):
            seen = set()
            for r in range(9):
                v = board[r][c]
                if v == ".":
                    continue
                if v in seen:
                    return False
                seen.add(v)

        # Boxes 3x3

        for box_r in range(3):
            for box_c in range(3):
                seen = set()
                for r in range(box_r *3, box_r *3 + 3):
                    for c in range(box_c *3, box_c * 3 + 3):
                        v = board[r][c]
                        if v == ".":
                            continue
                        if v in seen:
                            return False
                        seen.add(v)

        return True
    
## Solucion 2 - Limpia con memoria de dicts

from collections import defaultdict

class Solution:
    def isValidSudoku(self, board: List[List[int]]) -> bool:
        rows = defaultdict(set)
        cols = defaultdict(set)
        boxes = defaultdict(set)

        for r in range(9):
            for c in range(9):
                v = board[r][c]
                if v == ".":
                    continue
                box_key = (r // 3, c // 3)
                if v in rows[r] or v in cols[c] or v in boxes[box_key]:
                    return False
                rows[r].add(v)
                cols[c].add(v)
                boxes[box_key].add(v)
            return True
        
## Solucion 3 - Un solo set con claves compuestas(la elegante)

