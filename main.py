import socket
from flask import Flask, render_template, Response, redirect, request, session
import subprocess
from samsungtvws import SamsungTVWS
from roku import Roku
from flask_session import Session
import json
import os
import platform

app = Flask(__name__)

# Set session secret key
with open("Secrets/SessionsSecretKey.txt") as f:
    session_secret_key = f.read()
app.secret_key = session_secret_key
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Read valid users
with open("Secrets/ValidUsers.json") as f:
    valid_users = json.load(f)


def check_if_user_has_already_logged_in():
    if not session.get("username"):
        return False
    if session.get("username") in valid_users:
        if session.get("password") == valid_users[session.get("username")]:
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
        if input_username in valid_users:
            if input_password == valid_users[input_username]:
                session["username"] = input_username
                session["password"] = input_password
                return redirect("/")
        error_msg = "Wrong username or password"
    return render_template("login.html", error_msg=error_msg)


@app.route("/remote_action", methods=["POST"])
def remote_action():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    # for key, value in request.form.items():
    #     if key in app.tv_action:
    #         app.tv_action[key]()

    tv_ip_address = "192.168.254.125"
    tv_port = 8002
    token_file = os.path.dirname(os.path.realpath(__file__)) + '/Secrets/TvToken.txt'

    if "button_power_toggle" in request.form:
        print("Pressed button_power_toggle")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().power()
    elif "button_up" in request.form:
        print("Pressed button_up")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().up()
    elif "button_left" in request.form:
        print("Pressed button_left")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().left()
    elif "button_enter" in request.form:
        print("Pressed button_enter")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().enter()
    elif "button_right" in request.form:
        print("Pressed button_right")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().right()
    elif "button_down" in request.form:
        print("Pressed button_down")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().down()
    elif "button_back" in request.form:
        print("Pressed button_back")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().back()
    elif "button_menu" in request.form:
        print("Pressed button_menu")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().menu()
    elif "button_volume_up" in request.form:
        print("Pressed button_volume_up")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().volume_up()
    elif "button_volume_down" in request.form:
        print("Pressed button_volume_down")
        SamsungTVWS(host=tv_ip_address, port=tv_port, token_file=token_file).shortcuts().volume_down()
    print("Finished button press")
    return "", 204


@app.route("/remote_screen")
def remote_screen():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    return render_template("RemoteScreen.html")


def gen(s):
    while True:
        yield s.recv(2048)


@app.route("/remote_video")
def remote_video():
    if not check_if_user_has_already_logged_in():
        return redirect('/login')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", app.gstreamer_port))
    return Response(gen(s), mimetype=f'multipart/x-mixed-replace; boundary={app.mjpeg_boundary}')


def find_open_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def setup_tv_actions(ip, port):
    print("Connecting to samsung tv")
    tv_token_file = os.path.dirname(os.path.realpath(__file__)) + '/Secrets/TvToken.txt'
    # tv_remote = SamsungTVWS(host=ip, port=port, token_file=tv_token_file)
    print("Finished connecting to samsung tv")

    tv_action = {
        "button_power_toggle": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().power,
        "button_up": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().up,
        "button_left": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().left,
        "button_enter": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().enter,
        "button_right": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().right,
        "button_down": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().down,
        "button_back": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().back,
        "button_menu": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().menu,
        "button_volume_up": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().volume_up,
        "button_volume_down": SamsungTVWS(host=ip, port=port, token_file=tv_token_file).shortcuts().volume_down,
    }
    app.tv_action = tv_action
    print("done")


def setup_video_streaming():
    print("Opening gstreamer pipeline")
    if platform.system() == "Windows":
        gstreamer_cmd = "gst-launch-1.0.exe"
        webcam_option = ["ksvideosrc", "device-index=0"]
    elif platform.system() == "Linux":
        gstreamer_cmd = "gst-launch-1.0"
        webcam_option = ["v4l2src", "device=/dev/video0"]
    else:
        raise Exception(f"Does not currently suppport {platform.system()}")

    gstreamer_port = find_open_port()  # 5007
    mjpeg_boundary = "video_boundary"
    print(f"{gstreamer_port=}")
    cmd = [
        gstreamer_cmd,
        "-v",
        *webcam_option,
        "!", "videoconvert",
        "!", "jpegenc",
        "!", "multipartmux", f"boundary={mjpeg_boundary}",
        "!", "tcpserversink", "host=0.0.0.0", f"port={gstreamer_port}",
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    app.gstreamer_port = gstreamer_port
    app.mjpeg_boundary = mjpeg_boundary
    print("Finished gstreamer pipeline")


if __name__ == "__main__":
    # tv_ip_address = "192.168.254.125"
    # tv_port = 8002
    # setup_tv_actions(tv_ip_address, tv_port)

    setup_video_streaming()

    webhost_port = 4003
    app.run(host="0.0.0.0", port=webhost_port)

