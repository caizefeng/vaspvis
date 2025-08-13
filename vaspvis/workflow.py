import vaspvis.warnings_config
import os

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

from vaspvis import Band, Dos
from vaspvis.band_helpers import clean_data_GW, compare_signs
from vaspvis.band_helpers import get_magmoment
from vaspvis.standard import _figure_setup_band_dos


def plot_band_dos_and_inset(
        compare_data_array,
        compare_data_label_array,
        is_gw_list,
        band_folder_list,
        element_spd_dict_main,
        color_list_main,
        output_folder,
        element_spd_dict_inset=None,
        color_list_inset=None,
        wannier_suffix="-bands",
        sp_scale_factor=1.2,
        fill=True,
        alpha=0.3,
        linewidth=1.25,
        sigma=0.05,
        delta=0.0375,
        legend=False,
        erange=(-4, 4),
        fontsize=14,
        figsize_main=(6, 4),
        dos_figsize=(2, 4),
):
    """
    Function to plot band structure and DOS along with an inset-style DOS plot.

    Example Input:
        compare_data_array = ["/path/to/data1", "/path/to/data2"]
        compare_data_label_array = ["GW", "PBE"]
        is_gw_list = [True, False]
        band_folder_list = ["gw_band_SP", "band_GXWKGL"]
        element_spd_dict_main = {"Mn": "d", "Co": "d", "In": "p"}
        color_list_main = ["#d150fb", "#cd2b00", "#00bdff"]
        element_spd_dict_inset = {"Co": "d", "Mn": "d", "In": "p"}
        color_list_inset = ["#cd2b00", "#d150fb", "#00bdff"]
        output_folder = "./output"

    Parameters:
        compare_data_array (list): List of paths to data directories.
        compare_data_label_array (list): List of labels for the datasets.
        is_gw_list (list): List of booleans indicating if the data is GW-calculated.
        band_folder_list (list): List of subfolder names containing band structure data.
        element_spd_dict_main (dict): Element-SPD mapping for the main plot.
        color_list_main (list): Colors for the main plot.
        output_folder (str): Directory to save the output plots.
        element_spd_dict_inset (dict, optional): Element-SPD mapping for the inset plot.
        color_list_inset (list, optional): Colors for the inset plot.
        wannier_suffix (str, optional): Suffix for Wannier band files.
        sp_scale_factor (float, optional): Scale factor for non-GW spin-resolved band plots.
        fill (bool, optional): Whether to fill the DOS plots.
        alpha (float, optional): Transparency for the DOS plots.
        linewidth (float, optional): Line width for DOS plots.
        sigma (float, optional): Gaussian smearing for DOS.
        delta (float, optional): Spin polarization window.
        legend (bool, optional): Whether to show the legend.
        erange (tuple, optional): Energy range for the plots.
        fontsize (int, optional): Font size for labels.
        figsize_main (tuple, optional): Figure size for the main plot.
        dos_figsize (tuple, optional): Figure size for the inset plot.

    Returns:
        None
    """

    if element_spd_dict_inset is None:
        element_spd_dict_inset = element_spd_dict_main

    if color_list_inset is None:
        color_list_inset = color_list_main

    os.makedirs(output_folder, exist_ok=True)

    dos_folder = "dos"

    for data_path, data_label, is_gw, band_folder in zip(
            compare_data_array, compare_data_label_array, is_gw_list, band_folder_list):
        print(f"Processing: {data_label} | Path: {data_path}")

        band_path = f"{data_path}/{band_folder}"
        dos_path = f"{data_path}/{dos_folder}"

        # Load DOS data
        dos_up = Dos(folder=dos_path, spin='up', soc_axis="z", efermi_folder=dos_path)
        dos_down = Dos(folder=dos_path, spin='down', soc_axis="z", efermi_folder=dos_path)

        # === Plot Band Structure + DOS === #
        fig_main, ax_main = plt.subplots(nrows=1, ncols=2, sharey=True, figsize=figsize_main, dpi=400,
                               gridspec_kw={'width_ratios': [7, 3]})
        ax1, ax2 = _figure_setup_band_dos(ax=ax_main, fontsize=fontsize, ylim=erange)

        # Band plot
        if is_gw:
            # Load band data
            band_data, labels, labelx, efermi = clean_data_GW(
                data_path,
                gw_band_folder=band_folder,
                wannier_suffix=wannier_suffix,
                full_bz_folder=dos_folder)

            for band in band_data:
                ax1.scatter(band[:, 0], band[:, 1] - efermi,
                            c=compare_signs(band[:, 2], 0),
                            marker='o', s=0.5,
                            cmap=plt.cm.bwr_r  # Red = low, White = 0, Blue = high
                            )

            ax1.vlines(labelx, erange[0], erange[1], color='black', alpha=0.7, linewidth=0.5)
            ax1.set_xticks(labelx)
            ax1.set_xticklabels(labels, fontdict={'fontstyle': 'italic'})
            ax1.set_xlim(0, np.max(labelx))

        else:
            band_up = Band(
                folder=band_path,
                spin="up",
                soc_axis='z',
                efermi_folder=dos_path,
            )
            band_down = Band(
                folder=band_path,
                spin="down",
                soc_axis='z',
                efermi_folder=dos_path,
            )

            band_up.plot_plain(
                ax=ax1,
                erange=erange,
                sp_color="blue",
                linewidth=0,
                sp_scale_factor=sp_scale_factor,
            )
            band_down.plot_plain(
                ax=ax1,
                erange=erange,
                sp_color="red",
                linewidth=0,
                sp_scale_factor=sp_scale_factor,
            )

        ax1.axhline(y=0, color='black', linestyle='--', linewidth=0.75)

        # DOS plot
        dos_up.plot_element_spd(ax=ax2, element_spd_dict=element_spd_dict_main, fill=fill,
                                alpha=alpha, linewidth=linewidth, sigma=sigma,
                                energyaxis='y', color_list=color_list_main,
                                legend=legend, erange=erange)

        dos_down.plot_element_spd(ax=ax2, element_spd_dict=element_spd_dict_main, fill=fill,
                                  alpha=alpha, linewidth=linewidth, sigma=sigma,
                                  energyaxis='y', color_list=color_list_main,
                                  legend=legend, erange=erange)

        # Final plot formatting
        ax2.invert_xaxis()
        ax2.axvline(x=0, color='black', linewidth=linewidth)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.75)
        ax2.xaxis.set_major_locator(MaxNLocator(nbins=len(ax2.get_xticklabels()) - 2, prune='lower'))
        desired_xticks = [round(0.7 * max(ax2.get_xlim())), round(0.7 * min(ax2.get_xlim()))]
        ax2.set_xticks(desired_xticks)
        ax2.set_xlabel('DOS (arb. units)')

        fig_main.subplots_adjust(wspace=0)

        # Get original positions
        pos_band = ax1.get_position()
        pos_dos = ax2.get_position()

        # Shift upwards by 0.02 (play with the value)
        ax1.set_position([pos_band.x0, pos_band.y0 + 0.03, pos_band.width, pos_band.height])
        ax2.set_position([pos_dos.x0, pos_dos.y0 + 0.03, pos_dos.width, pos_dos.height])

        fig_main.savefig(f"{output_folder}/band_dos_{data_label}_spd.png", dpi=400, transparent=True)
        plt.show()


        # === Plot Inset-Style DOS Only === #
        plt.rcParams.update({'font.size': 11})
        fig_dos, ax_dos = plt.subplots(figsize=dos_figsize, dpi=440)

        # Plotting inset in reverse order
        dos_up.plot_element_spd(ax=ax_dos, element_spd_dict=element_spd_dict_inset, fill=fill,
                                alpha=alpha, linewidth=linewidth, sigma=sigma,
                                energyaxis='y', color_list=color_list_inset,
                                legend=False, erange=[-0.8, 0.8])

        dos_down.plot_element_spd(ax=ax_dos, element_spd_dict=element_spd_dict_inset, fill=fill,
                                  alpha=alpha, linewidth=linewidth, sigma=sigma,
                                  energyaxis='y', color_list=color_list_inset,
                                  legend=False, erange=[-0.8, 0.8])

        ax_dos.set_xlabel('DOS (arb. units)  ')
        ax_dos.set_ylabel('$E - E_{F}$ (eV)')
        ax_dos.axhline(y=0, color='black', linestyle='--', linewidth=0.75)
        ax_dos.invert_xaxis()

        pos_dos_panel = ax_dos.get_position()
        ax_dos.set_position([pos_dos_panel.x0+0.25, pos_dos_panel.y0, pos_dos_panel.width*0.7, pos_dos_panel.height])

        fig_dos.savefig(f"{output_folder}/dos_panel_{data_label}_spd.png", dpi=400, transparent=True,
                    # bbox_inches='tight', pad_inches=0.1
                        )
        plt.show()

    # === Generate Legend === #
    fig_legend, ax_legend = plt.subplots(figsize=(2.1, 2))
    dots = [mlines.Line2D([], [], color='grey', marker='o', linestyle='None', markersize=20, label='DOS')]

    for i, (k, v) in enumerate(element_spd_dict_main.items()):
        dots.append(mlines.Line2D([], [], color=color_list_main[i], marker='o', linestyle='None', markersize=20,
                                  label=f'{k}({v})'))

    ax_legend.legend(handles=dots, loc='center', fontsize=22, facecolor='white', edgecolor='k')
    ax_legend.axis('off')

    fig_legend.savefig(f'{output_folder}/dos_legend.png', dpi=900, transparent=True)
    plt.show()

    # === Calculate Spin Polarization === #
    fermi_spin_polarization(compare_data_array,
                            sigma=sigma,
                            delta=delta,
                            dos_folder=dos_folder)


