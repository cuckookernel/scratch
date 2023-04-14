"""
Video downloader for daily motion videos
"""
import os
from pathlib import Path
import time
import requests


def main():
    # %%
    # TO GET the following url:
    #  1. go to daily motion website
    #  2. start watching a video
    #  3. Go to developer tools > Network tab
    #  4. Filter events through search box: m3u8
    #  5. Right-click on the one that has a short name and do copy URL
    # %%
    m3u_playlist_url = "https://proxy-036.dc3.dailymotion.com/sec(saQeXx3qXZg3T3rkC8HACLCec7UpPv4E_cl1mitDf3Lld4gU8P1NOMp24D8tBY3MD4zYa6qYMmWF_8X2cFbyI0mt3-prZCoKX7-XAu_bJzk)/video/489/883/396388984_mp4_h264_aac_4.m3u8"
    output_name = "da-ali-g-show.s03e02.mp4"
    m3u_playlist = get_playlist(m3u_playlist_url)
    print(f"playlist has: {len(m3u_playlist)}")
    domain = get_domain(m3u_playlist_url)
    chunks = []
    # %%
    for i, item in enumerate(m3u_playlist[509:]):
        url = domain + item
        print(item)
        resp = requests.get(url)

        print( f"{i + 1} / {len(m3u_playlist)} - status: ", resp.status_code)
        if resp.status_code != 200:
            raise RuntimeError("bad request")

        bytes_chunk = resp.content
        print( "length: ", len(bytes_chunk) )
        chunks.append(bytes_chunk)
        time.sleep(3)
    # %%

    all_bytes = b"".join(chunks)
    print(f"writing output ({len(all_bytes) / 1e6:.1f} MiB) to: {os.getcwd()}/{output_name}")
    Path(output_name).write_bytes(all_bytes)

    # %%


def get_domain(m3u_playlist: str):
    parts = m3u_playlist.split("/")
    print(parts)
    return "/".join(parts[:3])
# %%


def get_playlist(m3u_playlist_url: str):

    playlist_resp = requests.get(m3u_playlist_url)
    print(playlist_resp.status_code)
    playlist0 = playlist_resp.text.split("\n")

    playlist = [x for x in playlist0 if x != "" and not x.startswith("#")]
    return playlist
    # %%
