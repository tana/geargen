from typing import Literal, cast
from math import pi, cos, tan, atan
import cadquery as cq
from .profile import involuteProfile


def makeParallelShaftGear(
    module: float,
    teeth: int,
    width: float,
    pressureAngle: float = 20.0,
    rootFillet: float | None = None,
    type: Literal["spur", "helical", "herringbone"] = "spur",
    helixAngle: float = 20,
    normal: bool = False,
) -> cq.Solid:
    pressureAngleRad = pressureAngle * pi / 180
    helixAngleRad = pi * helixAngle / 180
    pitchRadius = module * teeth / 2

    if normal and (type == "helical" or type == "herringbone"):
        # Convert normal module and pressure angle into axial ones
        module = module / cos(helixAngleRad)
        pressureAngle = atan(tan(pressureAngleRad) / cos(helixAngleRad)) * 180 / pi

    profile = involuteProfile(
        module,
        teeth,
        pressureAngle=pressureAngle,
        rootFillet=rootFillet,
    )

    wp = cq.Workplane(obj=profile).toPending()
    if type == "spur":
        solid = wp.extrude(width).val()
    elif type == "helical":
        solid = wp.twistExtrude(
            width, (180 / pi) * width * tan(helixAngleRad) / pitchRadius
        ).val()
    elif type == "herringbone":
        wp = wp.twistExtrude(
            width / 2, (180 / pi) * width * tan(helixAngleRad) / pitchRadius / 2
        )
        solid = wp.mirror(wp.faces("+Z"), union=True).val()
    return cast(cq.Solid, solid)
