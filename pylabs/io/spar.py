

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
 'Spec.image in plane transf': 'string',
 'TSI_factor': 'int',
 'ap_angulation': 'float',
 'ap_off_center': 'float',
 'ap_size': 'float',
 'averages': 'int',
 'cc_angulation': 'float',
 'cc_off_center': 'float',
 'cc_size': 'float',
 'de_coupling': 'string',
 'dim1_direction': 'string',
 'dim1_ext': 'string',
 'dim1_low_val': 'float',
 'dim1_pnts': 'int',
 'dim1_step': 'float',
 'dim1_t0_point': 'string',
 'dim2_direction': 'string',
 'dim2_ext': 'string',
 'dim2_low_val': 'float',
 'dim2_pnts': 'int',
 'dim2_step': 'float',
 'dim2_t0_point': 'string',
 'dim3_direction': 'string',
 'dim3_ext': 'string',
 'dim3_low_val': 'float',
 'dim3_pnts': 'int',
 'dim3_step': 'float',
 'dim3_t0_point': 'string',
 'dim4_direction': 'string',
 'dim4_ext': 'string',
 'dim4_low_val': 'float',
 'dim4_pnts': 'int',
 'dim4_step': 'float',
 'dim4_t0_point': 'string',
 'echo_acquisition': 'string',
 'echo_nr': 'string',
 'echo_time': 'float',
 'equipment_sw_verions': 'string',
 'examination_name': 'string',
 'image_chemical_shift': 'string',
 'image_plane_slice_thickness': 'float',
 'lr_angulation': 'float',
 'lr_off_center': 'float',
 'lr_size': 'float',
 'mix_number': 'int',
 'nr_of_phase_encoding_profiles_ky': 'int',
 'nr_of_slices_for_multislice': 'int',
 'nr_phase_encoding_profiles': 'int',
 'nucleus': 'string',
 'num_dimensions': 'int',
 'offset_frequency': 'int',
 'patient_birth_date': 'string',
 'patient_name': 'string',
 'patient_orientation': 'string',
 'patient_position': 'string',
 'phase_encoding_direction': 'string',
 'phase_encoding_enable': 'string',
 'phase_encoding_fov': 'int',
 'placeholder1': 'string',
 'placeholder2': 'string',
 'repetition_time': 'float',
 'resp_motion_comp_technique': 'string',
 'rows': 'int',
 'sample_frequency': 'int',
 'samples': 'int',
 'scan_date': 'string',
 'scan_id': 'string',
 'si_ap_off_angulation': 'float',
 'si_ap_off_center': 'float',
 'si_cc_off_angulation': 'float',
 'si_cc_off_center': 'float',
 'si_lr_off_angulation': 'float',
 'si_lr_off_center': 'float',
 'slice_distance': 'float',
 'slice_thickness': 'float',
 'spec_col_extension': 'string',
 'spec_col_lower_val': 'float',
 'spec_col_upper_val': 'float',
 'spec_data_type': 'string',
 'spec_num_col': 'int',
 'spec_num_row': 'int',
 'spec_row_extension': 'string',
 'spec_row_lower_val': 'float',
 'spec_row_upper_val': 'float',
 'spec_sample_extension': 'string',
 'spectrum_echo_time': 'float',
 'spectrum_inversion_time': 'int',
 'synthesizer_frequency': 'int',
 't0_kx_direction': 'string',
 't0_ky_direction': 'string',
 't0_mu1_direction': 'string',
 't1_measurement_enable': 'string',
 't2_measurement_enable': 'string',
 'time_series_enable': 'string',
 'volume_selection_enable': 'string',
 'volume_selection_method': 'string',
 'volumes': 'int',
}
