class CoordUtil:
    
    def format(self, x, y, map_size) -> tuple:
        
        y = map_size - y - 75
        x -= 75

        if x < 0:
            x = 0
        if x > map_size:
            x = map_size - 150
        if y < 0:
            y = 0
        if y > map_size:
            y = map_size-150

        return (x,y)