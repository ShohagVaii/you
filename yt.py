import yt_dlp

# ডাউনলোড অপশন
ydl_opts = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # সেরা কোয়ালিটি
    'outtmpl': 'path/to/save/%(title)s.%(ext)s',  # ফাইলের নাম এবং পাথ
}

# ভিডিও URL
url = "https://www.youtube.com/watch?v=your_video_id"

# ডাউনলোড
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("ভিডিও ডাউনলোড সম্পন্ন!")
except Exception as e:
    print(f"একটি ত্রুটি ঘটেছে: {e}")
