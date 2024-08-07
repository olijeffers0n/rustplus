from enum import Enum


class Emoji(Enum):
    ANGRY = ":angry:"
    COFFEE_CAN = ":coffeecan:"
    EYEBROW = ":eyebrow:"
    FUNNY = ":funny:"
    HAPPY = ":happy:"
    LAUGH = ":laugh:"
    LOVE = ":love:"
    MASK = ":mask:"
    NERVOUS = ":nervous:"
    NEUTRAL = ":neutral:"
    HEART_ROCK = ":heartrock:"
    SMILE_CRY = ":smilecry:"
    COOL = ":cool:"
    LIGHT = ":light:"
    WORRIED = ":worried:"
    HEART = ":heart:"
    SKULL = ":skull:"
    EYES = ":eyes:"
    DANCE = ":dance:"
    EXCLAMATION = ":exclamation:"
    TRUMPET = ":trumpet:"
    WAVE = ":wave:"
    YELLOW_PIN = ":yellowpin:"
    SCIENTIST = ":scientist:"

    def __str__(self):
        return self.value
