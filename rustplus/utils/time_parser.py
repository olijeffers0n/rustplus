class TimeParser:

    def convert(self, time) -> str:
        
        input_time = float(time)
        input_time_minutes = input_time * 60
        HOURS = int(input_time_minutes // 60)
        MINUTES = int(input_time_minutes % 60)

        time_string = "{}:0{}" if MINUTES <= 9 else "{}:{}"

        return time_string.format(HOURS, MINUTES)