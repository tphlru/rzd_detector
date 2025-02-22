from webrtc_receiver import WHEPClient, get_hsd_camera_url
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image
import time

# Initialize the MTCNN module for face detection and the InceptionResnetV1 module for face embedding.
mtcnn = MTCNN(image_size=160, keep_all=True)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

class Frame:

    def __init__(self, image, human_id: int, frame_id: int, human_availability: bool):
        self.image = image
        self.human_id = human_id
        self.frame_id = frame_id
        self.human_availability = human_availability

class Filter:

    def _get_embedding_and_face(self, image):

        faces, probs = mtcnn(image, return_prob=True)
        if faces is None or len(faces) == 0:
            return None, None

        embedding = resnet(faces[0].unsqueeze(0))
        return embedding, faces[0]
    
    def _is_the_same(self, image, candidate_image, treshold: float):
        target_emb, target_face = self._get_embedding_and_face(image)
        if target_emb is None:
            return None

        candidate_emb, candidate_face = self._get_embedding_and_face(candidate_image)
        if candidate_emb is None:
            similarity = None
        else:
            similarity = torch.nn.functional.cosine_similarity(target_emb, candidate_emb).item()

        if similarity is None or similarity < treshold:
            return False
        else:
            return True
        
    async def get_frame_and_fps(self):
        past_img = 0
        human_id = 0
        frame_id = 0
        times = []
        start_time = time.time()
        async with WHEPClient(get_hsd_camera_url("192.168.1.47")) as client:
            for i in await client.get_frame_yield:
                times.append(time.time()-start_time)
                times = time[1:11]
                duration = times[0] - times[9]
                self.fps = 10/duration
                img = i
                if self._get_embedding_and_face(img) == (None, None):
                    yield Frame(img, human_id=human_id, frame_id=frame_id, human_availability=False), fps
                if self._is_the_same(img, past_img, 0.7):
                    yield Frame(img, human_id=human_id, frame_id=frame_id, human_availability=True), fps
                else:
                    yield None
                
                frame_id += 1
    def get_fps(self):
        return self.fps