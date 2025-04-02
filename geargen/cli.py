import argparse
import sys
import cadquery as cq
from .parallel import makeParallelShaftGear


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

    args = argParser.parse_args()

    if args.type == "spur" or args.type == "helical" or args.type == "herringbone":
        result = makeParallelShaftGear(
            args.module,
            args.teeth,
            args.width,
            pressureAngle=args.pressure_angle,
            rootFillet=args.root_fillet,
            type=args.type,
            helixAngle=args.helix_angle,
            normal=args.normal,
        )
    else:
        print("Unsupported gear type", file=sys.stderr)
        return -1

    cq.exporters.export(result, args.output)

    return 0
