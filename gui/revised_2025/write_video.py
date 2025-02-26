import cv2
from rzd_detector.codemodules.stream.webrtc_receiver import WHEPClient, get_hsd_camera_url
import asyncio
from tqdm import tqdm
import time
from events import start, stop, pause

client = WHEPClient(get_hsd_camera_url("192.168.43.96"))
async def w(path:str, n: int, new_tread: True, client: WHEPClient):
    await client.connect()
    prev_time = 0
    frame_count = 0
    fps = 0
    for _ in range(60):
        await client.get_raw_frame()
        now = time.time()
        fps = 1 / (now - prev_time)
        prev_time = now
        frame_count += 1
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_obj = cv2.VideoWriter(path, fourcc, fps, (1920, 1080))
    for _ in tqdm(range(n)):
        frame = await client.get_raw_frame()
        video_obj.write(frame)
    video_obj.release()
    print("Операция завершена")
    await client.close()
    return video_obj, fps

if __name__ == "__main__":
    asyncio.run(w("./output32.mp4", 500, True, client))