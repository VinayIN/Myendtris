import time
import tobii_research as tr
import math
from win32api import GetSystemMetrics
from pylsl import StreamInfo, StreamOutlet

outlet = None
pixelsX = GetSystemMetrics(0)
pixelsY = GetSystemMetrics(1)
 

def find_all_trackers():
	eyetrackers = tr.find_all_eyetrackers()
	cnt = 1
	for eyetracker in eyetrackers:
		print("Eyetracker " + '{: d}'.format(cnt) + ":")
		print("\tAddress: " + eyetracker.address)
		print("\tModel: " + eyetracker.model)
		print("\tName (It's OK if this is empty): " + eyetracker.device_name)
		print("\tSerial number: " + eyetracker.serial_number)
	return eyetrackers

def gaze_data_callback(gaze_data):
	global outlet
	#print("getting data\n")
	sample = gaze_data['right_gaze_point_on_display_area']
	if math.isnan(sample[0]):
		sample_pixel = (0,0)
	else:
		sample_pixel = (sample[0] * pixelsX, sample[1] * pixelsY)
	outlet.push_sample(sample_pixel)
	print(sample_pixel)
	
def gaze_data(eyetracker):

	global outlet
	
	eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
	info = StreamInfo('tobii', 'Gaze', 2, 40, 'float32', eyetracker.serial_number)
	outlet = StreamOutlet(info)

	print("Press Enter to quit")
	x = raw_input();
	eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
	
eyetrackers = find_all_trackers()
gaze_data(eyetrackers[0])