# we break up subjects into groups of 100,
# put them into their own BIDS directory,
# and run pyAFQ. Each iteration of this script processes 100 subjects.
# Screen / iteration determine which 100 subjects to run.
# We also encode whether to run CST/UNC instead of OR in the iteration parameter
# For example, `sh afq_processing_pipe.sh 0 0unc`
# would process the UNC for the first 100 subjects
if [ $# -lt 2 ]; 
   then 
   printf "Not enough arguments - %d\n" $# 
   exit 0 
   fi 
echo "Screen: $1"
echo "Iteration: $2"

declare -a gpu_num=1
RESULTS_DIR=/data/jk232

# determine data location, other parameters
# ALGO is a pyafq docker image
# DATA is your data location
if [[ "$2" == *"cst" ]]; then
    cp ${RESULTS_DIR}/config_cst.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all #get_tract_profiles
    HALF=true
elif [[ "$2" == *"cstwo" ]]; then
    cp ${RESULTS_DIR}/config_cst.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri2/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all #get_tract_profiles
    HALF=true
elif [[ "$2" == *"unc" ]]; then
    cp ${RESULTS_DIR}/config_unc.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all #get_tract_profiles
    HALF=false
elif [[ "$2" == *"unctwo" ]]; then
    cp ${RESULTS_DIR}/config_unc.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri2/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all #get_tract_profiles
    HALF=false
elif [[ "$2" == *"two" ]]; then
    cp ${RESULTS_DIR}/config.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri2/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all #get_tract_profiles
    HALF=true
else
    cp ${RESULTS_DIR}/config.toml ${RESULTS_DIR}/config_$1_$2.toml
    N_SEEDS=4
    DATA=/data/ukbiobank/blobs/mri/data/
    ALGO=ghcr.io/nrdg/pyafq:af72bdaf576e0c0c58e856a5a25506dc984868c5
    CALL1=export_seed_mask
    CALL2=export_all
    HALF=true
fi

# set up subject list and docker stuff
# note our subjects are in the form ${DATA}*_20250_2_0.zip
# this will need to be modified to however your data is structured.
# the point is to get a list of subjects and put them in a BIDs directory
declare -a raw_subjects
find ${DATA}*_20250_2_0.zip  -printf "%f\n" | tail -n +$1${2:0:1}00 | head -n 100 | cut -c1-7 > sub_list_dir/sub_list_${1}_${2}
mapfile -t raw_subjects < sub_list_dir/sub_list_${1}_${2}
rm -f sub_list_dir/sub_list_${1}_${2}
echo "bids_path = 'output/optic_bids_$1_$2'" >> ${RESULTS_DIR}/config_$1_$2.toml
docker run -td --name optic_pipe_$1_$2 -v ${RESULTS_DIR}:/output:rw ${ALGO}

# set up BIDS directory
for sub in ${raw_subjects[@]}; do
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc/sub-$sub/
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/sub-$sub/
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-$sub/
    mkdir -p ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/
done
printf "{\"Name\": \"UK_Biobank\", \"BIDSVersion\": \"1.4.0\"}" > ${RESULTS_DIR}/optic_bids_$1_$2/dataset_description.json
printf "{\"Name\": \"UK_Biobank\", \"PipelineDescription\": {\"Name\": \"preproc\"}, \"BIDSVersion\": \"1.4.0\"}" > ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc/dataset_description.json
printf "{\"Name\": \"UK_Biobank\", \"PipelineDescription\": {\"Name\": \"gpu\"}, \"BIDSVersion\": \"1.4.0\"}" > ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/dataset_description.json
printf "{\"Name\": \"UK_Biobank\", \"PipelineDescription\": {\"Name\": \"TBSS\"}, \"BIDSVersion\": \"1.4.0\"}" > ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/dataset_description.json

# move in the data
declare -a subjects
for sub in ${raw_subjects[@]}; do
    test -f "${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-${sub}/sub-${sub}_dwi_dti_FA_to_MNI.nii.gz"; then
        echo "$sub data already in BIDS."
        subjects+=(${sub})
    else
        unzip ${DATA}${sub}_20250_2_0.zip -d ${RESULTS_DIR}/${sub}
        if test -f "${RESULTS_DIR}/$sub/dMRI/TBSS/FA/dti_FA_to_MNI.nii.gz"; then
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI/data_ud.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc/sub-$sub/sub-${sub}_dwi.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI/bvals ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc/sub-$sub/sub-${sub}_dwi.bval
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI/bvecs ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc/sub-$sub/sub-${sub}_dwi.bvec
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI/dti_FA.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-$sub/sub-${sub}_dwi_model-DTI_FA.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI/dti_MD.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-$sub/sub-${sub}_dwi_model-DTI_MD.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/dMRI.bedpostX/nodif_brain_mask.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-$sub/sub-${sub}_dwi_brain_mask.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/MNI_to_dti_FA_warp.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_MNI_to_dti_FA_warp.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/dti_FA_to_MNI.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_dti_FA_to_MNI.nii.gz
            cp ${RESULTS_DIR}/$sub/dMRI/TBSS/FA/MNI_to_dti_FA_warp.nii.gz ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/TBSS/sub-$sub/sub-${sub}_dwi_dti_FA_to_MNI_backwarp.nii.gz
            subjects+=(${sub})
        else
            echo "$sub has incompatible data; skipped"
            touch ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-$sub/data_failure
        fi
        rm -rf ${RESULTS_DIR}/${sub}
    fi
done

exit

# generate ROIs
for sub in ${subjects[@]}; do
    touch ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/sub-$sub/sub-${sub}_filler_gputractography.trk
done
docker exec -it optic_pipe_$1_$2 pyAFQ output/config_$1_$2.toml -v --call ${CALL1}
for sub in ${subjects[@]}; do
    rm ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/sub-$sub/sub-${sub}_filler_gputractography.trk
done

#perform tractography
for sub in ${subjects[@]}; do
    if ${HALF}; then
        TRK_MASK="/opt/exec/output/optic_bids_$1_$2/derivatives/afq/sub-${sub}/sub-${sub}_dwi_brain_mask_halved.nii.gz"
        if [ ! -f ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/afq/sub-${sub}/sub-${sub}_dwi_brain_mask_halved.nii.gz ]; then
            docker exec -it optic_pipe_$1_$2 python output/cut_mask_in_half.py ${sub} $1 $2 "keepback"
        fi
    else
        TRK_MASK="/opt/exec/output/optic_bids_$1_$2/derivatives/afq/sub-${sub}/sub-${sub}_dwi_brain_mask.nii.gz"
    fi
    while [ ! -f ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/sub-${sub}/sub-${sub}_gputractography.trk ] ; do
        mkdir -p ${RESULTS_DIR}/hardi_gpu_${sub}
        nvidia-docker run --rm -v ${RESULTS_DIR}:/opt/exec/output:rw -it docker.pkg.github.com/dipy/gpustreamlines/gpustreamlines:latest /bin/bash -c "export CUDA_DEVICE_ORDER=PCI_BUS_ID; export CUDA_VISIBLE_DEVICES=${gpu_num}; python run_dipy_gpu.py /opt/exec/output/optic_bids_$1_$2/derivatives/preproc/sub-${sub}/sub-${sub}_dwi.nii.gz /opt/exec/output/optic_bids_$1_$2/derivatives/preproc/sub-${sub}/sub-${sub}_dwi.bval /opt/exec/output/optic_bids_$1_$2/derivatives/preproc/sub-${sub}/sub-${sub}_dwi.bvec ${TRK_MASK} --roi_nifti /opt/exec/output/optic_bids_$1_$2/derivatives/afq/sub-${sub}/sub-${sub}_dwi_seed_mask.nii.gz --sampling-density ${N_SEEDS} --chunk-size 100000 --ngpus 1 --output-prefix /opt/exec/output/hardi_gpu_${sub}/o --use-fast-write"
        nvidia-docker run --rm -v ${RESULTS_DIR}:/opt/exec/output:rw -it docker.pkg.github.com/dipy/gpustreamlines/gpustreamlines:latest ./merge_trk.sh -o /opt/exec/output/optic_bids_$1_$2/derivatives/gpu/sub-${sub}/sub-${sub}_gputractography.trk /opt/exec/output/hardi_gpu_${sub}/o*
        find ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/gpu/sub-${sub}/sub-${sub}_gputractography.trk -type f -size -1024k | xargs rm
        rm -rf ${RESULTS_DIR}/hardi_gpu_${sub}
    done
done

# finish tractometry
docker exec -it optic_pipe_$1_$2 pyAFQ output/config_$1_$2.toml --call ${CALL2}

docker kill optic_pipe_$1_$2
docker rm optic_pipe_$1_$2

# delete these to save space
rm -rf ${RESULTS_DIR}/optic_bids_$1_$2/derivatives/preproc

