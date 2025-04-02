from math import pi, sin, cos, tan, acos, atan2
from typing import cast
import cadquery as cq


def involute(
    r: float, baseRadius: float, startAngle: float, rev: bool
) -> tuple[float, float]:
    """Calculate points on a involute curve based on radial position as the parameter"""

    alpha = acos(baseRadius / r)
    invAlpha = tan(alpha) - alpha
    if rev:
        return (r * cos(-invAlpha + startAngle), r * sin(-invAlpha + startAngle))
    else:
        return (r * cos(invAlpha + startAngle), r * sin(invAlpha + startAngle))


def involuteProfile(
    module: float,
    teeth: int,
    pressureAngle: float = 20.0,
    rootFillet: float | None = None,
    internal: bool = False,
) -> cq.Wire:
    """Create an involute gear profile at the center of the XY plane"""

    if rootFillet is None:
        rootFillet = 0.38 * module

    pressureAngleRad = pressureAngle * pi / 180
    pitchRadius = module * teeth / 2
    baseRadius = pitchRadius * cos(pressureAngleRad)
    tipRadius = pitchRadius + 1.25 * module if internal else pitchRadius + module
    rootRadius = pitchRadius - module if internal else pitchRadius - 1.25 * module
    # Angular thickness of an involute part of the tooth
    involuteAngle = tan(acos(baseRadius / tipRadius)) - acos(baseRadius / tipRadius)
    pitchInvoluteAngle = tan(pressureAngleRad) - pressureAngleRad
    # Angular thickness of the tip arc (crest)
    # Assuming tooth width on the pitch circle is half of the pitch
    tipAngle = pi / teeth + 2 * (pitchInvoluteAngle - involuteAngle)

    involuteStartRadius = max(baseRadius, rootRadius)
    # Angular offset for connecting a root arc and an involute (when rootRadius < baseRadius)
    (involuteStartX, involuteStartY) = involute(involuteStartRadius, baseRadius, 0, False)
    involuteStartAngle = atan2(involuteStartY, involuteStartX)

    wp = cq.Workplane("XY")
    wp = wp.moveTo(rootRadius * cos(involuteStartAngle), rootRadius * sin(involuteStartAngle))

    for i in range(teeth):
        startAngle = 2 * pi * i / teeth
        endAngle = 2 * pi * (i + 1) / teeth

        # Connection between the root and an involute has two cases
        # https://involutegearsoft.hatenablog.com/entry/2023/09/18/163506
        if rootRadius < baseRadius:
            # Parts near the root are approximated by straight line (unless there are many teeth)
            wp = wp.lineTo(baseRadius * cos(startAngle), baseRadius * sin(startAngle))
        # Draw the outward involute curve
        wp = wp.parametricCurve(
            lambda t: involute(
                (tipRadius - involuteStartRadius) * t + involuteStartRadius,
                baseRadius,
                startAngle,
                False,
            ),
            N=16,
            makeWire=False,
        )
        # Draw the tip of the tooth
        wp = wp.radiusArc(
            (
                tipRadius * cos(startAngle + involuteAngle + tipAngle),
                tipRadius * sin(startAngle + involuteAngle + tipAngle),
            ),
            -tipRadius,
        )
        # Draw the inward involute curve
        wp = wp.parametricCurve(
            lambda t: involute(
                (tipRadius - involuteStartRadius) * (1 - t) + involuteStartRadius,
                baseRadius,
                startAngle + 2 * involuteAngle + tipAngle,
                True,
            ),
            N=16,
            makeWire=False,
        )
        if rootRadius < baseRadius:
            wp = wp.lineTo(
                rootRadius * cos(startAngle + 2 * involuteAngle + tipAngle),
                rootRadius * sin(startAngle + 2 * involuteAngle + tipAngle),
            )
        # Draw the root between teeth
        wp = wp.radiusArc(
            (rootRadius * cos(endAngle + involuteStartAngle), rootRadius * sin(endAngle + involuteStartAngle)), -rootRadius
        )

    wp = wp.close()
    wire = cast(cq.Wire, wp.val())

    # TODO: Fillet for gears with many teeths (currently fillet2D raises error)
    if rootRadius < baseRadius:
        # Fillet only root vertices
        rootVertices = [
            v
            for v in wire.Vertices()
            if v.X * v.X + v.Y * v.Y < (rootRadius * 1.001) ** 2
        ]
        assert len(rootVertices) == 2 * teeth
        wire = wire.fillet2D(
            radius=0.1, vertices=rootVertices
        )  # This has to be fillet2D, not fillet

    return wire
