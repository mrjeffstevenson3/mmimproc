**recipe to install cuda 7.5 - assumes ~/Software is target directory.**
on ubuntu 14.04 use std repos, 16.04 has hack at `https://www.pugetsystems.com/labs/hpc/Install-Ubuntu-16-04-or-14-04-and-CUDA-8-and-7-5-for-NVIDIA-Pascal-GPU-825/`**
if you need the make/model of your Graphics card do one of either:
`sudo lshw -C video` or `sudo lspci | grep -i nvidia` then check that you have the appropriate driver installed by going to `http://www.nvidia.com/Download/index.aspx` and filling in info. download run file if on 16.04 until stock cuda7.5 available.


#recover from bad install: deinstall everything
sudo apt-get remove --purge nvidia*
cd ~/Software
sudo ./NVIDIA-Linux-x86_64-367.57.run --uninstall
sudo ./cuda_7.5.18_linux.run --uninstall --silent

#then start with drivers 
sudo apt-get install nvidia-367 gcc-4.9 gcc-5
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 20
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 10
#use this to configure which version of gcc before pycuda making gcc 4.9 default
sudo update-alternatives --config gcc
pip install pycuda
#then run test of eddy_cuda7.5
toddr@uhora:/mnt/users/js/bbc/cuda_test$ eddy_cuda7.5 --acqp=acq_params.txt --bvals=sub-bbc253_ses-1_dti_15dir_b1000_1.bvals --bvecs=sub-bbc253_ses-1_dti_15dir_b1000_1.bvecs --imain=sub-bbc253_ses-1_dti_15dir_b1000_1.nii --index=index.txt --mask=sub-bbc253_ses-1_dti_15dir_b1000_1_S0_mask.nii --out=sub-bbc253_ses-1_dti_15dir_b1000_1_eddy_corrected_repol_std2_test --repol --ol_sqr --slm=linear --ol_nstd=2 --niter=9 --fwhm=20,5,0,0,0,0,0,0,0
Entering EddyGpuUtils::LoadPredictionMaker

...................Allocated GPU # 0...................
thrust::system_error thrown in CudaVolume::common_assignment_from_newimage_vol after resize() with message: function_attributes(): after cudaFuncGetAttributes: invalid device function
terminate called after throwing an instance of 'thrust::system::system_error'
  what():  function_attributes(): after cudaFuncGetAttributes: invalid device function
Aborted (core dumped)












1. get cuda 7.5 ubuntu at `https://developer.nvidia.com/cuda-75-downloads-archive` amd save run file if 16.04 or .deb into ~/Software. note for ubuntu 16.04 cuda 7.5 binaries not available cuda 8.0 FSL tests currently fail. stay tuned
2. `cd ~/Software`
3. `sudo dpkg -i cuda-repo-ubuntu1404-7-5-local_7.5-18_amd64.deb`
4. sudo apt-get update
5. sudo apt-get install cuda
6. then using http://www.r-tutor.com/gpu-computing/cuda-installation/cuda7.5-ubuntu
    as a guide - beware! it has errors in pathnames and export lib cmds
7. add the following to ~/.bashrc. for 16.04 change lines 1 & 2 to /usr/local/cuda-8.0
    #cuda paths
    export CUDA_ROOT=/usr/local/cuda-7.5
    export CUDA_HOME=/usr/local/cuda-7.5
    export CUDA_INC_DIR=${CUDA_HOME}/include
    export LD_LIBRARY_PATH=${CUDA_HOME}/lib64:$LD_LIBRARY_PATH
    export PATH=$CUDA_HOME:${CUDA_HOME}/bin:$PATH
    echo "CUDA PATH enabled: $CUDA_ROOT"
    echo "PATH env ="$PATH
8. open new shell or source ~/.bashrc
9. cuda-install-samples-7.5.sh  ~/Software
10. cd ~/Software/NVIDIA_CUDA-7.5_Samples/1_Utilities/deviceQuery
11. make
12. ./deviceQuery
13. #should see following:
        toddr@redshirt:~/Software/NVIDIA_CUDA-7.5_Samples/1_Utilities/deviceQuery$ ./deviceQuery
        ./deviceQuery Starting...
        
         CUDA Device Query (Runtime API) version (CUDART static linking)
        
        Detected 1 CUDA Capable device(s)
        
        Device 0: "GeForce GTX TITAN Black"
          CUDA Driver Version / Runtime Version          7.5 / 7.5
          CUDA Capability Major/Minor version number:    3.5
          Total amount of global memory:                 6143 MBytes (6441730048 bytes)
          (15) Multiprocessors, (192) CUDA Cores/MP:     2880 CUDA Cores
          GPU Max Clock rate:                            980 MHz (0.98 GHz)
          Memory Clock rate:                             3500 Mhz
          Memory Bus Width:                              384-bit
          L2 Cache Size:                                 1572864 bytes
          Maximum Texture Dimension Size (x,y,z)         1D=(65536), 2D=(65536, 65536), 3D=(4096, 4096, 4096)
          Maximum Layered 1D Texture Size, (num) layers  1D=(16384), 2048 layers
          Maximum Layered 2D Texture Size, (num) layers  2D=(16384, 16384), 2048 layers
          Total amount of constant memory:               65536 bytes
          Total amount of shared memory per block:       49152 bytes
          Total number of registers available per block: 65536
          Warp size:                                     32
          Maximum number of threads per multiprocessor:  2048
          Maximum number of threads per block:           1024
          Max dimension size of a thread block (x,y,z): (1024, 1024, 64)
          Max dimension size of a grid size    (x,y,z): (2147483647, 65535, 65535)
          Maximum memory pitch:                          2147483647 bytes
          Texture alignment:                             512 bytes
          Concurrent copy and kernel execution:          Yes with 1 copy engine(s)
          Run time limit on kernels:                     Yes
          Integrated GPU sharing Host Memory:            No
          Support host page-locked memory mapping:       Yes
          Alignment requirement for Surfaces:            Yes
          Device has ECC support:                        Disabled
          Device supports Unified Addressing (UVA):      Yes
          Device PCI Domain ID / Bus ID / location ID:   0 / 130 / 0
          Compute Mode:
             < Default (multiple host threads can use ::cudaSetDevice() with device simultaneously) >
        
        deviceQuery, CUDA Driver = CUDART, CUDA Driver Version = 7.5, CUDA Runtime Version = 7.5, NumDevs = 1, Device0 = GeForce GTX TITAN Black
        Result = PASS

