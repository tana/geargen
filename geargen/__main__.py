import argparse

import cadquery as cq

from geargen.profile import involuteProfile

if __name__ == "__main__":
    argParser = argparse.ArgumentParser(prog="geargen")
    argParser.add_argument("-o", "--output", required=True)
    argParser.add_argument("-m", "--module", type=float, required=True)
    argParser.add_argument("-n", "--teeth", type=int, required=True)
    argParser.add_argument("-w", "--width", type=float, required=True)
    argParser.add_argument("--pressure-angle", type=float, default=20)

    args = argParser.parse_args()

    result = involuteProfile(
        args.module, args.teeth, pressureAngle=args.pressure_angle
    ).extrude(args.width)

    cq.exporters.export(result, args.output)