def fermi_spin_polarization(compare_data_array, dos_erange=(-8, 8), sigma=0.05, delta=0.0375, dos_folder="dos"):
    """
    Calculate spin polarization for a list of datasets.

    Parameters:
        compare_data_array (list): List of paths to datasets.
        dos_erange (tuple, optional): Energy range for DOS calculations.
        sigma (float, optional): Gaussian smearing for DOS.
        delta (float, optional): Spin polarization window.
        dos_folder (str, optional): Subfolder name containing DOS data.

    Returns:
        dict: A dictionary with dataset paths as keys and spin polarization percentages as values.
    """
    spin_polarization_results = {}

    dummy_fig, dummy_ax = plt.subplots(figsize=(6, 2.5), dpi=400, nrows=1)

    for data_path in compare_data_array:
        print(f"Processing: {data_path}")

        # Get magnetic moment
        total_mag_val = get_magmoment(f"{data_path}/{dos_folder}")
        print(f"Magnetic moment: {total_mag_val}")

        # Load DOS for spin up
        dos_up = Dos(
            folder=f"{data_path}/{dos_folder}",
            spin="up",
            soc_axis="z",
            efermi_folder=f"{data_path}/{dos_folder}"
        )
        int_up = dos_up.plot_plain(
            ax=dummy_ax,  # No plotting
            energyaxis="x",
            sigma=sigma,
            erange=dos_erange,
            fill=False,
            SP_window=delta,
        )

        # Load DOS for spin down
        dos_down = Dos(
            folder=f"{data_path}/{dos_folder}",
            spin="down",
            soc_axis="z",
            efermi_folder=f"{data_path}/{dos_folder}"
        )
        int_dn = dos_down.plot_plain(
            ax=dummy_ax,  # No plotting
            energyaxis="x",
            sigma=sigma,
            erange=dos_erange,
            fill=False,
            SP_window=delta,
        )

        # Calculate spin polarization
        sp = (abs(int_up) - abs(int_dn)) / (abs(int_up) + abs(int_dn))
        spin_polarization_results[data_path] = 100 * sp
        print(f"Spin Polarization (%): {100 * sp}")

    plt.close(dummy_fig)

    return spin_polarization_results
