def convert_time(time) -> str:
    hours, minutes = divmod(time * 60, 60)

    return (
        f"{int(hours)}:0{int(minutes)}"
        if minutes <= 9
        else f"{int(hours)}:{int(minutes)}"
    )
