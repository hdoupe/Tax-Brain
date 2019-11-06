"""
Helper functions for the various taxbrain modules
"""
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.palettes import GnBu5
from collections import defaultdict

import taxcalc as tc
import behresp


def make_calculators(params, microdata, use_cps, verbose):
    """
    This function creates the baseline and reform calculators used when
    the `run()` method is called
    """
    # Create two microsimulation calculators
    gd_base = tc.GrowDiff()
    gf_base = tc.GrowFactors()
    # apply user specified growdiff
    if params["growdiff_baseline"]:
        gd_base.update_growdiff(params["growdiff_baseline"])
        gd_base.apply_to(gf_base)
    # Baseline calculator
    if use_cps:
        records = tc.Records.cps_constructor(data=microdata,
                                                gfactors=gf_base)
    else:
        records = tc.Records(microdata, gfactors=gf_base)
    policy = tc.Policy(gf_base)
    if params["base_policy"]:
        policy.implement_reform(params["base_policy"])
    base_calc = tc.Calculator(policy=policy,
                                records=records,
                                verbose=verbose)

    # Reform calculator
    # Initialize a policy object
    gd_reform = tc.GrowDiff()
    gf_reform = tc.GrowFactors()
    if params["growdiff_response"]:
        gd_reform.update_growdiff(params["growdiff_response"])
        gd_reform.apply_to(gf_reform)
    if use_cps:
        records = tc.Records.cps_constructor(data=microdata,
                                                gfactors=gf_reform)
    else:
        records = tc.Records(microdata, gfactors=gf_reform)
    policy = tc.Policy(gf_reform)
    if params["base_policy"]:
        policy.implement_reform(params["base_policy"])
    policy.implement_reform(params['policy'])
    # Initialize Calculator
    reform_calc = tc.Calculator(policy=policy, records=records,
                                verbose=verbose)
    # delete all unneeded variables
    del gd_base, gd_reform, records, gf_base, gf_reform, policy
    return base_calc, reform_calc


def run(varlist, run_func, year, calc_args):
    """
    Function for improving the memory usage of TaxBrain on Compute Studio
    Parameters
    ----------
    varlist: Variables from Tax-Calculator that will be saved
    year: year the calculator needs to run
    """
    base_calc, reform_calc = make_calculators(**calc_args)
    base_calc.advance_to_year(year)
    reform_calc.advance_to_year(year)
    return run_func(varlist, base_calc, reform_calc, year, params=calc_args["params"])


def static_run(varlist, base_calc, reform_calc, year, params):
    """
    Function for running a static simulation on the Compute Studio servers
    """
    # delay = [delayed(base_calc.calc_all()),
    #          delayed(reform_calc.calc_all())]
    # compute(*delay)
    base_calc.calc_all()
    reform_calc.calc_all()
    return year, base_calc.dataframe(varlist), reform_calc.dataframe(varlist)
    # self.base_data[year] = base_calc.dataframe(varlist)
    # self.reform_data[year] = reform_calc.dataframe(varlist)


def dynamic_run(varlist, base_calc, reform_calc, year, params):
    """
    Function for runnnig a dynamic simulation on the Compute Studio servers
    """

    base, reform = behresp.response(base_calc, reform_calc,
                                    params["behavior"],
                                    dump=True)
    # self.base_data[year] = base[varlist]
    # self.reform_data[year] = reform[varlist]
    # del base, reform
    return year, base[varlist], reform[varlist]


def weighted_sum(df, var, wt="s006"):
    """
    Return the weighted sum of specified variable
    """
    return (df[var] * df[wt]).sum()


