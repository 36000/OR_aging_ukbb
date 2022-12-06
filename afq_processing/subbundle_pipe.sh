if [ $# -lt 2 ]; 
   then 
   printf "Not enough arguments - %d\n" $# 
   exit 0 
   fi 
echo "Screen: $1"
echo "Iteration: $2"

# put in your data directories
if [[ "$2" == *"two" ]]; then
    DATA=/data/ukbiobank/blobs/mri2/data/
else
    DATA=/data/ukbiobank/blobs/mri/data/
fi
RESULTS_DIR=/data/jk232

# set up subject list and docker stuff
declare -a raw_subjects
find ${DATA}*_20250_2_0.zip  -printf "%f\n" | tail -n +$1${2:0:1}00 | head -n 100 | cut -c1-7 > sub_list_${1}_${2}
mapfile -t raw_subjects < sub_list_${1}_${2}
rm -f sub_list_${1}_${2}

# set up BIDS directory
for sub in ${raw_subjects[@]}; do
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/subbundle/sub-$sub/subbundle_inters
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/subbundle/sub-$sub/sls
    
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/ 
 
    unzip ${DATA}${sub}_20250_2_0.zip -d ${RESULTS_DIR}/${sub}
    cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/MNI_to_dti_FA_warp.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_MNI_to_dti_FA_warp.nii.gz
    cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/dti_FA_to_MNI.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_dti_FA_to_MNI.nii.gz
    cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/MNI_to_dti_FA_warp.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_dti_FA_to_MNI_backwarp.nii.gz
    rm -rf ${RESULTS_DIR}/${sub}
done
printf "{\"Name\": \"G_calcarine_subrois\", \"PipelineDescription\": {\"Name\": \"subbundle\"}, \"BIDSVersion\": \"1.4.0\"}" > ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/subbundle/dataset_description.json

for SUB in ${raw_subjects[@]}; do
    if test -f "${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-${SUB}/ses-01/sub-${SUB}_dwi_model-DKI_MD.nii.gz"; then
        mv ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-${SUB}/ses-01/* ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-${SUB}/
    fi
    if test -f "${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-${SUB}/sub-${SUB}_dwi_model-DKI_MD.nii.gz"; then
        echo "Running Subject: $SUB"
        docker run --rm -v ${RESULTS_DIR}:${RESULTS_DIR}:rw -v ${PWD}:/scripts:rw -it --entrypoint python 36000/pyafq:seg_by_dist scripts/test_subbundle.py $1 $2 $SUB "three"
    fi
done
docker run --rm -v ${RESULTS_DIR}:${RESULTS_DIR}:rw -v ${PWD}:/scripts:rw -it --entrypoint python 36000/pyafq:seg_by_dist scripts/viz_subbundle.py $1 $2 "${raw_subjects[@]}" 

