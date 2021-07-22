class TimeParser:
    def convert(self, time) -> str:
        input_time = float(time)
        input_time_minutes = input_time * 60
        HOURS = int(input_time_minutes // 60)
        MINUTES = int(input_time_minutes % 60)
        
        if MINUTES <= 9:
            time_string = "{}:0{}".format(HOURS, MINUTES)
        else:
            time_string = "{}:{}".format(HOURS, MINUTES)

        return time_string