from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

app = FastAPI(title="Audio API")

# 返回一个极小的有效 WAV 头 + 静音数据（1秒，8kHz，8-bit mono）
# 这是演示用途，体积非常小，但大多数浏览器可识别为音频。

def _tiny_wav_bytes():
    import struct
    nchannels = 1
    sampwidth = 1  # 8-bit
    framerate = 8000
    nframes = framerate  # 1秒
    comptype = b'NONE'
    compname = b'not compressed'

    # RIFF header
    # 'RIFF' + size + 'WAVE'
    data = bytearray()
    data.extend(b'RIFF')
    # placeholder for size (will fill later)
    data.extend(b'\x00\x00\x00\x00')
    data.extend(b'WAVE')

    # fmt chunk
    data.extend(b'fmt ')
    data.extend(struct.pack('<I', 16))  # chunk size
    data.extend(struct.pack('<H', 1))   # PCM format
    data.extend(struct.pack('<H', nchannels))
    data.extend(struct.pack('<I', framerate))
    byte_rate = framerate * nchannels * sampwidth
    data.extend(struct.pack('<I', byte_rate))
    block_align = nchannels * sampwidth
    data.extend(struct.pack('<H', block_align))
    data.extend(struct.pack('<H', sampwidth * 8))  # bits per sample

    # data chunk
    data.extend(b'data')
    data_bytes = bytes([128] * nframes)  # 8-bit unsigned silence
    data.extend(struct.pack('<I', len(data_bytes)))
    data.extend(data_bytes)

    # fill RIFF size
    riff_size = len(data) - 8
    data[4:8] = struct.pack('<I', riff_size)
    return bytes(data)

_DUMMY = _tiny_wav_bytes()

@app.get("/{filename}")
@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    if filename.endswith('.wav'):
        return Response(content=_DUMMY, media_type='audio/wav')
    # 其他格式简单返回同一数据，媒体类型设为 audio/mpeg 以兼容
    return Response(content=_DUMMY, media_type='audio/mpeg')
