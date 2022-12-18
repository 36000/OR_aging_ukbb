Most python files here use the python_analysis_docker.

First run:

compile_profiles.sh

correct_profiles.py

make_wide_profiles.py

Then run gen_pheno.py , modified to point to your UKBB csv file

For figure 1: first_paper_plots/pheno_histograms.py

For figure 2: see README in first_paper_plots/figure2

For figure 3: first_paper_plots/bundle_missingness.py
For the supporting ANOVA: first_paper_plots/missingness_anova.py

For profile plots (figures 4-8):

    First run first_paper_plots/wide_to_aci.py

    Then:

    first_paper_plots/general_profiles_plot.py ukbb_l_filt

    first_paper_plots/general_profiles_plot.py ukbb_r_filt

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt_cst

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt_unc

For profile plots only using subjects with all bundles found:

    First run first_paper_plots/wide_to_aci.py with only_all_bundles=True

    Then:

    first_paper_plots/general_profiles_plot.py ukbb_l_filt_oab

    first_paper_plots/general_profiles_plot.py ukbb_r_filt_oab

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt_oab

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt_cst_oab

    first_paper_plots/general_profiles_plot.py ukbb_lvr_filt_unc_oab

For figures 9,10 do: first_paper_plots/lme.py then first_paper_plots/lme2.py

    Both of these have a do_oab flag for only using subjects with all bundles found
    
    lme2.py uses the rpy_docker python installation.
