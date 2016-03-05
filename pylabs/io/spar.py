

def load(fpath):
    hdr = {}
    with open(fpath) as sparfile:
        lines = sparfile.readlines()
    for line in lines[25:]:
        line = line.strip()
        if line == '':
            continue
        if line[0] == '!':
            continue
        parts = line.split(':')
        key = parts[0].strip()
        val = parts[1].strip()
        if key not in keys.keys():
            raise ValueError('Unknown SPAR header field: '+key)
        fmt = keys[key]
        if fmt is 'int':
            val = int(val)
        if fmt is 'float':
            val = float(val)
        hdr[key] = val
    return hdr

keys = {
'echo_time': 'string',
 'spec_row_lower_val': 'string',
 'dim2_pnts': 'string',
 'image_plane_slice_thickness': 'string',
 'echo_nr': 'string',
 'phase_encoding_enable': 'string',
 'nr_phase_encoding_profiles': 'int',
 'si_ap_off_center' : 'float',
 'si_lr_off_center' : 'float',
 'si_cc_off_center' : 'float',
 'si_ap_off_angulation' : 'float',
 'si_lr_off_angulation' : 'float',
 'si_cc_off_angulation' : 'float',
 't0_kx_direction' : 'int',
 't0_ky_direction' : 'int',
 'nr_of_phase_encoding_profiles_ky' : 'int',
 'phase_encoding_direction' : 'string',
 'phase_encoding_fov' : 'int',
 'scan_date': 'string',
 'image_chemical_shift': 'string',
 'cc_angulation': 'string',
 'echo_acquisition': 'string',
 'cc_size': 'string',
 'dim3_ext': 'string',
 'cc_off_center': 'string',
 'resp_motion_comp_technique': 'string',
 't0_mu1_direction': 'string',
 'patient_birth_date': 'string',
 'dim1_direction': 'string',
 'scan_id': 'string',
 'rows': 'string',
 'dim3_low_val': 'string',
 'examination_name': 'string',
 'spec_row_extension': 'string',
 'lr_angulation': 'string',
 'dim2_t0_point': 'string',
 'ap_off_center': 'float',
 'patient_name': 'string',
 'dim3_pnts': 'string',
 'ap_angulation': 'string',
 'de_coupling': 'string',
 'spec_col_upper_val': 'string',
 'offset_frequency': 'string',
 'dim3_step': 'string',
 'repetition_time': 'string',
 'dim2_low_val': 'string',
 'synthesizer_frequency': 'string',
 'spec_data_type': 'string',
 'spec_col_extension': 'string',
 'patient_orientation': 'string',
 'dim3_t0_point': 'string',
 'spec_num_col': 'string',
 'dim2_direction': 'string',
 'samples': 'int',
 'volume_selection_enable': 'string',
 'Spec.image in plane transf': 'string',
 'TSI_factor': 'string',
 'num_dimensions': 'string',
 'spectrum_inversion_time': 'string',
 'spec_row_upper_val': 'string',
 'nr_of_slices_for_multislice': 'string',
 't1_measurement_enable': 'string',
 'nucleus': 'string',
 'sample_frequency': 'string',
 'dim1_ext': 'string',
 'dim2_step': 'string',
 't2_measurement_enable': 'string',
 'dim1_low_val': 'string',
 'lr_size': 'string',
 'dim1_t0_point': 'string',
 'spec_sample_extension': 'string',
 'placeholder2': 'string',
 'mix_number': 'string',
 'dim3_direction': 'string',
 'spec_num_row': 'string',
 'volume_selection_method': 'string',
 'spectrum_echo_time': 'string',
 'dim1_pnts': 'string',
 'ap_size': 'string',
 'dim1_step': 'string',
 'dim2_ext': 'string',
 'volumes': 'string',
 'slice_distance': 'string',
 'placeholder1': 'string',
 'equipment_sw_verions': 'string',
 'time_series_enable': 'string',
 'averages': 'string',
 'lr_off_center': 'string',
 'spec_col_lower_val': 'string',
 'patient_position':'string'
}




