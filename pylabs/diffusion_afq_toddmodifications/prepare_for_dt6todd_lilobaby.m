pe_mat = [0 1 0; 0 -1 0];
% First for 64 dir data
[AFQbase AFQdata AFQfunc AFQutil AFQdoc AFQgui] = AFQ_directories;
sub_dir = fullfile(AFQdata, 'sub-lilobaby');
params = dtiInitParams; % Set up parameters for controlling dtiInit
dtEddy = fullfile(sub_dir,'s0_d2000_add50.nii.gz'); % Path to the data
params.bvalsFile = fullfile(sub_dir,'bvals.csv'); % Path to bvals
params.bvecsFile = fullfile(sub_dir,'bvecs.csv'); % Path to the bvecs
params.eddyCorrect=-1; % This turns off eddy current and motion correction
%params.outDir = fullfile(basedir,'dti64');
params.rotateBvecsWithCanXform=1; % Phillips data requires this to be 1
params.phaseEncodeDir=1; % AP phase encode
params.clobber=1; % Overwrite anything previously done
params.fitMethod='rt'; % 'ls, or 'rt' for robust tensor fitting (longer)
t1 = fullfile(sub_dir,'b0.nii.gz'); % Path to the t1-weighted image
%this b0.nii.gz was created by extracting the
%non diffusion image from the dwi data set and rotating
%using Nudge to get the brain straight
% so for lilobabyG304, the head the very tilted and need to be straightened
% so the algorithm with take the newly straigtened b0 image and
% then automatically straighten and coregister and rotate the bvecs/tensors for all of the other DWI
% so that they are ready to go for AFQ runs
dt6FileName{1} = dtiInit(dtEddy,t1,params); % Run dtiInit to preprocess data
% I had to offset the MRI intensities by using fslmaths -add 50 option
% because the negative MRI intensities values were causing the
% rt fit method to crash
