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

Change the username and password in `Secrets/ValidUsers.json` to something more secure. These will be required when first logging into the server. 

Also make sure to change `Secrets/SessionsSecretKey.txt` to a more secure value. These key will be used to encrypt the user session which remembers a previously logged in user's credentials.

To run the server just type

```
python main.py
```

In order to access the server from outside the local network portforward the ip and port number of the server

Also use something like [duckdns](https://www.duckdns.org/) to obtain a domain that can track the dynamic ip of a typical home network 
