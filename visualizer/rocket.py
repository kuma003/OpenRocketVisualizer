"""
rocket.py

Notes:
    - Coordinate origin is bottom of the rocket.
    - The unit is meter (but normalized and adjusted when drawing).
"""

import glob
import jpype
import numpy as np
import os
import tomllib
from pathlib import Path

import matplotlib.pyplot as plt

import numpy as np
import orhelper
import pygame as pg
import requests
from orhelper import FlightDataType, OrLogLevel

# from orhelper._orhelper import or_logger
from jpype import java

# java.util.logging.Logger
# .getLogger("ch").setLevel(java.util.logging.Level.OFF)

# silent loggers' console message ?
# or_logger.setLevel(getattr(jpype.JPackage("ch").qos.logback.classic.Level, "OFF"))


class Rocket:
    NOSE_CONE_DETAIL = 10  # number of points to draw the nose cone

    FLIGHT_DATA = [
        FlightDataType.TYPE_TIME,
        FlightDataType.TYPE_ALTITUDE,
        FlightDataType.TYPE_POSITION_X,
        FlightDataType.TYPE_POSITION_Y,
        FlightDataType.TYPE_POSITION_XY,
        FlightDataType.TYPE_ORIENTATION_THETA,
        FlightDataType.TYPE_ORIENTATION_PHI,
        FlightDataType.TYPE_AOA,
    ]

    def __init__(self, file_path: os.PathLike):
        """
        Initialize the Rocket object.
        Args:
            file_path (os.PathLike): path to the ork file.
        """

        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = str(file_path)

        # find or download jar file for OpenRocket
        self.__jar_path = os.environ.get("CLASSPATH")

        if self.__jar_path is None or not Path(self.__jar_path).exists():
            self.__jar_path = glob.glob("*.jar")

            if self.__jar_path:
                self.__jar_path = self.__jar_path[0]
            else:
                print("OpenRocket jar file not found. Downloading...")
                with open("settings.toml", "rb") as f:
                    settings = tomllib.load(f)
                    url = settings["openrocket"]["url"]
                    response = requests.get(url)
                    self.__jar_path = url[url.rfind("/") + 1 :]
                    with open(self.__jar_path, "wb") as f:
                        f.write(response.content)
                print("Done.")
                self.__jar_path = os.environ.get("CLASSPATH")

        self.flight_data: dict[FlightDataType, float] = None
        self.nose: Nose = None
        self.bodys: list[Body] = []

        self.drawing_positon = [0.5, 0.5]  # position of the rocket(percentage)
        self.drawing_size = 0.8  # size of the rocket vs. window height(percentage)

    def run_simulation(self):
        """
        Run the simulation.
        """
        with orhelper.OpenRocketInstance(self.__jar_path) as instance:
            orh = orhelper.Helper(instance)
            doc = orh.load_doc(self.file_path)

            try:
                sim = doc.getSimulation(0)
            except:
                print("Error: Simulation Data is not available.")
                print(
                    "INFO: Please check the simulation data is attached or\n the OpenRocket version is the latest."
                )

            opts = sim.getOptions()
            rocket = sim.getRocket()
            # set simulation specifications from settings.toml
            with open("settings.toml", "rb") as f:
                settings = tomllib.load(f)
                opts.setLaunchRodAngle(
                    np.radians(90 - settings["simulation"]["launchRod"]["angle"])
                )  # convert to radians
                opts.setLaunchRodLength(
                    settings["simulation"]["launchRod"]["length"]
                )  # must be in meters
                opts.setWindSpeedAverage(settings["simulation"]["wind"]["speed"])
                opts.setWindSpeedDeviation(settings["simulation"]["wind"]["deviation"])
                opts.setWindTurbulenceIntensity(
                    settings["simulation"]["wind"]["turbulenceIntensity"]
                )
                # opts.setWindDirection(
                #     np.radians(settings["simulation"]["wind"]["direction"])
                # ) # omit

            orh.run_simulation(sim)  # run simulation
            sim_data = sim.getSimulatedData()
            print("launch clear vel: ", sim_data.getLaunchRodVelocity())
            print("max altitude: ", sim_data.getMaxAltitude())
            print("max velocity: ", sim_data.getMaxVelocity())
            print("flight time: ", sim_data.getFlightTime())

            self.flight_data = orh.get_timeseries(
                sim, self.FLIGHT_DATA
            )  # get timeseries data

            ### get rocket structure ###

            self.length = rocket.getLength()  # total length of the rocket

            self.dry_mass = rocket.getMass()  # mass without propellant

            sustainer = rocket.getChild(0)

            if sustainer.getChildCount() == 0:
                raise ValueError("No sustainer stage found.")

            # only available for the single rocket, not for the multi-stage rocket
            sustainer = rocket.getChild(0)

            # in the most of the cases, the first child is the nose cone
            nose = sustainer.getChild(0)
            nose_cone_length = nose.getLength()
            radius = [
                nose.getRadius(nose_cone_length / self.NOSE_CONE_DETAIL * i)
                for i in range(0, self.NOSE_CONE_DETAIL + 1)
            ]  # shape of the nose cone
            self.nose = Nose(radius, nose_cone_length, self.length)

            # verify all of the body tubes
            for i in range(1, sustainer.getChildCount()):
                for coord in sustainer.getChild(i).getLocations():
                    print(coord)
                body = sustainer.getChild(i)
                body_positon = np.array([body.getPosition().x, body.getPosition().y])
                self.bodys.append(
                    Body(
                        body_positon[0],  # only need x-axis position
                        body.getLength(),
                        body.getOuterRadius(),
                        self.length,
                    )
                )
                for component in body.getChildren():
                    if not "FinSet" in type(component).__name__:  # not a fin
                        continue

                    # start point of the fin shape
                    start_point = component.getLocations()[0]
                    self.bodys[-1].fins.append(
                        Fin(
                            body_positon,
                            np.array([start_point.x, start_point.y]),
                            [
                                np.array([point.x, point.y])
                                for point in component.getFinPoints()
                            ],
                            component.getFinCount(),
                            self.length,
                        )
                    )

    def update(self, pos: np.ndarray, roll: float, pitch: float, yaw: float):
        """
        Update the rocket for drawing.

        Args:
            pos (np.ndarray): position of the center of the whole rocket in percentage relative to the window size.
            roll (float): roll angle(degrees).
            pitch (float): pitch angle(degrees).
            yaw (float): yaw angle(degrees).
        """
        roll = np.radians(roll)
        pitch = np.radians(pitch)
        yaw = np.radians(yaw)

        window_size = pg.display.get_window_size()
        scale_factor = (
            window_size[1] / self.length * self.drawing_size * np.cos(yaw)
        )  # scale factor

        rotation_matrix = np.array(
            [
                [np.cos(pitch), -np.sin(pitch)],
                [np.sin(pitch), np.cos(pitch)],
            ]
        )
        pos = np.array(window_size) * pos  # convert to pixcel
        self.nose.update(pos, scale_factor, rotation_matrix)
        for body in self.bodys:
            # body.update()
            body.update(pos, scale_factor, rotation_matrix, roll)

    def draw(self, screen: pg.surface):
        """
        Draw the rocket on the screen.

        Args:
            screen (pg.surface): screen to draw the rocket.
        """
        # Returns:
        #     pg.Rect: bounding box of the rocket.

        self.nose.draw(screen)
        for body in self.bodys:
            body.draw(screen)

        # x_points = [point[0] for body in self.bodys for point in body.polygons] + [
        #     point[0] for point in self.nose.polygon
        # ]
        # y_points = [point[1] for body in self.bodys for point in body.polygons] + [
        #     point[1] for point in self.nose.polygon
        # ]

        # x_min = min(x_points)
        # x_max = max(x_points)
        # y_min = min(y_points)
        # y_max = max(y_points)

        # return pg.Rect(x_min, y_min, x_max - x_min, y_max - y_min)


