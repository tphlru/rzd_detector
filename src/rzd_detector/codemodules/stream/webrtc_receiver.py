import cv2
import threading
import queue
import numpy as np


class VideoStream:
    def __init__(self, source=0, queue_size=5):
        # self.stream = cv2.VideoCapture(source)
        self.queue = queue.Queue(maxsize=queue_size)
        self.stopped = False

        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while not self.stopped:
            # ret, frame = self.stream.read()
            ret = True
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            if not ret:
                self.stop()
                return

            # Очищаем очередь, если она заполнена, чтобы не задерживать последние кадры
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
        # self.stream.release()


if __name__ == "__main__":
    vs = VideoStream()
    while True:
        frame = vs.get_frame()
        if frame is not None:
            cv2.imshow("Frame", frame)
        if cv2.waitKey(1) == 27:  # ESC
            break
    vs.stop()
    cv2.destroyAllWindows()
