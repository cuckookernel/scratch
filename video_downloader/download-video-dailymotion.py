"""Video downloader for daily motion videos
"""
import os
import time
from pathlib import Path

import requests

# %%


def main():
    # %%
    # TO GET the following url:
    #  1. go to daily motion website
    #  2. start watching a video
    #  3. Go to developer tools > Network tab
    #  4. Filter events through search box: m3u8
    #  5. Right-click on the one that has a short name and do copy URL
    # %%
    m3u_playlist_url = "https://proxy-033.dc3.dailymotion.com/sec(q7wHNBo9zV_qod5lIeRMXLeBXTDlObmQG_UoQ1BpYb7EXHxifBnkl5_2OsGruYi-ctsDWgW4IGfoZaV2f-bubY2q-4-kw2HqQum1NLz6P_o)/video/755/255/396552557_mp4_h264_aac_3.m3u8"
    output_path = Path("/home/teo/Downloads/Da-Ali-G-Show-from-dailymotion/da-ali-g-show.s03e04.mp4")
    m3u_playlist = get_playlist(m3u_playlist_url)
    print(f"playlist has: {len(m3u_playlist)}")
    # %%
    domain = get_domain(m3u_playlist_url)
    chunks = []

    for i, item in enumerate(m3u_playlist):
        url = domain + item
        print(item)
        resp = requests.get(url)

        print( f"{i + 1} / {len(m3u_playlist)} - status: ", resp.status_code)
        if resp.status_code != 200:
            raise RuntimeError("bad request")

        bytes_chunk = resp.content
        print( "length: ", len(bytes_chunk) )
        chunks.append(bytes_chunk)
        time.sleep(1)

    all_bytes = b"".join(chunks)
    print(f"writing output ({len(all_bytes) / 1e6:.1f} MiB) to: {os.getcwd()}/{output_name}")
    output_path.write_bytes(all_bytes)
    # %%


def get_domain(m3u_playlist: str):
    parts = m3u_playlist.split("/")
    print(parts)
    return "/".join(parts[:3])


def get_playlist(m3u_playlist_url: str):

    playlist_resp = requests.get(m3u_playlist_url)
    print(playlist_resp.status_code)
    playlist0 = playlist_resp.text.split("\n")

    playlist = [x for x in playlist0 if x != "" and not x.startswith("#")]
    return playlist
    # %%
