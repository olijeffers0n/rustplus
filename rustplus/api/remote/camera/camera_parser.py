import dataclasses
from typing import Union, Tuple, List
from PIL import Image

from .camera_constants import LOOKUP_CONSTANTS


@dataclasses.dataclass
class RayData:
    distance: float
    alignment: float
    material: int


class Parser:
    def __init__(self, width, height) -> None:
        self.width = width
        self.height = height
        self.data_pointer = 0
        self._rays = None
        self._ray_lookback = [[0 for _ in range(3)] for _ in range(64)]
        self._sample_offset = 0
        self.colours = [
            [0.5, 0.5, 0.5],
            [0.8, 0.7, 0.7],
            [0.3, 0.7, 1],
            [0.6, 0.6, 0.6],
            [0.7, 0.7, 0.7],
            [0.8, 0.6, 0.4],
            [1, 0.4, 0.4],
            [1, 0.1, 0.1],
        ]

        self.output = [None for _ in range(self.width * self.height)]

    def handle_camera_ray_data(self, data) -> None:
        self._rays = data
        self.data_pointer = 0
        self._sample_offset = 2 * data.sample_offset
        while self._sample_offset >= 2 * self.width * self.height:
            self._sample_offset -= 2 * self.width * self.height
        self._ray_lookback = [[0 for _ in range(3)] for _ in range(64)]

    def step(self) -> None:

        if self._rays is None:
            return

        while True:
            if self.process_rays_batch():
                self._rays = None
                break

    def process_rays_batch(self) -> bool:
        if self._rays is None:
            return True

        for h in range(100):

            if self.data_pointer >= len(self._rays.ray_data) - 1:
                return True

            ray = self.next_ray(self._rays.ray_data)

            while self._sample_offset >= 2 * self.width * self.height:
                self._sample_offset -= 2 * self.width * self.height

            distance = ray[0]
            alignment = ray[1]
            material = ray[2]

            index1 = LOOKUP_CONSTANTS[self._sample_offset]
            self._sample_offset += 1
            index2 = int(LOOKUP_CONSTANTS[self._sample_offset] * self.width + index1)
            self._sample_offset += 1
            self.output[index2] = RayData(distance, alignment, material)

        return False

    def next_ray(self, ray_data) -> List[Union[float, int]]:
        byte = ray_data[self.data_pointer]
        self.data_pointer += 1

        if byte == 255:
            second_byte = ray_data[self.data_pointer]
            self.data_pointer += 1
            third_byte = ray_data[self.data_pointer]
            self.data_pointer += 1
            fourth_byte = ray_data[self.data_pointer]
            self.data_pointer += 1

            t = (second_byte << 2) | (third_byte >> 6)
            r = 63 & third_byte
            i = fourth_byte

            u = (3 * (int(t / 128) | 0) + 5 * (int(r / 16) | 0) + 7 * i) & 63
            self._ray_lookback[u][0] = t
            self._ray_lookback[u][1] = r
            self._ray_lookback[u][2] = i

        else:

            c = 192 & byte

            if c == 0:
                h = 63 & byte
                y = self._ray_lookback[h]
                t = y[0]
                r = y[1]
                i = y[2]

            elif c == 64:
                p = 63 & byte
                v = self._ray_lookback[p]
                b = v[0]
                w = v[1]
                x = v[2]
                g = ray_data[self.data_pointer]
                self.data_pointer += 1
                t = b + ((g >> 3) - 15)
                r = w + ((7 & g) - 3)
                i = x

            elif c == 128:
                R = 63 & byte
                C = self._ray_lookback[R]
                I = C[0]
                P = C[1]
                k = C[2]

                t = I + (ray_data[self.data_pointer] - 127)
                self.data_pointer += 1
                r = P
                i = k

            else:
                A = ray_data[self.data_pointer]
                self.data_pointer += 1
                F = ray_data[self.data_pointer]
                self.data_pointer += 1

                t = (A << 2) | (F >> 6)
                r = 63 & F
                i = 63 & byte

                D = (3 * (int(t / 128) | 0) + 5 * (int(r / 16) | 0) + 7 * i) & 63
                self._ray_lookback[D][0] = t
                self._ray_lookback[D][1] = r
                self._ray_lookback[D][2] = i

        return [t / 1023, r / 63, i]

    def render(self) -> Image.Image:

        # We have the output array filled with RayData objects
        # We can get the material at each pixel and use that to get the colour
        # We can then use the alignment to get the alpha value

        image = Image.new("RGBA", (self.width, self.height), (208, 230, 252))

        for i in range(len(self.output)):
            ray: Union[RayData, None] = self.output[i]
            if ray is None:
                continue

            material = ray.material
            alignment = ray.alignment

            if ray.distance == 1 and alignment == 0 and material == 0:
                continue

            colour = self.colours[material]
            image.putpixel(
                (i % self.width, self.height - 1 - (i // self.width)),
                self._convert_colour(
                    (colour[0], colour[1], colour[2], alignment)
                ),
            )

        return image

    @staticmethod
    def _convert_colour(
        colour: Tuple[float, float, float, float],
        background: Tuple[int, int, int] = (0, 0, 0),
    ) -> Tuple[int, int, int]:
        target_colour = (
            ((1 - colour[3]) * background[0]) + (colour[3] * colour[0]),
            ((1 - colour[3]) * background[1]) + (colour[3] * colour[1]),
            ((1 - colour[3]) * background[2]) + (colour[3] * colour[2]),
        )

        return (
            min(255, int(target_colour[0] * 255)),
            min(255, int(target_colour[1] * 255)),
            min(255, int(target_colour[2] * 255)),
        )
