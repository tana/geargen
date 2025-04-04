import argparse
import sys
import cadquery as cq
from .parallel import makeParallelShaftGear
from .bevel import makeBevelGear


def main():
    argParser = argparse.ArgumentParser(prog="geargen")
    argParser.add_argument("-o", "--output", required=True)
    argParser.add_argument("-m", "--module", type=float, required=True)
    argParser.add_argument("-n", "--teeth", type=int, required=True)
    argParser.add_argument("-w", "--width", type=float, required=True)
    argParser.add_argument("--root-fillet", type=float)
    argParser.add_argument("--pressure-angle", type=float, default=20)
    argParser.add_argument("-ha", "--helix_angle", type=float, default=20)
    argParser.add_argument("-t", "--type", default="spur")
    argParser.add_argument("--normal", action="store_true")
    argParser.add_argument("-od", "--outer_diameter", type=float)
    argParser.add_argument("-nc", "--counterpart_teeth", type=int)
    argParser.add_argument("-sa", "--shaft_angle", type=float, default=90)

    args = argParser.parse_args()

    if (
        args.type == "spur"
        or args.type == "helical"
        or args.type == "herringbone"
        or args.type == "internal"
        or args.type == "internal_helical"
        or args.type == "internal_herringbone"
    ):
        if (
            args.type == "internal"
            or args.type == "internal_helical"
            or args.type == "internal_herringbone"
        ) and args.outer_diameter is None:
            print(
                "Outer diameter (-od) is necessary for internal gears", file=sys.stderr
            )
            return -1

        result = makeParallelShaftGear(
            args.module,
            args.teeth,
            args.width,
            pressureAngle=args.pressure_angle,
            rootFillet=args.root_fillet,
            type=args.type,
            helixAngle=args.helix_angle,
            normal=args.normal,
            outerDiameter=args.outer_diameter,
        )
    elif args.type == "bevel":
        result = makeBevelGear(
            args.module,
            args.teeth,
            args.counterpart_teeth,
            args.width,
            shaftAngle=args.shaft_angle,
            pressureAngle=args.pressure_angle,
            rootFillet=args.root_fillet,
            type=args.type,
        )
    else:
        print("Unsupported gear type", file=sys.stderr)
        return -1

    cq.exporters.export(result, args.output)

    return 0
