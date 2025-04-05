# geargen
**geargen** is a command-line-based, CAD-independent generator for gears.

## Features
- Spur gears
- Helical and herringbone gears
- Internal gears
- Bevel gears with arbitrary shaft angle

## Usage
All parameters are specified by command line options.
Distances are specified in millimeters and angles are specified in degrees.

Note: it only generates the essential part of a gear. Additional parts, such as the shaft bore or the hub, has to be added afterwards using CAD programs.

### Spur gear
Spur gear with module 2, 16 teeth, and 10 mm width:

```
geargen -m 2 -n 16 -w 10 -o spur.step
```

- `-m` option specifies the value of module.
- `-n` specifies number of teeth.
- `-w` specifies gear width.
- `-o` specifies the name of a STEP file to be written.

### Herringbone gear
Herringbone gear with helix angle of 30 degrees, module 1, 32 teeth, 10 mm width:

```
geargen -t herringbone -ha 30 -m 1 -n 32 -w 10 -o herringbone.step
```

- `-t` option changes gear type. Also helical gears can be generated with `-t helical`.
- `-ha` specifies helix angle (default 20 deg).

### Internal gear
Internal spur gear with module 1, 50 teeth, 10 mm width, and outer diameter of 60 mm:

```
geargen -t internal -m 1 -n 50 -w 10 -od 60 -o internal.step
```

- `-t internal` means internal spur gear. `-t internal_helical` and `-t internal_herringbone` are also supported.
- `-od` specifies outer diameter.

### Bevel gear
Bevel gear with module 1, 20 teeth, and 10 mm facewidth, meshes with a 40-teeth gear at 90 degrees:

```
geargen -t bevel -m 1 -n 20 -w 10 -nc 40 -sa 90 -o bevel.step
```

- `-nc` option specifies number of teeth of the counterpart.
- `-sa` specifies shaft angle (default 90 deg).

## TODO
- [ ] Profile shifting
- [ ] Timing belt profile (GT2)