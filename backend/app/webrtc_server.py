import asyncio

from aiortc import (
    RTCPeerConnection,
    VideoStreamTrack,
    RTCSessionDescription
)

from av import VideoFrame

from services.vision_service import (
    get_latest_processed_frame
)

pcs = set()


class CameraTrack(VideoStreamTrack):

    def __init__(self):
        super().__init__()
        self.last_frame = None

    async def recv(self):

        pts, time_base = await self.next_timestamp()

        frame = get_latest_processed_frame()

        if frame is None:

            await asyncio.sleep(0.01)

            if self.last_frame is None:
                return await self.recv()

            frame = self.last_frame

        self.last_frame = frame

        video_frame = VideoFrame.from_ndarray(
            frame,
            format="bgr24"
        )

        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame


async def offer(request):

    params = await request.json()

    pc = RTCPeerConnection()

    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_state_change():

        print("WebRTC State:", pc.connectionState)

        if pc.connectionState in [
            "failed",
            "closed",
            "disconnected"
        ]:

            await pc.close()
            pcs.discard(pc)

    # add processed camera stream
    pc.addTrack(CameraTrack())

    offer = RTCSessionDescription(
        sdp=params["sdp"],
        type=params["type"]
    )

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()

    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
    }