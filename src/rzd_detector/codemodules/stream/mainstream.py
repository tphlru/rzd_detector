import cv2
import threading
import queue
import numpy as np

from webrtc_receiver import WHEPClient, get_hsd_camera_url


class VideoStream:
    def __init__(self, queue_size=60, rpi_ip="192.168.1.89"):
        # self.stream = cv2.VideoCapture(source)
        self.url = get_hsd_camera_url(rpi_ip)
        self.stream = WHEPClient(self.url)
        self.queue = queue.Queue(maxsize=queue_size)
        self.stopped = False

        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while not self.stopped:
            # ret, frame = self.stream.read()
            frame = self.stream.get_frame_yield()

            if self.queue.full():
                self.queue.get()

            self.queue.put(frame)

    def get_frame(self):
        if not self.queue.empty():
            return self.queue.get()
        return None  # Если кадров нет, возвращаем None

    def stop(self):
        self.stopped = True
        self.thread.join()
        self.stream.stop()


if __name__ == "__main__":
    vs = VideoStream()
    while True:
        frame = vs.get_frame()
        if frame is not None:
            print(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow("Frame", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break
    vs.stop()
    cv2.destroyAllWindows()
