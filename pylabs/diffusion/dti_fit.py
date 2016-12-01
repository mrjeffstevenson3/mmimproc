import collections


class DTIFitCmds(collections.MutableMapping):
    '''
    Mapping that works like both a dict and a mutable object, i.e.
    d = D(foo='bar')
    and
    d.foo returns 'bar'
    '''

    def __init__(self, dwif=None, mask_fname=None, sigma=None, *args, **kwargs):
        '''Use the object dict'''
        self.dwif = dwif
        self.mask_fname = mask_fname
        self.sigma = sigma
        if len(args) == len(kwargs) == 0:
            #set up dti fit methods to loop over
            self.__dict__ = {'cam_part1': {'RESTORE': ['modelfit -inputfile '+str(self.dwif)+'.nii -schemefile ../scheme.txt -model ldt_wtd -noisemap noise_map.Bdouble -bgmask '+
                                                        str(self.mask_fname)+' -outputfile linear_tensor.Bfloat',   'cat noise_map.Bdouble noise_map.Bdouble | voxel2image -inputdatatype double -header '+
                                                        str(self.mask_fname)+' -outputroot noise_map', 'fslmaths noise_map -sqrt sigma_map', 'fslstats sigma_map -P 50'],
                                           'OLS': ['pass'],
                                           'WLS': ['pass']
                                           },
                             'cam_part2': {'RESTORE': [
                                                        ],
                                            'OLS': ['pass'],
                                            'WLS': ['pass']
                                            },
                         }
        else:
            #feed whole shebang 1st time
            self.__dict__.update(*args, **kwargs)

    # The next five methods are requirements of the ABC.
    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    # The final two methods aren't required, but nice for demo purposes:
    def __str__(self):
        '''returns simple dict representation of the mapping'''
        return str(self.__dict__)

    def __repr__(self):
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}, DTIFitCmds({})'.format(super(DTIFitCmds, self).__repr__(),
                                  self.__dict__)
