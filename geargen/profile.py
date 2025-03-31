from math import pi, sin, cos, tan, acos
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
    module: float, teeth: int, pressureAngle: float = 20.0
) -> cq.Workplane:
    """Create an involute gear profile at the center of the XY plane"""

    pressureAngleRad = pressureAngle * pi / 180
    pitchRadius = module * teeth / 2
    baseRadius = pitchRadius * cos(pressureAngleRad)
    tipRadius = pitchRadius + module
    rootRadius = pitchRadius - 1.25 * module
    # Angular thickness of an involute part of the tooth
    involuteAngle = tan(acos(baseRadius / tipRadius)) - acos(baseRadius / tipRadius)
    pitchInvoluteAngle = tan(pressureAngleRad) - pressureAngleRad
    # Angular thickness of the tip arc (crest)
    # Assuming tooth width on the pitch circle is half of the pitch
    tipAngle = pi / teeth + 2 * (pitchInvoluteAngle - involuteAngle)

    wp = cq.Workplane("XY")
    wp = wp.moveTo(rootRadius, 0)

    for i in range(teeth):
        startAngle = 2 * pi * i / teeth
        endAngle = 2 * pi * (i + 1) / teeth

        # Draw the outward involute curve
        wp = wp.lineTo(baseRadius * cos(startAngle), baseRadius * sin(startAngle))
        wp = wp.parametricCurve(
            lambda t: involute(
                (tipRadius - baseRadius) * t + baseRadius, baseRadius, startAngle, False
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
                (tipRadius - baseRadius) * (1 - t) + baseRadius,
                baseRadius,
                startAngle + 2 * involuteAngle + tipAngle,
                True,
            ),
            N=16,
            makeWire=False,
        )
        wp = wp.lineTo(
            rootRadius * cos(startAngle + 2 * involuteAngle + tipAngle),
            rootRadius * sin(startAngle + 2 * involuteAngle + tipAngle),
        )
        # # Draw the root between teeth
        wp = wp.radiusArc(
            (rootRadius * cos(endAngle), rootRadius * sin(endAngle)), -rootRadius
        )

    wp = wp.close()

    return wp
