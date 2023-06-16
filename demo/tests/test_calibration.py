from meyendtris.modules.relaxation.calibration import StressCalibration
from meyendtris.modules.concentration.calibration import DistractionCalibration

def test_stress_calibration():
    alpha_calibration = StressCalibration()
    alpha_calibration.run()

def test_distraction_calibration():
    distraction_calibration = DistractionCalibration()
    distraction_calibration.run()