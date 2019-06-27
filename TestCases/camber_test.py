from AeroSandbox import *

p = Airplane(
    name="Single Wing",
    xyz_ref=[0, 0, 0],
    wings=[
        Wing(
            name="Wing",
            xyz_le=[0, 0, 0],
            symmetric=True,
            sections=[
                WingSection(
                    xyz_le=[0, 0, 0],
                    chord=0.5,
                    twist=0,
                    airfoil=Airfoil(name="naca9412")
                ),
                WingSection(
                    xyz_le=[0, 1, 0],
                    chord=0.5,
                    twist=0,
                    airfoil=Airfoil(name="naca9412")
                )
            ]
        )
    ]
)
p.set_ref_dims_from_wing()
ap= vlm1(airplane=p,
         op_point = OperatingPoint(
    velocity = 10, alpha=0, beta = 0
))
ap.run()
ap.draw()