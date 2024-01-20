import socket
from flask import Flask, render_template, Response, redirect, request, session
from flask_session import Session
import subprocess
import json
import piir


app = Flask(__name__)


def check_if_user_has_already_logged_in():
    if not session.get("username"):
        return False
    if session.get("username") in app.user_config["valid_users"]:
        if session.get("password") == app.user_config["valid_users"][session.get("username")]:
            return True


@app.route("/")
def root():
    if check_if_user_has_already_logged_in():
        return redirect("/remote_screen")
    else:
        return redirect('/login')


@app.route("/login", methods=["POST", "GET"])
def login():
    error_msg = ""
    if request.method == "POST":
        input_username = request.form.get("username")
        input_password = request.form.get("password")
        if input_username in app.user_config["valid_users"]:
            if input_password == app.user_config["valid_users"][input_username]:
                session["username"] = input_username
                session["password"] = input_password
                return redirect("/")
        error_msg = "Wrong username or password"
    return render_template("login.html", error_msg=error_msg)


@app.route("/remote_action", methods=["POST"])
def remote_action():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    for key, value in request.form.items():
        action = key.replace("button_", "")  # Remove button_ from key to get action only
        print(f"Pressing: {action}")
        app.remote.send(action)
    return "", 204


@app.route("/remote_screen")
def remote_screen():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    return render_template("RemoteScreen.html")


def gen(s):
    while True:
        data, address = s.recvfrom(100_000_000)
        yield data


@app.route("/remote_video")
def remote_video():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("127.0.0.1", app.gstreamer_port))
    return Response(gen(s), mimetype=f'multipart/x-mixed-replace; boundary={app.mjpeg_boundary}')


def find_open_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def setup_video_streaming():
    print("Opening gstreamer pipeline")

    gstreamer_cmd = "gst-launch-1.0"
    webcam_option = ["libcamerasrc"]

    gstreamer_port = find_open_port()
    mjpeg_boundary = "video_boundary"
    print(f"{gstreamer_port=}")

    gstreamer_crop = []
    if "video_options" in app.user_config:
        if "crop" in app.user_config["video_options"]:
            left = app.user_config["video_options"]["crop"]["left"]
            right = app.user_config["video_options"]["crop"]["right"]
            top = app.user_config["video_options"]["crop"]["top"]
            bottom = app.user_config["video_options"]["crop"]["bottom"]
            gstreamer_crop = ["!", "videocrop", f"left={left}", f"right={right}", f"top={top}", f"bottom={bottom}"]

    cmd = [
        gstreamer_cmd,
        "-v",
        *webcam_option,
        "!", "videoconvert",
        *gstreamer_crop,
        "!", "jpegenc", "quality=50",
        "!", "multipartmux", f"boundary={mjpeg_boundary}",
        "!", "udpsink", "host=127.0.0.1", f"port={gstreamer_port}",
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    app.gstreamer_port = gstreamer_port
    app.mjpeg_boundary = mjpeg_boundary
    print("Finished gstreamer pipeline")


if __name__ == "__main__":

    # Load user specified configuration file
    with open("Config.json") as f:
        config = json.load(f)

    # Setup session
    app.secret_key = config["session_secret_key"]
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    app.user_config = config
    app.remote = piir.Remote("InfraredCodes.json", 17)

    setup_video_streaming()

    app.run(host="0.0.0.0", port=config["webserver_port"])

