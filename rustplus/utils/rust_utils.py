from ..api.structures import RustTime

def format_time(protobuf) -> RustTime:

    def convert_time(time) -> str:

        HOURS, MINUTES = divmod(time * 60, 60)

        return f"{int(HOURS)}:0{int(MINUTES)}" if MINUTES <= 9 else f"{int(HOURS)}:{int(MINUTES)}"

    SUNRISE = convert_time(protobuf.response.time.sunrise)
    SUNSET = convert_time(protobuf.response.time.sunset)
    PARSED_TIME = convert_time(protobuf.response.time.time)

    return RustTime(protobuf.response.time.dayLengthMinutes, SUNRISE, SUNSET, PARSED_TIME, protobuf.response.time.time)