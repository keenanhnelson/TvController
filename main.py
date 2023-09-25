import socket
from flask import Flask, render_template, Response, redirect, request
import subprocess
import samsungctl
from roku import Roku

app = Flask(__name__)


@app.route("/")
def root():
    return redirect("/remote_screen")


@app.route("/remote_action", methods=["POST"])
def remote_action():
    config_samsung = {
        "name": "samsungctl",
        "description": "PC",
        "id": "",
        "host": "192.168.254.167",
        "port": 55000,
        "method": "legacy",
        "timeout": 0,
    }
    remote = samsungctl.Remote(config_samsung)

    # https://github.com/ollo69/ha-samsungtv-smart/blob/master/docs/Key_codes.md
    if "button_power_on" in request.form:
        print("Pressed button_power_on")
        remote.control("KEY_POWERON")
    elif "button_power_off" in request.form:
        print("Pressed button_power_off")
        remote.control("KEY_POWEROFF")
    elif "button_up" in request.form:
        print("Pressed button_up")
        remote.control("KEY_UP")
    elif "button_left" in request.form:
        print("Pressed button_left")
        remote.control("KEY_LEFT")
    elif "button_select" in request.form:
        print("Pressed button_select")
        remote.control("KEY_ENTER")
    elif "button_right" in request.form:
        print("Pressed button_right")
        remote.control("KEY_RIGHT")
    elif "button_down" in request.form:
        print("Pressed button_down")
        remote.control("KEY_DOWN")
    elif "button_volume_up" in request.form:
        print("Pressed button_volume_up")
        remote.control("KEY_VOLUP")
    elif "button_volume_down" in request.form:
        print("Pressed button_volume_down")
        remote.control("KEY_VOLDOWN")

    remote.close()
    return "", 204


@app.route("/remote_screen")
def remote_screen():
    return render_template("RemoteScreen.html")


def gen(s):
    while True:
        yield s.recv(2048)


@app.route("/stream")
def stream():
    print("stream() called")

    gstreamer_cmd = "gst-launch-1.0.exe"
    gstreamer_port = 5007
    mjpeg_boundary = "video_boundary"
    cmd = [
            gstreamer_cmd,
            "-v",
            "ksvideosrc", "do-stats=True",
            "!", "videoconvert",
            "!", "jpegenc",
            "!", "multipartmux", f"boundary={mjpeg_boundary}",
            "!", "tcpserversink", "host=0.0.0.0", f"port={gstreamer_port}",
        ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", gstreamer_port))
    return Response(gen(s), mimetype=f'multipart/x-mixed-replace; boundary={mjpeg_boundary}')


if __name__ == "__main__":
    # config_samsung = {
    #     "name": "samsungctl",
    #     "description": "PC",
    #     "id": "",
    #     "host": "192.168.254.167",
    #     "port": 55000,
    #     "method": "websocket",
    #     "timeout": 0,
    # }
    # remote = samsungctl.Remote(config_samsung)
    # remote.control("KEY_VOLUP")
    # remote.close()

    # app.run(debug=True, port=4003)
    app.run(host="0.0.0.0", port=4003)
# gst-launch-1.0 -v d3d11screencapturesrc monitor-index=1 crop-x=1280 crop-y=720 crop-width=320 crop-height=240 ! videoconvert ! jpegenc ! multipartmux boundary=video_boundary ! tcpserversink host=0.0.0.0 port=5007
