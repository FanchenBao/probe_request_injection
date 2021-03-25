## DISCLAIMER: increasing txpower might violate the law! Please do NOT be stupid and BE LIKE JIMMY!

# Description

This repo contains scripts and guides to achieve two goals:

1. Modify txpower on a WiFi chip that is resistant to the commonly prescribed method.
2. Perform probe request injection

For the usage of the scripts, you can go to [Usage](https://github.com/FanchenBao/probe_request_injection#usage) directly. If you want to read a bit about the story behind this repo, continue onto [Story](https://github.com/FanchenBao/probe_request_injection#story).

# Story
Below is the process I have gone through to find a solution that allows me to perform probe request injection at different txpower level on a [AWUS036NHA](https://www.alfa.com.tw/products/awus036nha?variant=36473966166088) WiFi adapter.

## Motivation

For research purpose, I need to emit probe request at different txpower level on my AWUS036NHA WiFi adapter, which is connected to a raspberry Pi 4B (RPi). However, the commonly used method, such as [this one](https://forums.kali.org/showthread.php?4129-Increase-Wi-Fi-TX-Power-Signal-Strength), does not work when the WiFi adapter (wlan1) is on monitor mode. Yet emitting probe request is only possible on monitor mode. Thus I am stuck.

```bash
pi@raspberrypi:~ $ sudo iwconfig wlan1 txpower 30
Error for wireless request "Set Tx Power" (8B26) :
    SET failed on device wlan1 ; Operation not supported.
```

Fortunately, I came across [this answer](https://askubuntu.com/a/1169997/1193746), which walked me through a more complicated way to change txpower. According to the author, some WiFi chip, such as the one in AWUS036NHA, has its region stuck to a country by the manufactuer. This makes it impossible to change txpower by simply reseting the country code to one that allows higher txpower. This seemed to fit my problem very well, so I went through all the steps and was indeed able to modify txpower.

However, even with this convoluted method, I still was NOT able to make commands such as `sudo iwconfig wlan1 txpower 30` or `iw dev wlan1 set txpower fixed 2500` work. This left me with the option that I had to rebuild the regulatory database each time a new txpower level was needed. Yet, since reboot is required to have the updated regulatory database take effect, I am looking at six reboots to emit probe request from 5 dBm to 30 dBm with 5 dBm increments. This apparently does not sound fun for the hardware; nor is it scalable if more txpower levels need to be visited.

## Breakthrough
As I was playing around with different commands, I found that **after the regulatory database had been rebuilt**, I was able to change txpower to the maximum allowed in each country by simply resetting the country code. For instance, if the regulatory database looks like this:

```
country FOO: DFS-FCC
	(2402 - 2482 @ 40), (10)

country BAR: DFS-FCC
	(2402 - 2472 @ 40), (20)

country BAZ: DFS-FCC
	(2402 - 2472 @ 40), (30)
```

I can set txpower on wlan1 to 10 dBm by running

```bash
sudo iw reg set FOO && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up
```

Similarly, I can set it to 20 dBm by running

```bash
sudo iw reg set BAR && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up
```

This is great! Although I was NOT able to specifically set wlan1 txpower to XX dBm, I could work around it by setting the region to the country whose max txpower matches XX dBm. But there is a catch, when I ran `sudo iw reg set BAZ && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up` to ramp up txpower to 30 dBm, it did not work.

## Catch
The reason why setting region to BAZ did NOT work was that the default country where the WiFi chip was stuck to (it is GB, by the way) had the max txpower at 20 dBm. Thus, in order to set wlan1 to 30 dBm, it seemed that I had to increase the max txpower allowed in GB to at least 30 dBm. I made the change, and sure enough, setting region to BAZ successfully changed wlan1 txpower to 30 dBm.

## Solution
Here is the solution that suits my need.

1. Follow the [answer](https://askubuntu.com/a/1169997/1193746) to rebuild the regulatory database. When modifying the database, set the txpower on GB, the default country of the WiFi chip, to the max level I want, e.g. 30 dBm. Then choose any country and set their txpower to the level I want. Since I need six txpower levels, I arbitrarily change the txpower of six countries in the regulatory database. By the way, I know that GB is the default country of the WiFi chip because running `iw reg get` shows that `phy#1` is attached to GB.
2. After the new regulatory database is in use, loop through each country that I have arbitrarily chosen above, set the region to that country, and the WiFi chip's txpower will become the txpower associated with that country.

# Usage

## Download this repo

`git clone https://github.com/FanchenBao/probe_request_injection.git`

## Install dependencies

For modifying txpower, do the following:

1. System-level dependency
    ```bash
    sudo apt-get update && sudo apt-get install python-future python-m2crypto libgcrypt20 libgcrypt20-dev libnl-dev -y
    ```
2. Get repo for modifying regulatory database
    ```bash
    wget https://git.kernel.org/pub/scm/linux/kernel/git/sforshee/wireless-regdb.git/snapshot/wireless-regdb-master-2019-06-03.tar.gz
    wget https://git.kernel.org/pub/scm/linux/kernel/git/mcgrof/crda.git/snapshot/crda-4.14.tar.gz
    tar xfv wireless-regdb-master-2019-06-03.tar.gz
    tar xfv crda-4.14.tar.gz
    ```
3. Move the downloaded repos to `probe_request_injection/mod_txpower`
    ```bash
    mv -r wireless-regdb-master-2019-06-03 probe_request_injection/mod_txpower
    mv -r crda-4.14 probe_request_injection/mod_txpower
    ```
4. If the original `regulatory.bin` in your system exists in `/lib/crda/` instead of `/usr/lib/crda` (i.e. check to see the contents of `/lib/crda/` and `/usr/lib/crda`), as is the case with RPi, change this line `REG_BIN?=/usr/lib/crda/regulatory.bin` to `REG_BIN?=/lib/crda/regulatory.bin` in `mod_txpower/crda-4.14/Makefile`.

For emitting probe request, do the following:

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip3 install -r requirements.txt`
4. Install [tmux](https://github.com/tmux/tmux/wiki/Installing) 

## Rebuild the regulatory database
The rebuild contains two steps (assuming we are in the root directory of `probe_request_injection`).

1. Change the max txpower level specified in `wireless-regdb-master-2019-06-03/db.txt`. This can be done manually, or programatically using the script `mod_txpower/modify_regdb.py`. Below is an example using the script to change the max txpower associated with GB to 30 dBm.

    ```bash
    python3 mod_txpower/modify_regdb.py --country GB --power 30
    ```

    The `mod_txpower/modify_regdb.py` script has other features. Read `python3 mod_txpower/modify_regdb.py -h` for details. **Note that to run this python script, you do NOT have to be in the virtual environment.**

2. Prepare backups
    ```bash
    sudo cp /lib/firmware/regulatory.db /lib/firmware/regulatory.db-backup
    sudo cp /lib/firmware/regulatory.db.p7s /lib/firmware/regulatory.db.p7s-backup
    sudo cp /lib/crda/regulatory.bin /lib/crda/regulatory.bin-backup
    ```
3. Run command

    ```bash
    ./mod_txpower/mod_txpower.sh
    ```
    
    The script takes care of all the building and file copying steps of rebuilding the regulatory database. These steps are exactly the same as specified in the [answer](https://askubuntu.com/a/1169997/1193746). The script also triggers reboot. After reboot, the updated regulatory database is in use.


## Emit probe request

Probe request injection is achieved using the [Scapy](https://scapy.readthedocs.io/en/latest/) library. The logic of emitting probe request is in `emit/emit_probe_request.py`. Using this script requires that the virtual environment be activated. Run the following command to read the helper text of this script.

```bash
source venv/bin/activate
python3 emit/emit_probe_request.py -h
```

However, we will not be running this script directly to emit probe request, because emitting also requires that we are under `sudo` all the time. To make this process easier, we simply use `emit/emit.sh` script to run the Python script in a tmux session. Run the following command to read its helper text.

```bash
./emit/emit.sh -h
```

## Examples

### Example 1: modify txpower

Suppose your WiFi chip (wlan1) is stuck to country code GB (see [Solution](https://github.com/FanchenBao/probe_request_injection#solution) regarding how you can tell which country your WiFi chip is stuck to), which has txpower capped at 20 dBm. You want to modify txpower to 30 and 40 dBm. Here are the scripts to help you achieve your goal.

1. Modify regulatory database

    ```bash
    # Increase max txpower allowed on GB
    python3 mod_txpower/modify_regdb.py --country GB --power 40

    # Pick any two countries and set their max txpower to 30 and 40 dBm
    python3 mod_txpower/modify_regdb.py --country ZA --power 30
    python3 mod_txpower/modify_regdb.py --country ZW --power 40

    # rebuild regulatory database and reboot
    ./mod_txpower/mod_txpower.sh
    ```

2. Change txpower after regulatory database rebuild

    ```bash
    # Sanity check to see whether max txpower associated with GB has been changed to 40
    iw reg get

    # Change to 30 dBm
    sudo iw reg set ZA && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up
    # Check txpower
    iwconfig wlan1

    # Change to 40 dBm
    sudo iw reg set ZW && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up
    # Check txpower
    iwconfig wlan1
    ```

### Example 2: emit probe request

1. Emit on wlan1, channel 10, every second, using current time stamp as MAC prefix

    ```
    ./emit/emit.sh -i wlan1 -c 10 --interval 1
    ```

2. Emit on wlan1, channel 5, with MAC prefix set to `12:34:56` and default emission interval
    ```
    ./emit/emit.sh -i wlan1 -c 5 --mac 12:34:56
    ```

### Example 3: emit probe request on 30 and 40 dBm

After going through [Example 1](https://github.com/FanchenBao/probe_request_injection#example-1-modify-txpower), we can use the following script to emit probe request on wlan1 at two different txpower levels, with their MAC address specifying which txpower level they are on. Each emission lasts 30 seconds.

```bash
COUNTRY_LIST="ZA ZW"
for COUNTRY in $COUNTRY_LIST; do
    # set to a new txpower
    sudo iw reg set $COUNTRY && sudo ifconfig wlan1 down && sudo ifconfig wlan1 up
    # record the current txpower
    CUR_TXPOWER=$(iwconfig wlan1 | grep -Po "(?<=Tx-Power=)\d+(?=\sdBm)")
    # Create a custom MAC address indicating the current txpower.
    # e.g. 40:00:00:00:00:00 for txpower at 40 dBm
    MAC=$(printf "%02d" $CUR_TXPOWER):00:00:00:00:00
    ./emit/emit.sh -i wlan1 -c 10 --mac $MAC
    sleep 30
    tmux kill-sess -t emit
done
```

# License
[MIT](https://github.com/FanchenBao/probe_request_injection/blob/master/LICENSE)