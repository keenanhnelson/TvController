# TV Controller

This project is for remotely monitoring and controlling a TV

## Setup on Linux

Make sure the system is up-to-date

```
sudo apt update && sudo apt upgrade
```

 Install required packages dev packages

```
sudo apt-get install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev liblzma-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

Install pyenv

```
curl https://pyenv.run | bash

# Adds commands to .bashrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Adds commands to .profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.profile
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.profile
echo 'eval "$(pyenv init -)"' >> ~/.profile

# Reload the bash
source ~/.bashrc
```

Next clone the project

```
git clone https://github.com/keenanhnelson/TvController.git
cd TvController
```

Install the required python version using pyenv

```
pyenv install "$(cat .python-version)"
```

Setup the virtual environment and install the required python modules

```
python -m venv venv
```

Checkout the virtual environment

```
source venv/bin/activate
```

Install the required modules

```
python -m pip install -r requirements.txt
```

Add a file called Config.json to the root of the project. This file contains all the available user configuration options. An example is shown below. Make sure to change `valid_users` to a list of better usernames and passwords. Also make sure to change the `session_secret_key` to a better password value. Lastly, make sure the `tv_info` is changed to point to the correct ip address of the desired tv. There is also a crop option that can be calibrated to only show the TV. To not crop the webcam image, remove the `crop` section entirely.

```
{
  "valid_users": {
    "bad_username": "bad_password",
    "bad_username2": "bad_password2"
  },

  "session_secret_key": "BAD_SECRET_KEY123",

  "tv_info": {
    "ip": "192.168.1.xxx",
    "port": 8002
  },
  
  "video_options": {
    "crop": {
      "left": 60,
      "right": 80,
      "top": 100,
      "bottom": 80
    }
  },
  
  "webserver_port": 4003
}
```

To run the server just type

```
python main.py
```

Use the `v4l2-ctl` command to change camera options on Linux. The below commands will list the current camera settings along with changing the camera to manual exposure and the exposure to a low value.

```
v4l2-ctl -l  # List available camera settings and current values
v4l2-ctl --set-ctrl auto_exposure=1  # Set exposure to manual
v4l2-ctl --set-ctrl exposure_time_absolute=13  # Set the exposure to a certain value. Lower will lead to a darker image
```

In order to access the server from outside the local network port forward the ip and port number of the server which is displayed after the server starts

Also use something like [duckdns](https://www.duckdns.org/) to obtain a domain that can track the dynamic ip of a typical home network 
