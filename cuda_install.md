#recipe to install cuda 7.5 on ubuntu 14.04 - assumes ~/Software is target directory

1. get cuda 7.5 ubuntu at https://developer.nvidia.com/cuda-75-downloads-archive amd save into ~/Software
2. cd ~/Software
3. sudo dpkg -i cuda-repo-ubuntu1404-7-5-local_7.5-18_amd64.deb
4. sudo apt-get update
5. sudo apt-get install cuda
6. then using http://www.r-tutor.com/gpu-computing/cuda-installation/cuda7.5-ubuntu
    as a guide - beware! it has errors in pathnames and export lib cmds
7. add the following to ~/.bashrc
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

