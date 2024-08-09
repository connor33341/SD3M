from gradio_client import Client
import http.server
import http.client
import http.cookies
import webbrowser
import socketserver
import urllib
import xmltodict
import io

DIRS = {
    "config": "private\\config",
    "public": "public"
}

with io.open(f"{DIRS["config"]}\\config.xml","r") as ConfigFile:
    ConfigFileContents = ConfigFile.read()
    ConfigFile.close()
    CONFIG = xmltodict.parse(ConfigFileContents)["Config"]

GradioClient = Client(CONFIG["Gradio"]["GradioApp"])

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == "/":
            self.path = "/index.html"

        Target = f"{DIRS["public"]}/{self.path}"
        print(f"[INFO]: Target: {Target}")
        TargetSplit = str(Target).split(".")
        print(f"[INFO]: Target Split: {TargetSplit}")
        FileType = TargetSplit[len(TargetSplit)-1]
        print(f"[INFO]: FileType: {FileType}")
        Found = False
        Contents = ""

        try:
            with io.open(Target,"r") as TargetFile:
                Contents = TargetFile.read()
                TargetFile.close()
                Found = True
        except Exception:
            print("[WARN]: Failed to locate file")
            Found = False

        if Found:
            self.send_response(200)
        else:
            self.send_response_only(404)

        if FileType == "html":
            self.send_header("Content-type","text/html")

        self.end_headers()
        self.wfile.write(Contents.encode())

    def do_POST(self):
        if self.path == "/generate/form":
            self.send_response(200)
            self.send_header("Content-type","image/webp")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            Prompt = parsed_data.get('prompt',[''])[0]
            NegativePrompt = parsed_data.get('negativeprompt',[''])[0]
            Seed = parsed_data.get('seed',[''])[0]
            Save = parsed_data.get('save',[''])[0]
            Prompt = str(Prompt)
            NegativePrompt = str(NegativePrompt)
            Seed = str(Seed)
            Save = str(Save)
            if Save == "on":
                Cookies = http.cookies.SimpleCookie()
                Cookies["Prompt"] = Prompt
                Cookies["NegativePrompt"] = NegativePrompt
                Cookies["Seed"] = Seed
                Cookies["Save"] = Save
            Result,Seed = GradioClient.predict(
                prompt=Prompt,
                negative_prompt=NegativePrompt,
                seed=0,
                randomize_seed=True, #if int(Seed) == 0 else False,
                width=int(CONFIG["AIConfig"]["Size"]["Width"]),
                height=int(CONFIG["AIConfig"]["Size"]["Height"]),
                guidance_scale=int(CONFIG["AIConfig"]["GS"]),
                num_inference_steps=int(CONFIG["AIConfig"]["IS"]),
                api_name=CONFIG["Gradio"]["Endpoint"]
            )
            self.end_headers()
            with io.open(Result,"rb") as File:
                Data = File.read()
                File.close()
            self.wfile.write(Data)
            print(Result)

with socketserver.TCPServer(("",int(CONFIG["WebServer"]["Port"])),Handler) as httpd:
    Url = "http://localhost:"+format(CONFIG["WebServer"]["Port"])
    print("Server Running at {}",Url)
    webbrowser.open(Url)
    try:
        httpd.serve_forever()
    except:
        httpd.server_close()