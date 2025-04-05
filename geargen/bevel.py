from typing import Literal, cast
from math import pi, sin, cos, tan, atan, sqrt
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace  # type: ignore
from OCP.gp import gp_Sphere  # type: ignore
from .profile import involuteProfile


def makeBevelGear(
    module: float,
    teeth: int,
    counterpartTeeth: int,
    width: float,
    shaftAngle: float = 90.0,
    pressureAngle: float = 20.0,
    rootFillet: float | None = None,
    type: Literal["bevel"] = "bevel",
    flatPartCoeff: float = 0.8,
) -> cq.Solid:
    pitchRadius = module * teeth / 2
    shaftAngleRad = shaftAngle * pi / 180
    coneAngle = atan(
        sin(shaftAngleRad) / ((counterpartTeeth / teeth) + cos(shaftAngleRad))
    )
    coneDistance = pitchRadius / sin(coneAngle)
    coneHeight = pitchRadius / tan(coneAngle)

    profile = involuteProfile(
        module,
        teeth,
        pressureAngle=pressureAngle,
        rootFillet=rootFillet,
    )

    outerSphere = cq.Solid.makeSphere(coneDistance)

    # Project the profile onto a sphere
    projected = cast(
        cq.Wire,
        profile.translate((0, 0, coneHeight)).project(
            cast(cq.Face, outerSphere.faces("not %PLANE")), (0, 0, -1), closest=True
        ),
    )

    # Create spherical face from the projected Wire
    gpSphere = gp_Sphere()
    gpSphere.SetRadius(coneDistance)
    mf = BRepBuilderAPI_MakeFace(gpSphere, projected.wrapped)
    outerFace = cq.Face(mf.Face()).fix()

    # Extrude it to make a bevel gear with specified facewidth
    solid = outerFace.thicken(-width)

    innerConeDistance = coneDistance - width
    innerConeHeight = coneHeight * (innerConeDistance / coneDistance)
    bottomFlatRadius = flatPartCoeff * pitchRadius
    topFlatRadius = bottomFlatRadius * innerConeDistance / coneDistance
    solid = cast(
        cq.Solid,
        solid
        + cq.Solid.makeCylinder(    # Add top spherical part
            topFlatRadius,
            coneHeight - innerConeHeight,
            pnt=(
                0,
                0,
                sqrt(innerConeDistance**2 - topFlatRadius**2),
            )
        )
        - cq.Solid.makeCylinder(    # Remove bottom spherical part
            bottomFlatRadius,
            coneDistance,
            pnt=(
                0,
                0,
                sqrt(coneDistance**2 - bottomFlatRadius**2),
            ),
        ),
    )

    return solid
