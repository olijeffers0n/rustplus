from collections.abc import Sequence


class Serializable:
    def serialize(self):
        data = {}
        for k, v in self.__dict__.items():
            key = k if k[0] != "_" else k[1:]
            if isinstance(v, Serializable):
                data[key] = v.serialize()
            elif isinstance(v, Sequence) and all(
                isinstance(element, Serializable) for element in v
            ):
                data[key] = [e.serialize() for e in v]
            else:
                data[key] = str(v)
        return data
