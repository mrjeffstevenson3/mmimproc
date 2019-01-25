%%% PARAMETERS %%%

SUBJ_NAME='test_subject'


%%% LOAD THE DATA %%%

% add BrainNet Viewer and Brain Connectivity Toolbox to the path
addpath(genpath('matlab/'))

% load csv and trim it
load TestMatrix_GraphAnalysis.csv
mat=TestMatrix_GraphAnalysis(:,1:74)


% this command will make symmetric a matrix called 'M'
mat=0.5.*(mat+mat')
mat
 


% read labels
labels=textread('brain_region_labels_penut74.csv','%s')


%%% PROCESS MATRIX %%%%

% replace NaN with zeros
mat(isnan(mat)) = 0 ;

% threshold at 10% sparsity, using BCT
mat_thr=threshold_proportional(mat,0.1)


%%% GET METRICS %%%

% get clustering coef
node_wise_cc=clustering_coef_wu(mat_thr)
global_cc=mean(node_wise_cc)

% get path lengths from inverted weighted matrix
path_lengths=distance_wei(1./mat_thr)

% get node-wise path lengths
node_wise_mean_path_lengths=zeros(1,length(path_lengths))
for i = 1:length(path_lengths)
   node_wise_mean_path_lengths(i)=mean(path_lengths(i,(path_lengths(i,:)~=0)&(isfinite(path_lengths(i,:)))))
end
global_charpath=nanmean(node_wise_mean_path_lengths)


%%% GENERATE OUTPUT %%%

% build output table
clustering_coefficient=[global_cc;node_wise_cc]
characteristic_path_length=[global_charpath;node_wise_mean_path_lengths']
myTable=table(clustering_coefficient, characteristic_path_length,'RowNames',[{'GLOBAL_AVERAGE'};labels])

% write to file
writetable(myTable,[SUBJ_NAME,'_network_measures.txt'],'WriteRowNames',true)

% write processed, thresholded matrix
writetable(table(mat_thr),[SUBJ_NAME,'_thresholded_connectivity_matrix.txt'],'Delimiter','tab','WriteVariableNames',false)

exit;

