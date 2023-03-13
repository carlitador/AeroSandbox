import aerosandbox as asb
import aerosandbox.numpy as np
import aerosandbox.tools.units as u
from typing import Dict, Union


# From Torenbeek: "Synthesis of Subsonic Airplane Design", 1976, Delft University Press
# Chapter 8: "Airplane Weight and Balance"

def mass_wing_simple(
        wing: asb.Wing,
        design_mass_TOGW: float,
        ultimate_load_factor: float,
        suspended_mass: float,
        main_gear_mounted_to_wing: bool = True,
) -> float:

    k_w = np.blend(
        (design_mass_TOGW - 5670) / 2000,
        6.67e-3,
        4.90e-3
    )

    span = wing.span() / np.cosd(wing.mean_sweep_angle(x_nondim=0.5))

    wing_root_thickness = wing.xsecs[0].airfoil.max_thickness() * wing.xsecs[0].chord

    return suspended_mass * (
            k_w *
            span ** 0.75 *
            (1 + (1.905 / span) ** 0.5) *
            ultimate_load_factor ** 0.55 *
            ((span / wing_root_thickness) / (suspended_mass / wing.area())) ** 0.30 *
            (1 if main_gear_mounted_to_wing else 0.95)
    )


def mass_wing(
        wing: asb.Wing,
        design_mass_TOGW: float,
        ultimate_load_factor: float,
        suspended_mass: float,
        never_exceed_airspeed: float,
        max_airspeed_for_flaps: float,
        main_gear_mounted_to_wing: bool = True,
        flap_deflection_angle: float = 30,
        strut_y_location: float = None,
        return_dict: bool = False,
) -> Union[float, Dict[str, float]]:
    """
    Computes the mass of a wing of an aircraft, according to Torenbeek's "Synthesis of Subsonic Airplane Design",
    1976, Appendix C: "Prediction of Wing Structural Weight".

    Likely more accurate than the Raymer wing weight models.

    Args:

        wing: The wing object.

        design_mass_TOGW: The design takeoff gross weight of the entire aircraft [kg].

        ultimate_load_factor: The ultimate load factor of the aircraft. 1.5x the limit load factor.

        suspended_mass: The mass of the aircraft that is suspended from the wing [kg].

        never_exceed_airspeed: The never-exceed airspeed of the aircraft [m/s]. Used for flutter calculations.

        max_airspeed_for_flaps: The maximum airspeed at which the flaps are allowed to be deployed [m/s]. In the
        absence of other information, 1.8x stall speed is a good guess.

        main_gear_mounted_to_wing: Whether the main gear is mounted to the wing structure.

        flap_deflection_angle: The maximum deflection angle of the flaps [deg].

        strut_y_location: The y-location of the strut (if any), relative to the wing's leading edge [m]. If None,
        it is assumed that there is no strut (i.e., the wing is a cantilever beam).

        return_dict: Whether to return a dictionary of all the intermediate values, or just the final mass. Defaults
        to False, which returns just the final mass.

    Returns: If return_dict is False (default), returns a single value: the mass of the wing [kg]. If return_dict is
    True, returns a dictionary of all the intermediate values.

    """

    # Wing span
    span = wing.span()

    # Sweep at 50% chord
    sweep_half_chord = wing.mean_sweep_angle(x_nondim=0.5)
    cos_sweep_half_chord = np.cosd(sweep_half_chord)

    # Structural wing span
    span_structural = span / cos_sweep_half_chord

    # Airfoil thickness over chord ratio at root
    root_t_over_c = wing.xsecs[0].airfoil.max_thickness()

    # Torenbeek Eq. C-2
    # `k_no` represents penalties due to skin joints, non-tapered skin, minimum gauge, etc.
    k_no = 1 + (1.905 / span_structural) ** 0.5

    # Torenbeek Eq. C-3
    # `k_lambda` represents penalties due to taper ratio
    k_lambda = (1 + wing.taper_ratio()) ** 0.4

    # Torenbeek unlabeled equations, between C-3 and C-4
    # `k_e` represents weight knockdowns due to bending moment relief from engines mounted in front of elastic axis.
    k_e = 1

    # `k_uc` represents weight knockdowns due to undercarriage.
    k_uc = 1 if main_gear_mounted_to_wing else 0.95

    # Torenbeek Eq. C-4
    # `k_st` represents weight excrescence due to structural stiffness against flutter.
    k_st = (
            1 +
            9.06e-4 * (
                    (span * np.cosd(wing.mean_sweep_angle(x_nondim=0))) ** 3 /
                    design_mass_TOGW
            ) * (
                    never_exceed_airspeed / 100 / root_t_over_c
            ) ** 2 *
            cos_sweep_half_chord
    )

    # Torenbeek Eq. C-5
    # `k_b` represents weight knockdowns due to bending moment relief from strut location.
    if strut_y_location is None:
        k_b = 1
    else:
        k_b = 1 - (strut_y_location / (wing.span() / 2)) ** 2

    ### Use all the above to compute the basic wing structural mass
    mass_basic_wing_structure = (
            4.58e-3 *
            k_no *
            k_lambda *
            k_e *
            k_uc *
            k_st *
            (
                    k_b * ultimate_load_factor * (0.8 * suspended_mass + 0.2 * design_mass_TOGW)
            ) ** 0.55 *
            span ** 1.675 *
            root_t_over_c ** -0.45 *
            cos_sweep_half_chord ** -1.325
    )

    S_flaps = wing.control_surface_area()

    # Torenbeek Eq. C-10
    k_f1 = 1 # single-slotted; double slotted, fixed hinge # TODO add details
    k_f2 = 1 # slotted flaps with fixed vane # TODO add details

    k_f = k_f1 * k_f2

    mass_trailing_edge_flaps = S_flaps * (
            2.706 * k_f *
            (S_flaps * span_structural) ** (3 / 16) *
            (
                    (max_airspeed_for_flaps / 100) ** 2 *
                    np.sind(flap_deflection_angle) *
                    np.cosd(wing.mean_sweep_angle(x_nondim=1)) /
                    root_t_over_c
            ) ** (3 / 4)
    )

    mass_leading_edge_devices = 0

    mass_high_lift_devices = mass_trailing_edge_flaps + mass_leading_edge_devices

    mass_spoilers_and_speedbrakes = np.softmax(
        12.2 * wing.area(),
        0.015 * mass_basic_wing_structure,
    )

    mass_wing = (
            mass_basic_wing_structure +
            1.2 * (mass_high_lift_devices + mass_spoilers_and_speedbrakes)
    )

    if return_dict:
        return locals()
    else:
        return mass_wing

# def mass_hstab(
#         hstab: asb.Wing,
#         design_mass_TOGW: float,
#         ultimate_load_factor: float,
#         suspended_mass: float,
#         main_gear_mounted_to_wing: bool = True,
# ) -> float:
#
#     k_wt = 0.64

def mass_fuselage(
        fuselage: asb.Fuselage,
        design_mass_TOGW: float,
        ultimate_load_factor: float,
):
    pass