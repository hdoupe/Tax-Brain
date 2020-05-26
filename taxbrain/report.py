import behresp
import taxbrain
import taxcalc as tc
try:
    import cairocffi as cairo
except ImportError:
    import warnings
    warnings.warn("Cairo is not installed.")
    cairo = None
from pathlib import Path
from bokeh.io import export_png, export_svgs
from .report_utils import (form_intro, form_baseline_intro, write_text, date,
                           largest_tax_change, notable_changes,
                           behavioral_assumptions, consumption_assumptions,
                           policy_table, convert_table, growth_assumptions,
                           md_to_pdf)


CUR_PATH = Path(__file__).resolve().parent


def report(tb, name=None, change_threshold=0.05, description=None,
           outdir=None, author=None, css=None,
           verbose=False):
    """
    Create a PDF report based on TaxBrain results

    Parameters
    ----------
    tb: TaxBrain object
    name: Name you want used for the title of the report
    change_threshold: Percentage change (expressed as a decimal fraction) in
        an aggregate variable for it to be considered notable
    description: A description of the reform being run
    outdir: Output directory
    author: Person or persons to be listed as the author of the report
    css: Path to a CSS file used to format the final report
    verbose: boolean indicating whether or not to write progress as report is
        created
    """
    def format_table(df):
        """
        Apply formatting to a given table
        """
        for col in df.columns:
            df.update(
                df[col].astype(float).apply("{:,.2f}".format)
            )
        return df

    def export_plot(plot, graph):
        """
        Export a bokeh plot based on Cairo version
        """
        # export graph as a PNG or SVG depending on Cairo version is installed
        # higher quality SVG only works with Cairo version >= 1.15.4
        cairo_version = cairo.cairo_version()
        if cairo_version < 11504:
            filename = f"{graph}_graph.png"
            full_filename = Path(output_path, filename)
            export_png(plot, full_filename)
            print("For a higher quality SVG image file, install Cairo 1.15.4")
        else:
            filename = f"{graph}_graph.svg"
            full_filename = Path(output_path, filename)
            export_svgs(plot, filename=full_filename)

        return filename

    if not tb.has_run:
        tb.run()
    if not name:
        name = f"Policy Report-{date()}"
    if not outdir:
        outdir = "-".join(name)
    if author:
        author = f"Report Prepared by {author.title()}"
    # create directory to hold report contents
    output_path = Path(outdir)
    if not output_path.exists():
        output_path.mkdir()
    # dictionary to hold pieces of the final text
    text_args = {
        "start_year": tb.start_year,
        "end_year": tb.end_year,
        "title": name,
        "date": date(),
        "author": author
    }
    if verbose:
        print("Writing Introduction")
    # find policy areas used in the reform
    pol = tc.Policy()
    pol_meta = pol.metadata()
    pol_areas = set()
    for var in tb.params["policy"].keys():
        area = pol_meta[var]["section_1"]
        if area != "":
            pol_areas.add(area)
    pol_areas = list(pol_areas)
    # add policy areas to the intro text
    text_args["introduction"] = form_intro(pol_areas, description)
    # write final sentance of introduction
    current_law = tb.params["base_policy"]
    text_args["baseline_intro"] = form_baseline_intro(current_law)

    if verbose:
        print("Writing Summary")
    agg_table = tb.weighted_totals("combined")
    rev_change = agg_table.loc["Difference"].sum()
    rev_direction = "increase"
    if rev_change < 0:
        rev_direction = "decrease"
    text_args["rev_direction"] = rev_direction
    text_args["rev_change"] = f"{rev_change:,.0f}"

    # create differences table
    if verbose:
        print("Creating distribution table")
    diff_table = tb.differences_table(
        tb.start_year, "standard_income_bins", "combined"
    )
    # find which income bin sees the largest change in tax liability
    largest_change = largest_tax_change(diff_table)
    text_args["largest_change_group"] = largest_change[0]
    text_args["largest_change_str"] = largest_change[1]
    diff_table.columns = tc.DIFF_TABLE_LABELS
    # drop certain columns to save space
    drop_cols = [
        "Share of Overall Change", "Count with Tax Cut",
        "Count with Tax Increase"
    ]
    sub_diff_table = diff_table.drop(columns=drop_cols)

    # convert DataFrame to Markdown table
    diff_table.index.name = "_Income Bin_"
    # apply formatting
    diff_table = format_table(diff_table)
    diff_md = convert_table(sub_diff_table)
    text_args["differences_table"] = diff_md

    # aggregate results
    if verbose:
        print("Compiling aggregate results")
    # format aggregate table
    agg_table *= 1e-9
    agg_table = format_table(agg_table)
    agg_md = convert_table(agg_table)
    text_args["agg_table"] = agg_md

    # aggregate table by tax type
    tax_vars = ["iitax", "payrolltax", "combined"]
    agg_base = tb.multi_var_table(tax_vars, "base")
    agg_reform = tb.multi_var_table(tax_vars, "reform")
    agg_diff = agg_reform - agg_base
    agg_diff.index = ["Income Tax", "Payroll Tax", "Combined"]
    agg_diff *= 1e-9
    agg_diff = format_table(agg_diff)
    text_args["agg_tax_type"] = convert_table(agg_diff)

    # summary of policy changes
    text_args["reform_summary"] = policy_table(tb.params["policy"])

    # policy baseline
    if tb.params["base_policy"]:
        text_args["policy_baseline"] = policy_table(tb.params["base_policy"])
    else:
        text_args["policy_baseline"] = (
            f"This report is based on current law as of {date()}."
        )

    # notable changes
    if verbose:
        print("Finding notable changes")
    text_args["notable_changes"] = notable_changes(tb, change_threshold)

    # behavioral assumptions
    if verbose:
        print("Compiling assumptions")
    text_args["behavior_assumps"] = behavioral_assumptions(tb)
    # consumption asssumptions
    text_args["consump_assumps"] = consumption_assumptions(tb)
    # growth assumptions
    text_args["growth_assumps"] = growth_assumptions(tb)

    # determine model versions
    text_args["model_versions"] = [
        {"name": "Tax-Brain", "release": taxbrain.__version__},
        {"name": "Tax-Calculator", "release": tc.__version__},
        {"name": "Behavioral-Responses", "release": behresp.__version__}
    ]

    # create graphs
    if verbose:
        print("Creating graphs")
    dist_graph = taxbrain.distribution_plot(tb, tb.start_year, width=650)
    dist_graph.background_fill_color = None
    dist_graph.border_fill_color = None
    text_args["distribution_graph"] = export_plot(dist_graph, "dist")

    # differences graph
    diff_graph = taxbrain.differences_plot(tb, "combined", width=640)
    diff_graph.background_fill_color = None
    diff_graph.border_fill_color = None
    text_args["agg_graph"] = export_plot(diff_graph, "difference")

    # fill in the report template
    if verbose:
        print("Compiling report")
    template_path = Path(CUR_PATH, "report_files", "report_template.md")
    report_md = write_text(template_path, **text_args)

    # create PDF and HTML used to create the PDF
    wpdf, html = md_to_pdf(report_md, str(output_path), css)
    # write PDF, markdown files, HTML
    filename = name.replace(" ", "-")
    pdf_path = Path(output_path, f"{filename}.pdf")
    pdf_path.write_bytes(wpdf)
    md_path = Path(output_path, f"{filename}.md")
    md_path.write_text(report_md)
    html_path = Path(output_path, f"{filename}.html")
    html_path.write_text(html)
