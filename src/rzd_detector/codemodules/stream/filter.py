from webrtc_receiver import VideoStream
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from PIL import Image

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

    def __init__(self):
        self.video = VideoStream(queue_size=60)

    def get_embedding_and_face(self, image):

        faces, probs = mtcnn(image, return_prob=True)
        if faces is None or len(faces) == 0:
            return None, None

        embedding = resnet(faces[0].unsqueeze(0))
        return embedding, faces[0]
    
    def is_the_same(self, image, candidate_image, treshold: float):
        target_emb, target_face = self.get_embedding_and_face(image)
        if target_emb is None:
            return None

        candidate_emb, candidate_face = self.get_embedding_and_face(candidate_image)
        if candidate_emb is None:
            similarity = None
        else:
            similarity = torch.nn.functional.cosine_similarity(target_emb, candidate_emb).item()

        if similarity is None or similarity < treshold:
            return False
        else:
            return True
        
    def 