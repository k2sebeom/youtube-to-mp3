import ssl
from pytube import YouTube
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import shutil
import tempfile
from uuid import uuid1


ssl._create_default_https_context = ssl._create_stdlib_context


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['youtube.com'],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    content = """
<head>
    <title>My Youtube to Mp3</title>
    <style>
        body {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-items: stretch;
        }

        .container {
            background-color: skyblue;
            padding: 10;
            width: 100vw;
        }

        input {
            width: 400;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Download Youtube Video as Audio File</h1>
        <div> 
            <input id="ylink" type="text">
            <button id="sbtn">Submit</button>
        </div>
        <div style="margin-top: 20">
            <div>
                <p style="display: inline">Save As: </p> <input style="display: inline" id="name" type="text"></input> <p style="display: inline"></p>
                <span id="ext">.mp3</span>
            </div>
            <div style="margin-top: 20"> 
                <a  download id="dbtn"></a>
                <button id="nbtn" style="visibility: hidden;">Convert Next</button>
            </div>
        </div>
    </div>
    <script>
        function reset() {
            vidName.value = "";
            ylink.value = "";
            nbtn.style.visibility = 'hidden';
            dbtn.innerText = '';
            dbtn.href = '';
            sbtn.disabled = false;
            dbtn.style.pointerEvents = 'none';
        }

        const sbtn = document.querySelector('#sbtn');
        const dbtn = document.querySelector('#dbtn');
        const nbtn = document.querySelector('#nbtn');
        const ylink = document.querySelector('#ylink');
        const vidName = document.querySelector('#name');
        const ext = document.querySelector('#ext');
        
        dbtn.onclick = () => {
            dbtn.download = vidName.value + '.mp3';
        }

        nbtn.onclick = reset;

        sbtn.onclick = async () => {
            dbtn.innerText = "Converting...";
            dbtn.style.pointerEvents = 'none'
            sbtn.disabled = true;
  
            const resp1 = await fetch(`/title?url=${ylink.value}`);
            const j = await resp1.json();

            if (!j.status) {
                alert("Youtube link is not valid!!");
                reset();
                return;
            }

            vidName.value = j.title;

            const resp2 = await fetch(`/download?url=${ylink.value}`);
            const b = await resp2.blob();
            const dlink = URL.createObjectURL(b);

            dbtn.href = dlink;
            dbtn.innerText = "Click to Download";
            sbtn.disabled = false;
            dbtn.style.pointerEvents = 'all';
            nbtn.style.visibility = 'visible';
        }
    </script>
</body>
    """
    return HTMLResponse(content=content)


@app.get("/title")
def title(url: str):
    try:
        yt = YouTube(url)
    except:
        return { "status": False, "title": "" }
    stream = yt.streams.filter(progressive=True, file_extension='mp4').get_lowest_resolution()
    return { "status": True, "title": stream.title }


def clean(dpath):
    shutil.rmtree(dpath)


@app.get("/download")
def download(url: str, background_tasks: BackgroundTasks):
    tempdir = tempfile.mkdtemp()
    background_tasks.add_task(clean, tempdir)
    try:
        yt = YouTube(url)
        fpath = yt.streams.filter(file_extension='mp4').get_audio_only().download(tempdir, filename=f'{uuid1()}.mp3')
        return FileResponse(path=fpath)
    except:
        return None
