import ssl
from pytube import YouTube
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from glob import glob
import os


ssl._create_default_https_context = ssl._create_stdlib_context


app = FastAPI()

@app.get("/")
async def main():
    content = """
<body>
    <script src="https://code.jquery.com/jquery-1.11.2.min.js"></script>
    <div>
        <div>
            <h1>Download Youtube Video</h1>
            <input id="ylink" type="text">
            <button id="sbtn">Submit</button>
        </div>
        <div style="margin-top: 20">
            <div>
                <p style="display: inline">Save As: </p> <input style="display: inline" id="name" type="text"></input> <p style="display: inline">.mp3</p>
            </div>
            <div style="margin-top: 20"> 
                <a  download id="dbtn"></a>
            </div>
        </div>
    </div>
    <script>
        const sbtn = document.querySelector('#sbtn');
        const dbtn = document.querySelector('#dbtn');
        const ylink = document.querySelector('#ylink');
        const vidName = document.querySelector('#name');
        
        dbtn.onclick = () => {
            dbtn.download = vidName.value;
        }

        sbtn.onclick = async () => {
            dbtn.innerText = "Converting...";
            sbtn.disabled = true;

            const resp1 = await fetch(`/title?url=${ylink.value}`);
            const j = await resp1.json();
            vidName.value = j.title;

            const resp2 = await fetch(`/download?url=${ylink.value}`);
            const b = await resp2.blob();
            const dlink = URL.createObjectURL(b);

            dbtn.href = dlink;
            dbtn.innerText = "Click to Download";
            sbtn.disabled = false;
        }
    </script>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/title")
def title(url: str):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension='mp4').get_lowest_resolution()
    print(stream.title)
    return { "title": stream.title }

@app.get("/download")
def download(url: str):
    for fpath in glob('./tmp/*'):
        os.remove(fpath)
    yt = YouTube(url)
    yt.streams.filter(progressive=True, file_extension='mp4').get_lowest_resolution().download('./tmp')
    fpath = glob('./tmp/*')[0]
    os.system(f'ffmpeg -i "{fpath}" -f mp3 -y tmp/out.mp3')
    return FileResponse(path='tmp/out.mp3')
