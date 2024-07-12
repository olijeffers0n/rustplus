from enum import Enum


class Emoji(Enum):
    ANGRY = ":angry+0:"
    COFFEE_CAN = ":coffeecan+0:"
    EYEBROW = ":eyebrow+0:"
    FUNNY = ":funny+0:"
    HAPPY = ":happy+0:"
    LAUGH = ":laugh+0:"
    LOVE = ":love+0:"
    MASK = ":mask+0:"
    NERVOUS = ":nervous+0:"
    NEUTRAL = ":neutral+0:"
    HEART_ROCK = ":heartrock+0:"
    SMILE_CRY = ":smilecry+0:"
    COOL = ":cool+0:"
    LIGHT = ":light+0:"
    WORRIED = ":worried+0:"
    HEART = ":heart:"
    SKULL = ":skull:"
    EYES = ":eyes:"
    DANCE = ":dance:"
    EXCLAMATION = ":exclamation:"
    TRUMPET = ":trumpet:"
    WAVE = ":wave:"
    YELLOW_PIN = ":yellowpin:"
    SCIENTIST = ":scientist+0:"

    def __str__(self):
        return self.value
