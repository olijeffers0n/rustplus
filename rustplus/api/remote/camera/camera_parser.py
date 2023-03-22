import dataclasses
import math
from math import radians, tan
from typing import Union, Tuple, List

import numpy as np
from PIL import Image, ImageDraw

from .camera_constants import LOOKUP_CONSTANTS
from .structures import Entity


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

    @staticmethod
    def handle_entities(image: Image.Image, entities: List[Entity]) -> Image.Image:

        # Sort the entities from furthest to closest
        entities.sort(key=lambda e: e.position.z, reverse=True)

        for entity in entities:
            entity_pos = np.array([entity.position.x, entity.position.y + 0 if entity.type == 2 else 2, entity.position.z, 0])
            entity_rot = np.array([entity.rotation.x, entity.rotation.y, entity.rotation.z, 0])
            entity_size = np.array([entity.size.x, entity.size.y, entity.size.z, 0])

            # position, rotation, size of camera
            cam_pos = np.array([0, 0, 0])
            cam_rot = np.array([0, 0, 0])
            cam_fov = 65
            cam_near = 0.01
            cam_far = 1000

            # aspect ratio of the image
            aspect_ratio = image.width / image.height

            vertex_list1 = []
            vertex_list2 = []

            # The vertices of the pill
            height = entity.size.y
            x = -0.5 * entity.size.x ** entity.size.z
            while x <= 0.5 * entity.size.x ** entity.size.z:
                # Use the quadratic formula to find the y values of the top and bottom of the pill
                y1 = MathUtils.solve_quadratic(1, -2 * 0.5, x ** 2 + 0.5 ** 2 - 0.5 ** 2, False)
                y2 = MathUtils.solve_quadratic(1, -2 * (height - 0.5), x ** 2 + (height - 0.5) ** 2 - 0.5 ** 2, True)

                if y1 == 0 or y2 == 0:
                    x += 0.05
                    continue

                vertex_list1.append([x, y1 / 2, 0])
                vertex_list2.append([x, y2 / 2, 0])

                x += 0.05

            vertices = np.array(vertex_list1 + vertex_list2[::-1])

            model_matrix = np.matmul(np.matmul(MathUtils.translation_matrix(entity_pos),
                                               MathUtils.rotation_matrix(entity_rot)),
                                     MathUtils.scale_matrix(entity_size))

            view_matrix = MathUtils.camera_matrix(cam_pos, cam_rot)
            projection_matrix = MathUtils.perspective_matrix(cam_fov, aspect_ratio, cam_near, cam_far)
            mvp_matrix = np.matmul(np.matmul(projection_matrix, view_matrix), model_matrix)

            # Project the vertices onto the image plane
            pixel_coords = []
            for vertex in vertices:
                # Apply the transformation matrices to the vertex
                homog_vertex = np.append(vertex, 1)
                transformed_vertex = np.matmul(mvp_matrix, homog_vertex)

                # Normalize the transformed vertex to get 2D pixel coordinates
                x = int(transformed_vertex[0] / transformed_vertex[3] * image.width / 2 + image.width / 2)
                y = int(-transformed_vertex[1] / transformed_vertex[3] * image.height / 2 + image.height / 2)

                pixel_coords.append((x, y))

            # Draw the entity on the image
            image_draw = ImageDraw.Draw(image)
            image_draw.polygon(pixel_coords, outline="#ad0306" if entity.type == 2 else "#03ad15",
                               fill="#ad0306" if entity.type == 2 else "#03ad15")

        return image

    def render(self, entities: List[Entity]) -> Image.Image:

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

            if (ray.distance == 1 and alignment == 0 and material == 0) or material == 7:
                continue

            # TODO Switch to blobs instead of single pixels

            colour = self.colours[material]
            image.putpixel(
                (i % self.width, self.height - 1 - (i // self.width)),
                MathUtils._convert_colour(
                    (colour[0], colour[1], colour[2], alignment)
                ),
            )

        return self.handle_entities(image.resize((160 * 4, 90 * 4)), entities)


class MathUtils:

    @staticmethod
    def camera_matrix(position, rotation):
        matrix = np.matmul(MathUtils.rotation_matrix(rotation), MathUtils.translation_matrix(-position))
        return np.linalg.inv(matrix)

    @staticmethod
    def scale_matrix(size):
        return np.array([
            [size[0], 0, 0, 0],
            [0, size[1], 0, 0],
            [0, 0, size[2], 0],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def rotation_matrix(rotation):
        pitch = rotation[0]
        yaw = rotation[1]
        roll = rotation[2]

        rotation_x = np.array([
            [1, 0, 0, 0],
            [0, np.cos(pitch), -np.sin(pitch), 0],
            [0, np.sin(pitch), np.cos(pitch), 0],
            [0, 0, 0, 1]
        ])

        rotation_y = np.array([
            [np.cos(yaw), 0, np.sin(yaw), 0],
            [0, 1, 0, 0],
            [-np.sin(yaw), 0, np.cos(yaw), 0],
            [0, 0, 0, 1]
        ])

        rotation_z = np.array([
            [np.cos(roll), -np.sin(roll), 0, 0],
            [np.sin(roll), np.cos(roll), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        return np.matmul(np.matmul(rotation_x, rotation_y), rotation_z)

    @staticmethod
    def translation_matrix(position):
        return np.array([
            [1, 0, 0, position[0]],
            [0, 1, 0, position[1]],
            [0, 0, 1, -position[2]],
            [0, 0, 0, 1]
        ])

    @staticmethod
    def perspective_matrix(fov, aspect_ratio, near, far):
        f = 1 / tan(radians(fov) / 2)
        return np.array([
            [f / aspect_ratio, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
            [0, 0, -1, 0]
        ])

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

    @staticmethod
    def solve_quadratic(a: float, b: float, c: float, larger: bool) -> float:
        """
        Solves a quadratic equation but only returns either the larger or smaller root depending on the larger parameter
        """
        if a == 0:
            return -c / b

        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return 0

        if larger:
            return (-b + math.sqrt(discriminant)) / (2 * a)
        else:
            return (-b - math.sqrt(discriminant)) / (2 * a)