def distribution_plot(tb, year, width=500, height=400):
    """
    Create a horizontal bar chart to display the distributional change in
    after tax income
    """
    def find_percs(data, group):
        """
        Find the percentage of people in the data set that saw
        their income change by the given percentages
        """
        pop = data["s006"].sum()
        large_pos_chng = data["s006"][data["pct_change"] > 5].sum() / pop
        small_pos_chng = data["s006"][(data["pct_change"] <= 5) &
                                      (data["pct_change"] > 1)].sum() / pop
        small_chng = data["s006"][(data["pct_change"] <= 1) &
                                  (data["pct_change"] >= -1)].sum() / pop
        small_neg_change = data["s006"][(data["pct_change"] < -1) &
                                        (data["pct_change"] > -5)].sum() / pop
        large_neg_change = data["s006"][data["pct_change"] < -5].sum() / pop

        return (
            large_pos_chng, small_pos_chng, small_chng, small_neg_change,
            large_neg_change
        )

    # extract needed data from the TaxBrain object
    ati_data = pd.DataFrame(
        {"base": tb.base_data[year]["aftertax_income"],
         "reform": tb.reform_data[year]["aftertax_income"],
         "s006": tb.base_data[year]["s006"]}
    )
    ati_data["diff"] = ati_data["reform"] - ati_data["base"]
    ati_data["pct_change"] = (ati_data["diff"] / ati_data["base"]) * 100
    ati_data = ati_data.fillna(0.)  # fill in NaNs for graphing
    # group tupules: (low income, high income, income group name)
    groups = [
        (-9e99, 9e99, "All"),
        (1e6, 9e99, "$1M or More"),
        (500000, 1e6, "$500K-1M"),
        (200000, 500000, "$200K-500K"),
        (100000, 200000, "$100K-200K"),
        (75000, 100000, "$75K-100K"),
        (50000, 75000, "$50K-75K"),
        (40000, 50000, "$40K-50K"),
        (30000, 40000, "$30K-40K"),
        (20000, 30000, "$20K-30K"),
        (10000, 20000, "$10K-20K"),
        (-9e99, 10000, "Less than $10K")
    ]

    plot_data = defaultdict(list)
    # traverse list in reverse to get the axis of the plot in correct order
    for low, high, grp in groups[:: -1]:
        # find income changes by group
        sub_data = ati_data[(ati_data["base"] <= high) &
                            (ati_data["base"] > low)]
        results = find_percs(sub_data, grp)
        plot_data["group"].append(grp)
        plot_data["large_pos"].append(results[0])
        plot_data["small_pos"].append(results[1])
        plot_data["small"].append(results[2])
        plot_data["small_neg"].append(results[3])
        plot_data["large_neg"].append(results[4])

    # groups used for plotting
    change_groups = [
        "large_pos", "small_pos", "small", "small_neg", "large_neg"
    ]
    legend_labels = [
        "Increase of > 5%", "Increase 1-5%", "Change < 1%",
        "Decrease of 1-5%", "Decrease > 5%"
    ]
    plot = figure(
        y_range=plot_data["group"], x_range=(0, 1), toolbar_location=None,
        width=width, height=height,
        title=f"Percentage Change in After Tax Income - {year}"
    )
    plot.hbar_stack(
        change_groups, y="group", height=0.8, color=GnBu5,
        source=ColumnDataSource(plot_data),
        legend=legend_labels
    )
    # general formatting
    plot.yaxis.axis_label = "Expanded Income Bin"
    plot.xaxis.axis_label = "Portion of Population"
    plot.xaxis.formatter = NumeralTickFormatter(format="0%")
    plot.xaxis.minor_tick_line_color = None
    # move legend out of main plot area
    legend = plot.legend[0]
    plot.add_layout(legend, "right")

    return plot


def differences_plot(tb, tax_type, width=500, height=400):
    """
    Create a bar chart that shows the change in total liability for a given
    tax
    """
    acceptable_taxes = ["income", "payroll", "combined"]
    msg = f"tax_type must be one of the following: {acceptable_taxes}"
    assert tax_type in acceptable_taxes, msg

    # find change in each tax variable
    tax_vars = ["iitax", "payrolltax", "combined"]
    agg_base = tb.multi_var_table(tax_vars, "base")
    agg_reform = tb.multi_var_table(tax_vars, "reform")
    agg_diff = agg_reform - agg_base

    # transpose agg_diff to make plotting easier
    plot_data = agg_diff.transpose()
    tax_var = tax_vars[acceptable_taxes.index(tax_type)]
    plot_data["color"] = np.where(plot_data[tax_var] < 0, "red", "blue")

    plot = figure(
        title=f"Change in Aggregate {tax_type.title()} Tax Liability",
        width=width, height=height, toolbar_location=None
    )
    plot.vbar(
        x="index", bottom=0, top=tax_var, width=0.7,
        source=ColumnDataSource(plot_data),
        fill_color="color", line_color="color",
        fill_alpha=0.55
    )
    # general formatting
    plot.yaxis.formatter = NumeralTickFormatter(format="($0.00 a)")
    plot.xaxis.formatter = NumeralTickFormatter(format="0")
    plot.xaxis.minor_tick_line_color = None
    plot.xgrid.grid_line_color = None

    return plot
