import dataclasses
import math
import time
from importlib import resources
from math import radians, tan
import random
from typing import Union, Tuple, List

import cv2
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw, ImageFont

from .camera_constants import LOOKUP_CONSTANTS
from .structures import Entity

SCIENTIST_COLOUR = "#3098f2"
PLAYER_COLOUR = "#fa2828"
TREE_COLOUR = "#03ad15"
FONT_PATH = "rustplus.utils.fonts"


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
            (int(0.5 * 255), int(0.5 * 255), int(0.5 * 255)),
            (int(0.8 * 255), int(0.7 * 255), int(0.7 * 255)),
            (int(0.3 * 255), int(0.7 * 255), int(1 * 255)),
            (int(0.6 * 255), int(0.6 * 255), int(0.6 * 255)),
            (int(0.7 * 255), int(0.7 * 255), int(0.7 * 255)),
            (int(0.8 * 255), int(0.6 * 255), int(0.4 * 255)),
            (int(1 * 255), int(0.4 * 255), int(0.4 * 255)),
            (int(1 * 255), int(0.1 * 255), int(0.1 * 255)),
        ]

        self.output = [None for _ in range(self.width * self.height)]

    def handle_camera_ray_data(self, data) -> None:

        if data is None:
            return

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
    def handle_entities(image: Image.Image, entities: List[Entity], cam_fov: float, depth_data) -> Image.Image:

        # Sort the entities from furthest to closest
        entities.sort(key=lambda e: e.position.z, reverse=True)

        # position, rotation, size of camera
        cam_pos = np.array([0, 0, 0])
        cam_rot = np.array([0, 0, 0])
        cam_near = 0.01
        cam_far = 1000

        # aspect ratio of the image
        aspect_ratio = image.width / image.height

        view_matrix = MathUtils.camera_matrix(cam_pos, cam_rot)
        projection_matrix = MathUtils.perspective_matrix(
            cam_fov, aspect_ratio, cam_near, cam_far
        )

        image_data = list(image.getdata())
        text = set()

        for entity in entities:

            entity.size.x = min(entity.size.x, 5)
            entity.size.y = min(entity.size.y, 5)
            entity.size.z = min(entity.size.z, 5)

            entity_pos = np.array(
                [
                    entity.position.x,
                    entity.position.y + (2 if entity.type == 1 else 0),
                    entity.position.z,
                    0,
                ]
            )
            entity_rot = np.array(
                [entity.rotation.x, entity.rotation.y, entity.rotation.z, 0]
            )
            entity_size = np.array([entity.size.x, entity.size.y, entity.size.z, 0])

            vertices = MathUtils.get_player_vertices(entity.size) if entity.type == 2 else MathUtils.get_tree_vertices(entity.size)
            # Add the position for the name tag to the vertices
            vertices = np.append(vertices, [np.array([0, 1.3, 0, 1])], axis=0)

            model_matrix = np.matmul(
                np.matmul(
                    MathUtils.translation_matrix(entity_pos),
                    MathUtils.rotation_matrix(entity_rot),
                ),
                MathUtils.scale_matrix(entity_size),
            )

            # Add rotation to face the camera
            cam_direction = cam_pos - entity_pos[:3]
            cam_direction[1] = 0
            cam_angle = np.arctan2(cam_direction[2], cam_direction[0])
            cam_rotation_matrix = MathUtils.rotation_matrix([0, cam_angle, 0, 0])
            model_matrix = np.matmul(model_matrix, cam_rotation_matrix)

            mvp_matrix = np.matmul(
                np.matmul(projection_matrix, view_matrix), model_matrix
            )

            # Calculate the transformed vertices
            transformed_vertices = np.matmul(mvp_matrix, vertices.T).T

            # Normalize the transformed vertices and calculate pixel coordinates
            pixel_coords = tuple(
                map(
                    tuple,
                    np.round(
                        (
                                (
                                        transformed_vertices[:, :2]
                                        / transformed_vertices[:, 3, None]
                                )
                                * np.array([image.width, -image.height])
                                / 2
                        )
                        + np.array([image.width, image.height]) / 2
                    ).astype(np.int32),
                )
            )

            # Remove the last element of the pixel_coords array
            name_place = pixel_coords[-1]
            pixel_coords = pixel_coords[:-1]

            colour = (
                (PLAYER_COLOUR if not entity.name.isdigit() else SCIENTIST_COLOUR)
                if entity.type == 2
                else MathUtils.get_slightly_random_colour(TREE_COLOUR, entity.entity_id)
            )

            MathUtils.set_polygon_with_depth(
                MathUtils.gift_wrap_algorithm(pixel_coords), image_data, depth_data,
                math.sqrt(entity.position.x ** 2 + entity.position.y ** 2 + entity.position.z ** 2), colour, *image.size)

            if entity.type == 2:
                font_size = max(MathUtils.get_font_size(entity.position.z, 250, cam_near, cam_far, aspect_ratio, cam_fov), 1)
                # The font size should be proportional to the size of the entity as it gets further away
                with resources.path(FONT_PATH, "PermanentMarker.ttf") as path:
                    font = ImageFont.truetype(str(path), font_size)
                size = ImageDraw.Draw(image).textsize(entity.name, font=font)

                name_place1 = (name_place[0] - size[0] // 2, name_place[1] - size[1] // 2)
                text.add((name_place1, entity.name, font))

        image.putdata(image_data)
        draw = ImageDraw.Draw(image)
        for pos, name, font in text:
            draw.text(pos, name, font=font, fill="black")

        return image

    def render(self, entities: List[Entity], fov: float, far_plane) -> Image.Image:

        # We have the output array filled with RayData objects
        # We can get the material at each pixel and use that to get the colour
        # We can then use the alignment to get the alpha value

        image = Image.new("RGBA", (self.width * 4, self.height * 4), (208, 230, 252))
        depth_data = np.zeros((self.width * 4, self.height * 4))
        draw = ImageDraw.Draw(image)

        for i in range(len(self.output)):
            ray: Union[RayData, None] = self.output[i]
            if ray is None:
                continue

            material = ray.material
            alignment = ray.alignment

            if not ((ray.distance == 1 and alignment == 0 and material == 0) or material == 7):
                colour = self.colours[material]
                # Set a 4x4 pixel area to the colour
                draw.rectangle(
                    (
                        (i % self.width) * 4,
                        (self.height - 1 - (i // self.width)) * 4,
                        (i % self.width) * 4 + 4,
                        (self.height - 1 - (i // self.width)) * 4 + 4,
                    ),
                    fill=MathUtils._convert_colour((colour[0], colour[1], colour[2], alignment)),
                )
                distance = ray.distance * far_plane

            else:
                distance = float("inf")

            # Set the 4x4 pixel area to the depth value
            depth_data[
            (i % self.width) * 4: (i % self.width) * 4 + 4,
            (self.height - 1 - (i // self.width)) * 4: (self.height - 1 - (i // self.width))
                                                       * 4
                                                       + 4,
            ] = distance

        im = self.handle_entities(image, entities, fov, depth_data)
        return im


class MathUtils:
    VERTEX_CACHE = {}

    @staticmethod
    def camera_matrix(position, rotation):
        matrix = np.matmul(
            MathUtils.rotation_matrix(rotation), MathUtils.translation_matrix(-position)
        )
        return np.linalg.inv(matrix)

    @staticmethod
    def scale_matrix(size):
        return np.array(
            [[size[0], 0, 0, 0], [0, size[1], 0, 0], [0, 0, size[2], 0], [0, 0, 0, 1]]
        )

    @staticmethod
    def rotation_matrix(rotation):
        pitch = rotation[0]
        yaw = rotation[1]
        roll = rotation[2]

        rotation_x = np.array(
            [
                [1, 0, 0, 0],
                [0, np.cos(pitch), -np.sin(pitch), 0],
                [0, np.sin(pitch), np.cos(pitch), 0],
                [0, 0, 0, 1],
            ]
        )

        rotation_y = np.array(
            [
                [np.cos(yaw), 0, np.sin(yaw), 0],
                [0, 1, 0, 0],
                [-np.sin(yaw), 0, np.cos(yaw), 0],
                [0, 0, 0, 1],
            ]
        )

        rotation_z = np.array(
            [
                [np.cos(roll), -np.sin(roll), 0, 0],
                [np.sin(roll), np.cos(roll), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )

        return np.matmul(np.matmul(rotation_x, rotation_y), rotation_z)

    @staticmethod
    def translation_matrix(position):
        return np.array(
            [
                [1, 0, 0, position[0]],
                [0, 1, 0, position[1]],
                [0, 0, 1, -position[2]],
                [0, 0, 0, 1],
            ]
        )

    @staticmethod
    def perspective_matrix(fov, aspect_ratio, near, far):
        f = 1 / tan(radians(fov) / 2)
        return np.array(
            [
                [f / aspect_ratio, 0, 0, 0],
                [0, f, 0, 0],
                [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
                [0, 0, -1, 0],
            ]
        )

    @staticmethod
    def gift_wrap_algorithm(vertices):
        data = np.array(vertices)
        # use convex hull algorithm to find the convex hull from scipy
        hull = ConvexHull(data)
        # get the vertices of the convex hull
        return [tuple(data[i]) for i in hull.vertices]

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
            min(255, int(target_colour[0])),
            min(255, int(target_colour[1])),
            min(255, int(target_colour[2])),
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

    @classmethod
    def get_tree_vertices(cls, size):

        if size in cls.VERTEX_CACHE:
            return cls.VERTEX_CACHE[size]

        number_of_segments = 14
        segment_angle = (2 * math.pi) / number_of_segments

        vertex_list = []

        for x_value in [size.y / 8, -size.y / 8]:

            for i in range(number_of_segments):
                angle = segment_angle * i

                z = math.sin(angle) * abs(x_value)
                new_x = math.cos(angle) * abs(x_value)

                vertex_list.append([new_x, 0, z, 1])

        vertex_list.append([0, size.y / 2, 0, 1])

        vertices = np.array(vertex_list)
        cls.VERTEX_CACHE[size] = vertices
        return vertices

    @classmethod
    def get_player_vertices(cls, size):

        if size in cls.VERTEX_CACHE:
            return cls.VERTEX_CACHE[size]

        number_of_segments = 14
        segment_angle = (2 * math.pi) / number_of_segments

        vertex_list1 = []
        vertex_list2 = []

        # The vertices of the pill
        height = size.y + 0.3
        width = 0.5 * size.x ** size.z
        increment = 0.1

        x = 0
        while x <= width:

            for offset in range(-1, 2, 2):

                x_value = x * offset

                # Use the quadratic formula to find the y values of the top and bottom of the pill
                y1 = MathUtils.solve_quadratic(
                    1, -2 * 0.5, x_value ** 2 + 0.5 ** 2 - 0.5 ** 2, False
                )
                y2 = MathUtils.solve_quadratic(
                    1, -2 * (height - 0.5), x_value ** 2 + (height - 0.5) ** 2 - 0.5 ** 2, True
                )

                if y1 == 0 or y2 == 0:
                    x_value += increment
                    continue

                for i in range(number_of_segments):
                    angle = segment_angle * i

                    z = math.sin(angle) * abs(x_value)
                    new_x = math.cos(angle) * abs(x_value)

                    vertex_list1.append([new_x, y1 / 2, z, 1])
                    vertex_list2.append([new_x, y2 / 2, z, 1])

            # when x is greater than 4/5 of the width, decrease the increment
            if x > 0.8 * width:
                increment = 0.001

            x += increment

        vertices = np.array(vertex_list1 + vertex_list2[::-1])
        cls.VERTEX_CACHE[size] = vertices
        return vertices

    @staticmethod
    def get_slightly_random_colour(colour: str, entity_id: int) -> str:
        """
        Returns a slightly randomised version of the colour passed in
        Must be the same colour for the same entity id
        """

        random.seed(entity_id)
        r, g, b = int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)
        r = int(r * (1 + random.uniform(-0.1, 0.1)))
        g = int(g * (1 + random.uniform(-0.1, 0.1)))
        b = int(b * (1 + random.uniform(-0.1, 0.1)))
        return f"#{r}{g}{b}"

    @staticmethod
    def get_font_size(distance, font_size, near, far, aspect_ratio, fov):
        """
        Given the distance from the screen, uses perspective projection matrix to return a font size for some text.

        Args:
        distance (float): Distance from the screen in meters
        text (str): Text to calculate font size for
        font_size (int): Base font size in pixels
        screen_width (int): Width of the screen in pixels
        screen_height (int): Height of the screen in pixels

        Returns:
        int: Font size in pixels
        """
        f = 1.0 / np.tan(np.deg2rad(fov / 2.0))
        projection_matrix = np.array([
            [f / aspect_ratio, 0.0, 0.0, 0.0],
            [0.0, f, 0.0, 0.0],
            [0.0, 0.0, (far + near) / (near - far), 2.0 * far * near / (near - far)],
            [0.0, 0.0, -1.0, 0.0]
        ])

        # Define the modelview matrix based on the distance from the screen
        modelview_matrix = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, -distance],
            [0.0, 0.0, 0.0, 1.0]
        ])

        # Calculate the projection of the text onto the screen
        text_projection = projection_matrix @ modelview_matrix
        projected_text = np.array([font_size, 0, 0, 1]) @ text_projection
        projected_text /= projected_text[3]
        projected_size = projected_text[0]

        return int(projected_size)

    @staticmethod
    def set_polygon_with_depth(vertices, image_data, depth_data, depth, colour, width, height):

        colour = MathUtils.convert_colour_to_tuple(colour)

        for pixel in MathUtils.get_vertices_in_polygon(vertices, width, height):
            x, y = pixel
            # If the pixel is closer to the camera than the current depth, set the pixel to the colour
            # depth data is a numpy array
            if x < 0 or x >= depth_data.shape[0] or y < 0 or y >= depth_data.shape[1]:
                continue

            if depth_data[x, y] > depth:
                image_data[x + y * width] = colour
                depth_data[x, y] = depth

    @staticmethod
    def convert_colour_to_tuple(colour):
        """
        Converts a colour in the form
        #RRGGBB
        to a tuple of the form
        (R, G, B)
        """
        return int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)

    @staticmethod
    def get_vertices_in_polygon(vertices, width, height):
        """
        Takes a list of vertices and returns the vertices that are inside the polygon defined by the vertices
        vertices is a list of vertices in the form [x, y]
        width and height specify the size of the bounding box around the polygon
        """
        # Create an image mask for the polygon
        mask = Image.new('L', (width, height), 0)
        ImageDraw.Draw(mask).polygon(vertices, outline=1, fill=1)

        # Convert the mask to a NumPy array
        mask_arr = np.array(mask)

        # Find the indices of the non-zero values in the mask array
        y, x = np.nonzero(mask_arr)

        # Return the vertices that correspond to the non-zero indices
        return list(zip(x, y))
