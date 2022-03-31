import ssl
from pytube import YouTube
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from glob import glob
import shutil
import os
import tempfile


ssl._create_default_https_context = ssl._create_stdlib_context


app = FastAPI()

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
        <h1>Download Youtube Video</h1>
        <div> 
            <input id="ylink" type="text">
            <button id="sbtn">Submit</button>
        </div>
        <div style="margin-top: 20">
            <div>
                <p style="display: inline">Save As: </p> <input style="display: inline" id="name" type="text"></input> <p style="display: inline">.mp3</p>
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
        }

        const sbtn = document.querySelector('#sbtn');
        const dbtn = document.querySelector('#dbtn');
        const nbtn = document.querySelector('#nbtn');
        const ylink = document.querySelector('#ylink');
        const vidName = document.querySelector('#name');
        
        dbtn.onclick = () => {
            dbtn.download = vidName.value + '.mp3';
        }

        nbtn.onclick = reset;

        sbtn.onclick = async () => {
            dbtn.innerText = "Converting...";
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
        fpath = yt.streams.filter(progressive=True, file_extension='mp4').get_lowest_resolution().download(tempdir)
        os.system(f'ffmpeg -i "{fpath}" -f mp3 -y {tempdir}/out.mp3')
        return FileResponse(path=f'{tempdir}/out.mp3')
    except:
        return None
