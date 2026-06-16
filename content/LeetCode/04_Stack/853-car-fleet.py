## Solucion 1: Sort + iterar

class Solution:
    def carFleet(self, target: int, position: List[int], speed: List[int]) -> int:
        cars = sorted(zip(position, speed), reverse=True)

        fleets = 0
        current_fleet_eta = 0

        for pos, spd in cars:
            eta = (target - pos) / spd
            if eta > current_fleet_eta:
                fleets += 1
                current_fleet_eta = eta
        
        return fleets

## Solución 2: Versión con stack explícito

class Solution:
    def carFleet(self, target: int, positions: List[int], speeds: List[int]) -> int:
        cars = sorted(zip(positions, speeds), reverse=True)
        stack = []
        for pos, spd in cars:
            eta = (target - pos) / spd
            if not stack or eta > stack[-1]:
                stack.append(eta)
        return len(stack)
    
