import cv2
import time
import threading
import sys,getopt

def ParseArgs(argv):
    
    parsed_arguments = dict()

    try:
        opts, args = getopt.getopt(argv, "hi:o:",["input=","output="])
    except getopt.GetoptError:
        print('Argument parse error')
        sys.exit(2)
    
    input_parsed = False
    for opt, arg in opts:
        if opt == '-h':
            print('capture.py [OPTIONS]\n\t -i | --input \t input stream url\n\t -i --output \t output video file')
            sys.exit(0)
        elif opt in ('-i', '--input'):
            parsed_arguments['input'] = arg
            input_parsed = True
        elif opt in ('-o','--output'):
            parsed_arguments['output'] = arg
    
    if not input_parsed:
        print("Input stream (--input) required")
        sys.exit(1)
    return parsed_arguments



class StopRecording:
    def __init__(self):
        self.stop = False

    def wait_for_key_press(self):
        input("Press Enter to stop recording...")
        self.stop = True

class MJPEGCapture:
    def __init__(self,arguments):
        self.codec = 'mp4v'
        self.default_fps = 30.0
        self.output_filename = 'output.mp4'

        ## Override default values if given
        for key, value in arguments.items():
            if key == 'input':
                self.stream_url = value
            elif key == 'output':
                self.output_filename = value



    def capture_stream(self): 

        cap = cv2.VideoCapture(self.stream_url)
        
        if not cap.isOpened():
            print("Error: Unable to open stream.")
            return
        

        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to read frame.")
            return
        
        frame_height, frame_width = frame.shape[:2]
        frame_size = (frame_width, frame_height)


        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0: 
            fps = default_fps
        
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        out = cv2.VideoWriter(self.output_filename, fourcc, fps, frame_size)
        
        print(f"Recording started. Frame size: {frame_size}, FPS: {fps}. Press 'Enter' to stop recording...")

        stop_recording = StopRecording()
        key_listener = threading.Thread(target=stop_recording.wait_for_key_press)
        key_listener.start()

        start_time = time.time()
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame.")
                break


            out.write(frame)
            frame_count += 1

            if stop_recording.stop:
                break

        if fps == self.default_fps:
            elapsed_time = time.time() - start_time
            effective_fps = frame_count / elapsed_time
            print(f"Effective FPS: {effective_fps}")
        

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print(f"Video saved as {output_filename}")


stream_url = 'https://rpi-cam.scanlab.gr/stream.mjpg'
output_filename = 'output.mp4'
arguments = ParseArgs(sys.argv[1:])
 
mjpeg_recorder = MJPEGCapture(arguments)
mjpeg_recorder.capture_stream()
