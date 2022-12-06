RESULTS_DIR=/data/jk232

rm tract_profiles.csv

{ head -n 1 ${RESULTS_DIR}/optic_bids_0_1/derivatives/afq/tract_profiles.csv & tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]/derivatives/afq/tract_profiles.csv; } > tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]two/derivatives/afq/tract_profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]/derivatives/subbundle/profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]two/derivatives/subbundle/profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]cst/derivatives/afq/tract_profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]cstwo/derivatives/afq/tract_profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]unc/derivatives/afq/tract_profiles.csv; } >> tract_profiles.csv
{ tail -q -n +2 ${RESULTS_DIR}/optic_bids_*_[[:digit:]]unctwo/derivatives/afq/tract_profiles.csv; } >> tract_profiles.csv
