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
    type: Literal[
        "spur",
        "helical",
        "herringbone",
        "internal",
        "internal_helical",
        "internal_herringbone",
    ] = "spur",
    helixAngle: float = 20,
    normal: bool = False,
    outerDiameter: float | None = None,
) -> cq.Solid:
    pressureAngleRad = pressureAngle * pi / 180
    helixAngleRad = pi * helixAngle / 180
    pitchRadius = module * teeth / 2

    if normal and (type == "helical" or type == "herringbone"):
        # Convert normal module and pressure angle into axial ones
        module = module / cos(helixAngleRad)
        pressureAngle = atan(tan(pressureAngleRad) / cos(helixAngleRad)) * 180 / pi

    internal = type in set(["internal", "internal_helical", "internal_herringbone"])

    profile = involuteProfile(
        module,
        teeth,
        pressureAngle=pressureAngle,
        rootFillet=rootFillet,
        internal=internal,
    )

    wp = cq.Workplane(obj=profile).toPending()
    if type == "spur" or type == "internal":
        solid = wp.extrude(width).val()
    elif type == "helical" or type == "internal_helical":
        solid = wp.twistExtrude(
            width, (180 / pi) * width * tan(helixAngleRad) / pitchRadius
        ).val()
    elif type == "herringbone" or type == "internal_herringbone":
        wp = wp.twistExtrude(
            width / 2, (180 / pi) * width * tan(helixAngleRad) / pitchRadius / 2
        )
        solid = wp.mirror(wp.faces("+Z"), union=True).val()
    if internal:
        assert outerDiameter is not None
        solid = (
            cq.Workplane("XY")
            .circle(outerDiameter / 2)
            .extrude(width)
            .cut(cast(cq.Solid, solid))
            .val()
        )
    return cast(cq.Solid, solid)