class Nose:
    def __init__(
        self, radius_arr: list[float], nose_length: float, total_length: float
    ):
        """
        Initialize the Nose object.
        Args:
            radius_arr (list[float]): list of radius of the nose cone.
            nose_length (float): length of the nose cone.
            total_length (float): total length of the rocket.
        """
        self.total_length = total_length
        half_length = total_length / 2
        axial_points = np.linspace(0, nose_length, len(radius_arr))[1:] - half_length
        radius_arr = radius_arr[1:]  # exclude the first point

        self.nose_points = (
            [np.array([0, -half_length])]
            + [
                np.array([radius, axial_point])
                for radius, axial_point in zip(radius_arr, axial_points)
            ]
            + [
                np.array([-radius, axial_point])
                for radius, axial_point in zip(radius_arr[::-1], axial_points[::-1])
            ]
        )

        self.polygon = []  # polygon to draw the nose cone

    def update(self, pos: float, scale_factor: float, rotateion_matrix: np.ndarray):
        """
        Update the nose cone for drawing.

        Args:
            pos (float): position of the center of the whole rocket in pixcel.
            scale_factor (float): scale factor as the ratio of the window height to the total length of the rocket.
            rotateion_matrix (np.ndarray): rotation matrix for the nose cone. must be 2x2 matrix.
        """
        points = [np.dot(rotateion_matrix, point) for point in self.nose_points]

        self.polygon = [point * scale_factor + pos for point in points]
        self.polygon = [point for point in self.polygon]

    def draw(self, screen: pg.surface):
        """
        Draw the nose cone on the screen.

        Args:
            screen (pg.surface): screen to draw the nose cone.
        """
        pg.draw.polygon(screen, pg.Color("white"), self.polygon)
        pg.draw.polygon(screen, pg.Color("black"), self.polygon, width=1)


