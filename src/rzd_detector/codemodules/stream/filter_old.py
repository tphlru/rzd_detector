import cv2
import numpy as np

cv2.imshow("frame", np.zeros((480, 640, 3), np.uint8))
cv2.waitKey(1)
cv2.destroyAllWindows()

from webrtc_receiver import WHEPClient, get_hsd_camera_url
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
import timeit
import asyncio
import json

# Initialize the MTCNN module for face detection and the InceptionResnetV1 module for face embedding.
mtcnn = MTCNN(image_size=160, keep_all=True)
resnet = InceptionResnetV1(pretrained="vggface2").eval()


class Frame:
    def __init__(self, image, human_id: int, frame_id: int, human_availability: bool):
        self.image = image
        self.human_id = human_id
        self.frame_id = frame_id
        self.human_availability = human_availability


class Buffer:
    def __init__(self, max_count: int, out_of_range_action: int, save_path: str):
        self.max_count = max_count
        self.out_of_range_action = out_of_range_action
        self.save_path = save_path
        if save_path[-1] != "/":
            save_path += "/"
        self.frames = []

    def write_json(self, frame: Frame):
        frame_params = {
            "id": frame.frame_id,
            "image_path": self.save_path + "images/" + frame.frame_id + "jpg",
            "human_id": frame.human_id,
            "human_availability": frame.human_availability,
        }
        with open(self.save_path + "labels/" + frame.frame_id + ".json", "w") as f:
            json.dumps(frame_params, f)

    def add(self, frame: Frame):
        self.frames.append(frame)
        if len(self.frames) > self.max_count:
            if self.action <= 0:
                out_of_range_frame = np.array(self.frames[0]).astype(np.uint8)
                self.frames = self.frames[1 : self.max_count + 1]
                cv2.imwrite(
                    self.save_path + "images/" + frame.frame_id + "jpg",
                    out_of_range_frame,
                )  # работать не будет, но нужно спросить Тимура в каком формате у нас изображения + выбрать формат
                self.write_json(frame)
            else:
                self.frames = self.frames[1 : self.max_count + 1]


class Filter:
    def __init__(self):
        self.buffer = Buffer(60, 0, "Scripts/test_files/common/buffer_out_files")
        self.frame = None
        self.fps = 30
        self.past_img = np.zeros((1920, 1080, 3), np.uint8)
        self.counter = 0
        self.frame_id = 0
        self.human_id = 0

    def _get_embedding_and_face(self, image):
        faces, probs = mtcnn(image, return_prob=True)
        if faces is None or len(faces) == 0:
            return None, None

        embedding = resnet(faces[0].unsqueeze(0))
        return embedding, faces[0]

    def _is_the_same(self, image, candidate_image, treshold: float):
        print(image.shape, candidate_image.shape)
        target_emb, target_face = self._get_embedding_and_face(image)
        if target_emb is None:
            return None

        candidate_emb, candidate_face = self._get_embedding_and_face(candidate_image)
        if candidate_emb is None:
            similarity = None
        else:
            similarity = torch.nn.functional.cosine_similarity(
                target_emb, candidate_emb
            ).item()

        if similarity is None or similarity < treshold:
            return False
        else:
            return True

    async def _get_frame(self, client: WHEPClient):
        self.counter += 1
        if self.counter % 3 == 0:
            img = await client.get_raw_frame()
            if self._get_embedding_and_face(img) == (None, None):
                self.frame = Frame(
                    img,
                    human_id=self.human_id,
                    frame_id=self.frame_id,
                    human_availability=False,
                )
            elif self._is_the_same(img, self.past_img, 0.7):
                self.frame = Frame(
                    img,
                    human_id=self.human_id,
                    frame_id=self.frame_id,
                    human_availability=True,
                )
            else:
                self.frame = None
                self.human_id += 1
            # self.buffer.add(self.frame)
            self.past_img = img
        self.frame_id += 1

    async def get_frame(self, client: WHEPClient):
        await asyncio.to_thread(self._get_frame(client))
        yield self.frame

    def get_fps(self):
        return self.fps


async def main():
    f = Filter()
    client = WHEPClient(get_hsd_camera_url("192.168.1.49"))
    await client.connect()
    while True:
        try:
            i = await f.get_frame(client).__anext__()
            cv2.imshow("frame", i.image)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                await client.close()
                cv2.destroyAllWindows()
        except StopIteration:
            print("stop iteration")
            await client.close()
            break


if __name__ == "__main__":
    asyncio.run(main())
