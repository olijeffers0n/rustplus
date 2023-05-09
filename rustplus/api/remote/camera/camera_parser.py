import math
from importlib import resources
from math import radians, tan
import random
from typing import Union, Tuple, List, Any, Dict
import numpy as np
from scipy.spatial import ConvexHull
from PIL import Image, ImageDraw, ImageFont

from .camera_constants import LOOKUP_CONSTANTS
from .structures import Entity, Vector3

SCIENTIST_COLOUR = "#3098f2"
PLAYER_COLOUR = "#fa2828"
TREE_COLOUR = "#03ad15"
FONT_PATH = "rustplus.utils.fonts"


class Parser:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.data_pointer = 0
        self._rays = None
        self._ray_lookback = [[0 for _ in range(3)] for _ in range(64)]
        self._sample_offset = 0
        self.colours = [
            (127, 127, 127),
            (204, 178, 178),
            (76, 178, 255),
            (153, 153, 153),
            (178, 178, 178),
            (204, 153, 102),
            (255, 102, 102),
            (255, 25, 25),
        ]

        self.scale_factor = 6
        self.colour_output = None
        self.depth_output = None

        self.reset_output()

        self.entities = []
        self.last_fov = 0

    def reset_output(self) -> None:
        self.colour_output = np.full(
            (self.width * self.scale_factor, self.height * self.scale_factor, 3),
            np.array([208, 230, 252]),
        )
        self.depth_output = np.zeros(
            (self.width * self.scale_factor, self.height * self.scale_factor)
        )

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

            x = (index2 % self.width) * self.scale_factor
            y = (
                (self.width * self.height - 1 - index2) // self.width
            ) * self.scale_factor

            if (
                not (distance == 1 and alignment == 0 and material == 0)
                and material != 7
            ):
                self.colour_output[
                    x : x + self.scale_factor, y : y + self.scale_factor
                ] = MathUtils._convert_colour(
                    (
                        (colour := self.colours[material])[0],
                        colour[1],
                        colour[2],
                        alignment,
                    )
                )

            else:
                self.colour_output[
                    x : x + self.scale_factor, y : y + self.scale_factor
                ] = (208, 230, 252)
                distance = float("inf")

            self.depth_output[
                x : x + self.scale_factor, y : y + self.scale_factor
            ] = distance

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

    def handle_entities(
        self,
        image_draw: ImageDraw,
        image_data: Any,
        entities: List[Entity],
        cam_fov: float,
        depth_data: Any,
        far_plane: float,
        width: int,
        height: int,
        entity_render_distance: float,
        max_entity_amount: int,
    ) -> Any:
        image_data = np.array(image_data)

        players = [player for player in entities if player.type == 2]
        trees = [tree for tree in entities if tree.type == 1]

        tree_amount = max_entity_amount - len(players)
        target_trees = []

        if len(trees) < tree_amount:
            target_trees = trees

        else:
            if self.last_fov == cam_fov:
                for entity in self.entities:
                    # Entity is an entity id and we should try and find it in the trees list
                    for tree in trees:
                        if tree.entity_id == entity:
                            target_trees.append(tree)
                            break

            if len(target_trees) < tree_amount:
                random.shuffle(trees)
                target_trees += trees[: tree_amount - len(target_trees)]

        self.entities = [tree.entity_id for tree in target_trees]
        self.last_fov = cam_fov

        entities = players + target_trees
        entities.sort(key=lambda e: e.position.z, reverse=True)

        # position, rotation, size of camera
        cam_pos = np.array([0, 0, 0])
        cam_rot = np.array([0, 0, 0])
        cam_near = 0.01
        cam_far = 1000

        # aspect ratio of the image
        aspect_ratio = width / height

        view_matrix = MathUtils.camera_matrix(cam_pos, cam_rot)
        projection_matrix = MathUtils.perspective_matrix(
            cam_fov, aspect_ratio, cam_near, cam_far
        )

        text = set()

        for entity in entities:
            if entity.position.z > entity_render_distance and entity.type == 1:
                continue

            Parser.handle_entity(
                entity,
                image_draw,
                cam_pos,
                projection_matrix,
                view_matrix,
                image_data,
                depth_data,
                width,
                height,
                cam_near,
                cam_far,
                far_plane,
                cam_fov,
                aspect_ratio,
                text,
            )

        return text, image_data

    @staticmethod
    def handle_entity(
        entity,
        image_draw,
        cam_pos,
        projection_matrix,
        view_matrix,
        image_data,
        depth_data,
        width,
        height,
        cam_near,
        cam_far,
        far_plane,
        cam_fov,
        aspect_ratio,
        text,
    ) -> None:
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

        vertices = (
            MathUtils.get_player_vertices(entity.size)
            if entity.type == 2
            else MathUtils.get_tree_vertices(entity.size)
        )
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

        mvp_matrix = np.matmul(np.matmul(projection_matrix, view_matrix), model_matrix)

        # Calculate the transformed vertices
        transformed_vertices = np.matmul(mvp_matrix, vertices.T).T

        # Normalize the transformed vertices and calculate pixel coordinates
        pixel_coords = tuple(
            map(
                tuple,
                np.round(
                    (
                        (transformed_vertices[:, :2] / transformed_vertices[:, 3, None])
                        * np.array([width, -height])
                        / 2
                    )
                    + np.array([width, height]) / 2
                ).astype(np.int32),
            )
        )

        # Remove the last element of the pixel_coords array
        name_place = pixel_coords[-1]
        pixel_coords = pixel_coords[:-1]

        colour = (
            (PLAYER_COLOUR if not entity.name.isdigit() else SCIENTIST_COLOUR)
            if entity.type == 2
            else MathUtils.get_slightly_random_colour(TREE_COLOUR, entity.position)
        )

        MathUtils.set_polygon_with_depth(
            MathUtils.gift_wrap_algorithm(pixel_coords),
            image_data,
            depth_data,
            math.sqrt(
                entity.position.x**2 + entity.position.y**2 + entity.position.z**2
            ),
            colour,
            width,
            height,
            far_plane,
        )

        if entity.type == 2:
            font_size = max(
                MathUtils.get_font_size(
                    entity.position.z, 250, cam_near, cam_far, aspect_ratio, cam_fov
                ),
                1,
            )
            # The font size should be proportional to the size of the entity as it gets further away
            with resources.path(FONT_PATH, "PermanentMarker.ttf") as path:
                font = ImageFont.truetype(str(path), font_size)
            size = image_draw.textsize(entity.name, font=font)

            name_place1 = (
                name_place[0] - size[0] // 2,
                name_place[1] - size[1] // 2,
            )
            text.add((name_place1, entity.name, font))

    def render(
        self,
        render_entities: bool,
        entities: List[Entity],
        fov: float,
        far_plane: float,
        entity_render_distance: float,
        max_entity_amount: int,
    ) -> Image.Image:
        # We have the output array filled with RayData objects
        # We can get the material at each pixel and use that to get the colour
        # We can then use the alignment to get the alpha value

        image = Image.new(
            "RGBA",
            (self.width * self.scale_factor, self.height * self.scale_factor),
            (0, 0, 0),
        )
        draw = ImageDraw.Draw(image)

        if not render_entities:
            entities = []

        text, image_data = self.handle_entities(
            draw,
            self.colour_output,
            entities,
            fov,
            self.depth_output,
            far_plane,
            image.size[0],
            image.size[1],
            entity_render_distance,
            max_entity_amount,
        )
        image_data = image_data.astype("uint8")

        # transpose the array
        transposed_arr = image_data.transpose((1, 0, 2))

        # This doesn't work:
        image = Image.fromarray(transposed_arr, "RGB")

        draw = ImageDraw.Draw(image)
        for pos, name, font in text:
            draw.text(pos, name, font=font, fill="black")

        return image