class Body:
    def __init__(
        self, position: np.ndarray, length: float, radius: float, total_length: float
    ):
        """
        Initialize the Body object.

        Args:
            position (np.ndarray): x-axis position of the tip of the body tube in meter.
            length (float): length of the body tube in meter.
            radius (float): radius of the body tube in meter.
            total_length (float): total length of the rocket.
        """
        print("position: ", position)
        print("length: ", length)
        half_length = total_length / 2
        self.points = [
            np.array([radius, position - half_length]),
            np.array([radius, position + length - half_length]),
            np.array([-radius, position + length - half_length]),
            np.array([-radius, position - half_length]),
        ]
        self.fins: list[Fin] = []
        self.polygons = []

    def update(
        self,
        pos: np.ndarray,
        scale_factor: float,
        rotation_matrix: np.ndarray,
        beta: float,
    ):
        """
        Update the body tube for drawing.

        Args:
            pos (np.ndarray): position of the center of the whole rocket in pixcel.
            scale_factor (float): scale factor as the ratio of the window height to the total length of the rocket.
            rotateion_matrix (np.ndarray): rotation matrix for the body tube. must be 2x2 matrix.
            beta (float): roll angle for the body tube(degrees).
        """
        points = [np.dot(rotation_matrix, point) for point in self.points]

        self.polygons = [point * scale_factor + pos for point in points]

        for fin in self.fins:
            fin.update(pos, scale_factor, rotation_matrix, beta)

    def draw(self, screen: pg.surface):
        """
        Draw the body tube on the screen.

        Args:
            screen (pg.surface): screen to draw the body tube.
        """
        for fin in self.fins:
            fin.draw_backward(screen)
        pg.draw.polygon(screen, pg.Color("white"), self.polygons)
        pg.draw.polygon(screen, pg.Color("black"), self.polygons, width=1)
        for fin in self.fins:
            fin.draw_forward(screen)


class Fin:
    def __init__(
        self,
        parents_position: np.ndarray,
        start_point: np.ndarray,
        shape: list[np.ndarray],
        n_fins: int,
        total_length: float,
    ):
        """
        Initialize the Fin object.
        Args:
            parents_position (np.ndarray): position of the parent body tube.
            start_point (np.ndarray): start point(x, y)[m].
            points (list[np.ndarray]): list of fin shape points(x, y)[m] (inherit OpenRocket original coordinate).
            n_fins (int): number of fins.
            total_length (float): total length of the rocket
        """
        start_point = start_point[::-1]  # convert as longitudinal axis is y-axis
        parents_position = parents_position[::-1]
        offset = start_point - np.array([0, total_length / 2])
        print("offset: ", offset)
        print("start_point: ", start_point)
        print("parents_position: ", parents_position)

        self.shape = shape
        self.n_fin = n_fins

        self.points = [point[::-1] + offset for point in shape]
        print(self.points)

        self.polygons = []
        self.z_order = []

    def update(
        self,
        pos: np.ndarray,
        scale_factor: float,
        rotation_matrix: np.ndarray,
        beta: float,
    ):
        """
        Update the fin for drawing.

        Args:
            pos (np.ndarray): position of the center of the whole rocket in pixcel.
            scale_factor (float): scale factor as the ratio of the window height to the total length of the rocket.
            rotateion_matrix (np.ndarray): rotation matrix for the fin. must be 2x2 matrix.
            beta (float): roll angle for the fin(degrees).
        """
        # points = [np.dot(rotation_matrix, point) for point in self.points]

        # polygon = [point * scale_factor + pos for point in points]

        diff = 2 * np.pi / self.n_fin
        beta = np.radians(beta)

        self.polygons = [
            [
                np.dot(rotation_matrix, point * np.array([np.cos(diff * i + beta), 1]))
                * scale_factor
                + pos
                for point in self.points
            ]
            for i in range(self.n_fin)
        ]
        self.z_order = [
            (diff * i + beta) % (2 * np.pi) <= np.pi for i in range(self.n_fin)
        ]  # True: forward, False: backward

    def draw_backward(self, screen: pg.surface):
        """
        Draw the fin on the screen.
        Only for the backward fin.

        Args:
            screen (pg.surface): screen to draw the fin.
        """
        for polygon, z_order in zip(self.polygons, self.z_order):
            if not z_order:
                pg.draw.polygon(screen, pg.Color("blue"), polygon)
                pg.draw.polygon(screen, pg.Color("black"), polygon, width=1)

    def draw_forward(self, screen: pg.surface):
        """
        Draw the fin on the screen.
        Only for the forward fin.

        Args:
            screen (pg.surface): screen to draw the fin.
        """
        for polygon, z_order in zip(self.polygons, self.z_order):
            if z_order:
                pg.draw.polygon(screen, pg.Color("blue"), polygon)
                pg.draw.polygon(screen, pg.Color("black"), polygon, width=1)


if __name__ == "__main__":
    rocket: Rocket = Rocket("simple.ork")
    rocket.run_simulation()
