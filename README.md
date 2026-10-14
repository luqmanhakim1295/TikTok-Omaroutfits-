# TikTok-Omaroutfits-
## Auto edit video TikTok

`auto_edit.py` ambil semua video dalam satu folder dan hasilkan satu video TikTok:

- ambil part yang **clear sahaja** (frame blur / goyang dibuang)
- **crop dari paras mulut ke bawah** (muka atas mulut tak nampak)
- panjang video **15 saat ke bawah** (default 14s), saiz 1080x1920 (9:16)

```bash
pip install -r requirements.txt   # perlu ffmpeg juga
python3 auto_edit.py folder_video/ -o hasil.mp4
python3 auto_edit.py folder_video/ -o hasil.mp4 --music lagu.mp3   # letak lagu
python3 auto_edit.py folder_video/ -o hasil.mp4 --keep-audio       # kekal audio asal
```
