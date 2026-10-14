# SMS Elastic Launched Glider launcher v0.4

A printable prototype with a fully exposed wooden ruler top, independent numbered bank/pitch dials, separate +/-8 degree vial calibration, a defined axial draw scale and a removable unloaded alignment sight. This supplies CAD and instructions; the hardware checklist must still be sourced and packed to make a complete physical kit.

**Read ELG_Launcher_v04_Assembly_and_Calibration_Guide.pdf first.** Print coupon 12 + 13 first. Default wood cross section remains **30 x 6 mm**; default length is now **914.4 mm (36 inches)**. Vials remain **25 x 8 mm**. Existing 900 mm rulers work; regenerate the scale for the actual length. No load rating, angular accuracy or final 2027 competition compliance is established.

## Upgrade from v0.3

Print **07, 09, 10, 15 and 16 once each**. These replace the marker moving jaw, roll bracket and pitch scale and add a bank rotor and setup sight. Reuse 01-06, 08 and 11-14; keep both copies of 14. Part 15 has the same geometry as 11, so an extra v0.3 part 11 can serve as the bank rotor. Part 16 is optional during use but included for unloaded alignment setup.

Add one M4 x 20 bank pivot, 1 nylon spacer + 2 metal washers (1 mm thick, <=9 mm OD) and one M4 nut; 2 M3 x 12 sight screws, 2 M3 nuts and 4 M3 metal washers (1 mm, <=7 mm OD). Transfer the existing roll carrier hardware from old 09 to 15. Use the retained 4 x 40 mm pin and collars specified in the new guide; a different retained pin requires its own clearance check. Do not reuse the old fixed roll bracket with the new bank carrier.

Full set: **16 unique STL files, 17 printed pieces including both coupon halves**. Print 14 twice, all others once. STLs are in mm, placed at bed Z=0. STEP files are in assembly-local coordinates. The complete assembly is a reference, not a single print.

## Measurement definitions

- **Bank:** rotation about the ruler's long axis, +/-30 degrees. Positive raises the +Y edge (the bank-bracket side). Center the roll bubble to realize the selected bank, except near vertical where gravity gives little or no bank reference.
- **Pitch dial:** 0-90 degrees. For desired ruler elevation theta and bank phi, use `p = atan2(sin(theta), cos(theta)*cos(phi))`. At zero bank p = theta. The included table/helper applies this coupling correction. Verify with an independent angle gauge at actual settings.
- **Axial draw:** rear wood end x=0, front wood end x=L; pin center x=L+15. At hook station xH, `D=L+15-xH`. The side scale reads D directly. Record relaxed just-taut reading D0 for the exact rubber and hook, then axial pullback extension is `D-D0`. This is not total loop length or the curved rubber path around the sleeve. For 3D straight endpoint distance, include measured lateral/vertical offsets.
- **Alignment:** part 16 is a removable sight used without elastic tension to transfer a repeatable hook station and two fuselage reference marks. Remove the sight and its loose hardware before stretching. Hand positioning and release remain user-controlled; no glider is mechanically held in a guaranteed attitude.
- **Angle of attack:** the instrument measures ruler orientation, not wing-chord angle relative to incoming airflow. Use a known glider reference to record an initial geometric chord offset; that does not measure aerodynamic angle of attack.

## Build and use

Follow the PDF for the complete hardware list, assembly, calibration, example settings, scale installation and bench checks. Rub contrasting paint into the engraved dial numbers and ticks; the preview shows illustrative white infill. Tick spacing is 5 degrees, not a precision rating. Mark a witness line on each calibrated carrier.

The optional side scale has a continuous SVG and a five-segment letter-size PDF. Print at actual size/100%, check the 100 mm bar, and overlap segments by 10 mm. Start at the FRONT wooden end; values increase toward the rear. Keep the strip below the top plane. The ruler's own markings also work using the stated datum formula.

At each launch: confirm sight removed, same glider/rubber IDs, clamp and pin retention, intended D, correct dial settings and both centered bubbles, then use the established hand release. Physical fit, ruler-side friction, creep, strength, hand/glider/elastic clearance, calibration drift and launch repeatability still need testing. Begin with low elastic tension and eye protection, under adult supervision; stop if anything slips, cracks or shifts.

## Files and regeneration

- `STL/`, `STEP/`, `ELG_Launcher_Assembly.step`: printable parts and editable CAD.
- `build_launcher.py`: parameterized geometry and assembly checks.
- `check_adjustment.py`: 37 distinct sampled combinations at explicit default dimensions.
- `launch_settings.py`: dependency-free angle and draw helper with independent forward-vector checks.
- `render_preview.py`, `make_scale.py`, `make_guide.py`: reproducible presentation files.
- `geometry_checks.json`, `adjustment_checks.json`, `validation_summary.json`: measured digital results and limits.

```bash
python -m pip install -r requirements.txt
python build_launcher.py --width 30 --thickness 6 --length 914.4 --vial-length 25 --vial-diameter 8
python check_adjustment.py
python launch_settings.py --self-test --elevation 60 --bank 20
python render_preview.py
python make_scale.py
python make_guide.py
```

The build accepts wood widths 22-40 mm, thickness 4-10 mm, lengths 700-950 mm, vial lengths 20-26 mm and diameters 6-8 mm. Acceptance by the parser is not a claim every possible configuration was tested. Use measured dimensions and inspect the resulting checks; do not globally scale STLs. Use `--pitch-angle`, `--bank-angle`, `--pitch-trim`, `--roll-trim`, and `--sight-height` to check a specific pose. `check_adjustment.py` intentionally uses defaults and does not validate resized parts.

The guide-rendering scripts expect DejaVu Sans fonts under `/usr/share/fonts/truetype/dejavu/`; adjust those font paths when regenerating documents on another operating system. This does not affect the supplied STL, STEP or PDF files.

The source has no automated trigger or latch. It is a hand-release glider launcher prototype.
