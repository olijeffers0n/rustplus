class CoordUtil:
    
    def format(self, x, y, map_size) -> tuple:
        y = map_size - y - 100
        x -= 100

        if x < 0:
            x = 0
        if x > map_size:
            x = map_size - 200
        if y < 0:
            y = 0
        if y > map_size:
            y = map_size-200

        return (x,y)