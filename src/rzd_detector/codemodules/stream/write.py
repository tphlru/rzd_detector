import cv2
from rzd_detector.codemodules.stream.webrtc_receiver import WHEPClient, get_hsd_camera_url
import asyncio
from tqdm import tqdm
import time
client = WHEPClient(get_hsd_camera_url("192.168.43.101"))

async def w(path:str):
    await client.connect()
    prev_time = 0
    frame_count = 0
    fps = 0
    for i in range(60):
        await client.get_raw_frame()
        now = time.time()
        fps = 1 / (now - prev_time)
        prev_time = now
        frame_count += 1
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (1920, 1080))
    for _ in tqdm(range(120)):
        frame = await client.get_raw_frame()
        if frame is None:
            print("Пустой кадр, возможно, соединение потеряно.")
            break
        out.write(frame)  
    out.release()
    print("Операция прервана пользователем")
    await client.close()

asyncio.run(w())
