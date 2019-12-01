import numpy as np


def data_processing(real_unknown, imaginary_unknown, real_cal, imaginary_cal):
    # function to find theta using x and y from device or calibration x and y from device
    # just pass in the real and imaginary component
    def find_angle(real, imaginary):
        pi = np.pi
        phase = 0
        theta = 0

        # phase calibration with arctangent function accounting for changes in quadrant
        if real != 0 and imaginary != 0:
            # positive and positive
            if real > 0 and imaginary > 0:  # 1st, per page 21 in AD5933 data sheet
                theta = np.arctan(imaginary / real)
                phase = (theta * 180) / pi
            # negative and positive
            if real < 0 and imaginary > 0:  # 2nd, per page 21 in AD5933 data sheet
                theta = pi + np.arctan(imaginary / real)
                phase = (theta * 180) / pi
            # negative and negative
            if real < 0 and imaginary < 0:  # 3rd, per page 21 in AD5933 data sheet
                theta = pi + np.arctan(imaginary / real)
                phase = (theta * 180) / pi
            # positive and negative
            if real > 0 and imaginary < 0:  # 4th, per page 21 in AD5933 data sheet
                theta = 2 * (pi) + np.arctan(imaginary / real)
                phase = (theta * 180) / pi

        # handle arctan function if 'real' aka 'x' component is zero
        if real == 0:
            if real == 0 and imaginary > 0:  # 1st, per page 21 in AD5933 data sheet
                theta = pi / 2
                phase = (theta * 180) / pi
                print('1 and 2')
            if real == 0 and imaginary < 0:  # 4th, per page 21 in AD5933 data sheet
                theta = (3 * pi) / 2
                phase = (theta * 180) / pi
                print('3 and 4')

        # handle arctan function if 'imaginary' aka 'y' component is zero
        if imaginary == 0:
            if real > 0 and imaginary == 0:  # 1st, per page 21 in AD5933 data sheet
                theta = 0
                phase = (theta * 180) / pi
                print('1 and 4')
            if real < 0 and imaginary == 0:  # 4th, per page 21 in AD5933 data sheet
                theta = pi
                phase = (theta * 180) / pi
                print('2 and 3')
        return theta

    # magnitude calculation with gain factor from calibration resistor
    magnitude_cal = np.sqrt((real_cal ** 2) + (imaginary_cal ** 2))

    if magnitude_cal != 0:
        gain_factor = (1 / 1) / magnitude_cal
    else:
        gain_factor = (1 / 1) / 1

    if real_unknown != 0:
        magnitude = np.sqrt((real_unknown ** 2) + (imaginary_unknown ** 2))
        impedance = 1 / (gain_factor * magnitude)
    else:
        magnitude = 1
        impedance = 1

    theta = find_angle(real_unknown, imaginary_unknown)

    # adjusting vector projection to adjust for phase angle and magnitude
    z_real = np.abs(impedance) * np.cos(theta)
    z_imaginary = np.abs(impedance) * np.sin(theta)

    string_to_print = f'calibrated impedace magnitude: {impedance}\ntheta: {theta}\nz_real: {z_real}\nz_imaginary: {z_imaginary}'

    print(string_to_print)