class MathUtils:
    VERTEX_CACHE: Dict[Vector3, np.ndarray] = {}
    COLOUR_CACHE: Dict[Tuple[float, float, float, float], Tuple[int, int, int]] = {}

    @staticmethod
    def camera_matrix(position, rotation) -> np.ndarray:
        matrix = np.matmul(
            MathUtils.rotation_matrix(rotation), MathUtils.translation_matrix(-position)
        )
        return np.linalg.inv(matrix)

    @staticmethod
    def scale_matrix(size) -> np.ndarray:
        return np.array(
            [[size[0], 0, 0, 0], [0, size[1], 0, 0], [0, 0, size[2], 0], [0, 0, 0, 1]]
        )

    @staticmethod
    def rotation_matrix(rotation) -> np.ndarray:
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
    def translation_matrix(position) -> np.ndarray:
        return np.array(
            [
                [1, 0, 0, position[0]],
                [0, 1, 0, position[1]],
                [0, 0, 1, -position[2]],
                [0, 0, 0, 1],
            ]
        )

    @staticmethod
    def perspective_matrix(fov, aspect_ratio, near, far) -> np.ndarray:
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
    def gift_wrap_algorithm(vertices) -> List[Tuple[float, float]]:
        data = np.array(vertices)

        # Check that the min and max are not the same
        if (
            data.max(axis=0)[0] == data.min(axis=0)[0]
            or data.max(axis=0)[1] == data.min(axis=0)[1]
        ):
            return []

        # use convex hull algorithm to find the convex hull from scipy
        hull = ConvexHull(data)
        # get the vertices of the convex hull
        return [tuple(data[i]) for i in hull.vertices]

    @classmethod
    def _convert_colour(
        cls,
        colour: Tuple[float, float, float, float],
    ) -> Tuple[int, int, int]:
        if colour in cls.COLOUR_CACHE:
            return cls.COLOUR_CACHE[colour]

        colour = (
            int(colour[3] * colour[0]),
            int(colour[3] * colour[1]),
            int(colour[3] * colour[2]),
        )

        cls.COLOUR_CACHE[colour] = colour
        return colour

    @staticmethod
    def solve_quadratic(a: float, b: float, c: float, larger: bool) -> float:
        """
        Solves a quadratic equation but only returns either the larger or smaller root depending on the larger parameter
        """
        if a == 0:
            return -c / b

        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            return 0

        if larger:
            return (-b + math.sqrt(discriminant)) / (2 * a)
        else:
            return (-b - math.sqrt(discriminant)) / (2 * a)

    @classmethod
    def get_tree_vertices(cls, size) -> np.ndarray:
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
    def get_player_vertices(cls, size) -> np.ndarray:
        if size in cls.VERTEX_CACHE:
            return cls.VERTEX_CACHE[size]

        number_of_segments = 14
        segment_angle = (2 * math.pi) / number_of_segments

        vertex_list1 = []
        vertex_list2 = []

        # The vertices of the pill
        height = size.y + 0.3
        width = 0.5 * size.x**size.z
        increment = 0.1

        x = 0
        while x <= width:
            for offset in range(-1, 2, 2):
                x_value = x * offset

                # Use the quadratic formula to find the y values of the top and bottom of the pill
                y1 = MathUtils.solve_quadratic(
                    1, -2 * 0.5, x_value**2 + 0.5**2 - 0.5**2, False
                )
                y2 = MathUtils.solve_quadratic(
                    1,
                    -2 * (height - 0.5),
                    x_value**2 + (height - 0.5) ** 2 - 0.5**2,
                    True,
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
    def get_slightly_random_colour(colour: str, entity_pos: Vector3) -> str:
        """
        Returns a slightly randomised version of the colour passed in
        Must be the same colour for the same entity id
        """

        r, g, b = int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)

        # Create an algorithm will slightly vary the colour based on the distance from the origin
        # This is to make it easier to distinguish between entities

        distance_squared = entity_pos.x**2 + entity_pos.y**2 + 2 * entity_pos.z**2

        r += int(distance_squared * 0.0003) % 10
        g += int(distance_squared * 0.0003) % 10
        b += int(distance_squared * 0.0003) % 10

        return f"#{r}{g}{b}"

    @staticmethod
    def get_font_size(distance, font_size, near, far, aspect_ratio, fov) -> int:
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
        projection_matrix = np.array(
            [
                [f / aspect_ratio, 0.0, 0.0, 0.0],
                [0.0, f, 0.0, 0.0],
                [
                    0.0,
                    0.0,
                    (far + near) / (near - far),
                    2.0 * far * near / (near - far),
                ],
                [0.0, 0.0, -1.0, 0.0],
            ]
        )

        # Define the modelview matrix based on the distance from the screen
        modelview_matrix = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, -distance],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        # Calculate the projection of the text onto the screen
        text_projection = projection_matrix @ modelview_matrix
        projected_text = np.array([font_size, 0, 0, 1]) @ text_projection
        projected_text /= projected_text[3]
        projected_size = projected_text[0]

        return int(projected_size)

    @staticmethod
    def set_polygon_with_depth(
        vertices, image_data, depth_data, depth, colour, width, height, far_plane
    ) -> None:
        if len(vertices) <= 1:
            return

        colour = MathUtils.convert_colour_to_tuple(colour)

        pixels = MathUtils.get_vertices_in_polygon(vertices, width, height)

        if len(pixels) == 0:
            return

        pixels = pixels[
            (pixels[:, 0] >= 0)
            & (pixels[:, 0] < depth_data.shape[0])
            & (pixels[:, 1] >= 0)
            & (pixels[:, 1] < depth_data.shape[1])
        ]

        # Get all pixels where depth_data[x, y] * far_plane > depth is true
        pixels = pixels[
            depth_data[pixels[:, 0], pixels[:, 1]] * far_plane > depth - 0.5
        ]

        # Set the pixels to the colour
        image_data[pixels[:, 0], pixels[:, 1]] = colour

    @staticmethod
    def convert_colour_to_tuple(colour) -> Tuple[int, int, int]:
        """
        Converts a colour in the form
        #RRGGBB
        to a tuple of the form
        (R, G, B)
        """
        return int(colour[1:3], 16), int(colour[3:5], 16), int(colour[5:7], 16)

    @staticmethod
    def get_vertices_in_polygon(vertices, width, height) -> np.ndarray:
        """
        Takes a list of vertices and returns the vertices that are inside the polygon defined by the vertices
        vertices is a list of vertices in the form [x, y]
        width and height specify the size of the bounding box around the polygon
        """
        # Create an image mask for the polygon
        mask = Image.new("L", (width, height), 0)
        ImageDraw.Draw(mask).polygon(vertices, outline=1, fill=1)

        # Convert the mask to a NumPy array
        mask_arr = np.array(mask)

        # Find the indices of the non-zero values in the mask array
        y, x = np.nonzero(mask_arr)

        # Return the vertices that correspond to the non-zero indices
        return np.array(list(zip(x, y)))
