import cv2
import numpy as np
img = np.zeros((480, 640, 3), np.uint8)
cv2.imshow("Video Stream", img)
cv2.waitKey(1)
cv2.destroyAllWindows()


import urllib.parse  
import asyncio  
import aiohttp  
import json  
import ssl  
from av import VideoFrame 
import logging 
import subprocess


from aiortc import RTCPeerConnection, RTCSessionDescription  # noqa: E402

HSD_IP = "192.168.43.96"

logger = logging.getLogger(__name__)


class WHEPClient:
    def __init__(self, url):
        """
        Инициализация клиента WHEP
        Args:
            url: базовый URL для подключения
        """
        self.base_url = url
        self.pc = None
        self.session_url = None
        self.track_video = None
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def __aenter__(self):
        if await self.connect():
            return self
        else:
            raise Exception("Failed to connect.")

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def get_ice_servers(self):
        """Получение ICE серверов"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.options(
                    self.base_url, ssl=self.ssl_context
                ) as response:
                    link_header = response.headers.get("Link", "")
                    if not link_header:
                        return []

                    ice_servers = []
                    for link in link_header.split(", "):
                        if 'rel="ice-server"' in link:
                            url = link[1 : link.find(">")]
                            server = {"urls": [url]}

                            if "username=" in link and "credential=" in link:
                                username = link[
                                    link.find('username="') + 10 : link.find(
                                        '"; credential'
                                    )
                                ]
                                credential = link[
                                    link.find('credential="') + 12 : link.find(
                                        '"; credential-type'
                                    )
                                ]
                                server |= {
                                    "username": json.loads(f'"{username}"'),
                                    "credential": json.loads(f'"{credential}"'),
                                    "credentialType": "password",
                                }

                            ice_servers.append(server)
                    return ice_servers
        except Exception as e:
            logger.warning(f"Failed to get ICE servers: {str(e)}")
            return []

    async def setup_peer_connection(self, ice_servers):
        """Настройка WebRTC peer connection"""
        config = {}
        if ice_servers:
            config["iceServers"] = ice_servers

        self.pc = RTCPeerConnection(configuration=config)
        logger.debug(f"ICE servers: {ice_servers}")
        logger.info(f"Creating PeerConnection with config: {config}")

        self.pc.addTransceiver("video", direction="recvonly")
        self.pc.addTransceiver("audio", direction="recvonly")

        @self.pc.on("track")
        async def on_track(track):
            print(f"Received track: {track.kind}")
            if track.kind == "video":
                self.track_video = track

        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            print(f"Connection state changed to: {self.pc.connectionState}")

        @self.pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print(f"ICE connection state changed to: {self.pc.iceConnectionState}")

        # Создание offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        return offer

    async def send_offer(self, offer):
        """Отправка offer на сервер"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers={"Content-Type": "application/sdp"},
                data=offer.sdp,
                ssl=self.ssl_context,
            ) as response:
                if response.status == 201:
                    self.session_url = str(
                        urllib.parse.urljoin(
                            self.base_url, response.headers["Location"]
                        )
                    )
                    answer_sdp = await response.text()
                    print(f"Received answer SDP: {answer_sdp[:100]}...")
                    return answer_sdp
                elif response.status == 404:
                    logger.error("Stream not found")
                else:
                    logger.error(f"Failed to send offer: {response.status}")

    async def connect(self):
        """Установка соединения"""
        try:
            # Получение ICE серверов
            ice_servers = await self.get_ice_servers()

            # Настройка peer connection и получение offer
            offer = await self.setup_peer_connection(ice_servers)
            logger.info(f"Created offer: {offer.sdp[:100]}...")

            # Отправка offer и получение answer
            answer_sdp = await self.send_offer(offer)

            # Установка remote description
            answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
            await self.pc.setRemoteDescription(answer)

            # Ждем установки соединения
            while self.pc.connectionState not in ["connected", "failed", "closed"]:
                await asyncio.sleep(0.1)

            if self.pc.connectionState != "connected":
                raise Exception(f"Failed to connect: {self.pc.connectionState}")
            else:
                print("Connection established successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to stream: {str(e)}")
            if self.pc:
                await self.pc.close()
            return False

    async def display_stream(self, client):
        """Отображение видеопотока через OpenCV"""
        cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
        while True:
            if self.track_video:
                try:
                    frame = await self.track_video.recv()
                    if isinstance(frame, VideoFrame):
                        # Конвертация кадра в формат OpenCV
                        img = frame.to_ndarray(format="bgr24")
                        frame = await client.get_raw_frame()
                        cv2.imshow("Video Stream", img)

                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                except Exception as e:
                    print(f"Frame processing error: {str(e)}")
                    break
            else:
                await asyncio.sleep(0.1)

        cv2.destroyAllWindows()

    async def stream_stream(self, client):
        """Отображение видеопотока через OpenCV"""
        # cv2.namedWindow("Video Stream", cv2.WINDOW_NORMAL)
        ffmpeg_process = open_ffmpeg_stream_process(self)
        while True:
            if self.track_video:
                try:
                    frame = await self.track_video.recv()
                    if isinstance(frame, VideoFrame):
                        img = frame.to_ndarray(format="bgr24")
                        ffmpeg_process.stdin.write(frame.astype(np.uint8).tobytes())
                        cv2.imshow("Video Stream", img)

                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break
                except Exception as e:
                    print(f"Frame processing error: {str(e)}")
                    break
            else:
                await asyncio.sleep(0.1)
        ffmpeg_process.stdin.close()
        ffmpeg_process.wait()
        cv2.destroyAllWindows()

    async def get_raw_frame(self):
        if self.track_video:
            try:
                frame = await self.track_video.recv()
                if isinstance(frame, VideoFrame):
                    return frame.to_ndarray(format="bgr24")
            except Exception as e:
                print(f"Frame processing error: {str(e)}")
        else:
            await asyncio.sleep(0.02)

    async def close(self):
        """Закрытие соединения"""
        if self.pc:
            await self.pc.close()
        if self.session_url:
            async with aiohttp.ClientSession() as session:
                await session.delete(self.session_url, ssl=self.ssl_context)


def get_hsd_camera_url(rpi_ip, stream_path="cam"):
    return f"http://{rpi_ip}:8889/{stream_path}/whep"


async def main():
    async with WHEPClient(get_hsd_camera_url(HSD_IP)) as client:
        await client.display_stream(client=client)

def open_ffmpeg_stream_process(self):
    args = (
        "ffmpeg -re -stream_loop -1 -f rawvideo -pix_fmt "
        "rgb24 -s 1920x1080 -i pipe:0 -pix_fmt yuv420p "
        "-f rtsp rtsp://rtsp_server:8554/stream"
    ).split()
    return subprocess.Popen(args, stdin=subprocess.PIPE)


if __name__ == "__main__":
    asyncio.run(main())
