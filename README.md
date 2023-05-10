Simple python script that utilizes a few libraries to create a voice-activated virtual assistant on the device of your choosing.  
This is my version of an "open-source Alexa" that focuses on the one feature that I use the most: playing music.  It works by using the Vosk voice recognition library
to interpret the user's voice, pyttsx3 library to provide vocal feedback to the user, and the Selenium engine to navigate and play videos on youtube.

Anyone interested in developing their own music-playing virtual assistant, similar to popular voice assistants, may find this repository beneficial. 
I made this so I wouldn't have to keep paying my monthly Amazon Music Unlimited subscription and the added privacy from using my own IoT device is also a plus.

Hardware:

Raspberry Pi 4 Model B 2GB RAM - Small but powerful device to replace my Amazon Echo
https://www.raspberrypi.com/products/raspberry-pi-4-model-b/

Raspberry Pi 32GB Preloaded (NOOBS) SD Card - For Raspbian OS and storage
https://www.amazon.com/Raspberry-Pi-32GB-Preloaded-NOOBS/dp/B01LXR6EOA

GeeekPi Raspberry Pi Mini Tower Kit, Raspberry Pi 4 Case with ICE Tower Cooler - Ice tower keeps RPi temps cool and this kit includes a case that goes well with it
https://www.amazon.com/GeeekPi-Raspberry-Heatsink-Expansion-Boardfor/dp/B0B6V7XFJH

Mini USB Microphone for Laptop and Desktop Computer - I used this one, but feel free to use any microphone that works with your device
https://www.amazon.com/Microphone-Gooseneck-Universal-Compatible-CGS-M1/dp/B08M37224H

Software:

Music Mode for Youtube chrome extension - extension that has tons of features that help make the music listening experience better (block ads, etc.)
https://chrome.google.com/webstore/detail/music-mode-for-youtube/abbpaepbpakcpipajigmlpnhlnbennna

ChromeDriver - required for Selenium if you don't use any driver manager
https://chromedriver.chromium.org/downloads


This is not intended to be a major project for me, but I will try my best when I have time to help anyone who is trying to recreate this for their own purposes.

Additional Notes: 
- Wasn't able to install the latest version of python on my raspberry pi, so I was not able to utilize match case for the process_command function.  Lots of "elif" as a result.
- Will incorporate async at some point so that wait times are shorter
- Saw in the news this morning that youtube is cracking down on adblockers, so will have to deal with that if/when that happens.
- Spent a long time trying to set up my raspberry pi so that it would run the script at startup but was not able to get it to work.  Maybe in the future...

Credit to Brandon Jacobson's youtube (https://www.youtube.com/@BrandonJacobson) videos for help with installing the libraries and setting up the 
speech to text and text to speech functionality(Vosk, pyaudio, pyttsx3, etc).  Please check out his videos if you need help with getting those to work.
