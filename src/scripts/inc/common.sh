#!/bin/bash

TMP_DIR="/tmp"
RUN_USER="spacepi"
HOME_DIR="/var/lib/space"

function run_python {
    python3 "$@"
}

function run_pip {
    pip3 "$@"
}

function init_classic {
    local monitorspace=${1}

    install -Dm744 initd_space.sh /etc/init.d/spacePi

    mkdir -p /etc/opt/spacePi
    touch /etc/opt/space/.keep
    if [ "$monitorspace" == true ]; then
        touch /etc/opt/spaePi/monitor_enable
    fi

    touch /var/log/spacePi.log

    update-rc.d spacePi defaults
}

function init_systemd {
    local monitorspace=${1}

    install -Dm644 ./spacePi.service /usr/lib/systemd/system/spacePi.service
    mkdir -p /etc/systemd/system/spacePi.service.d/

    if [ "$monitorAlexa" == true ]; then
        install -Dm644 ./unit-overrides/restart.conf /etc/systemd/system/spacePi.service.d/restart.conf
    fi

    systemctl daemon-reload
    systemctl enable spacePi.service
}

function create_user {

    echo -n "Creating a user to run spacePi under ... "

    if id -u ${RUN_USER} >/dev/null 2>&1; then
        echo "user already exists. That's cool - using that."
    else
        if useradd --system --user-group ${RUN_USER} 2>/dev/null; then
            echo "done."
        else
            echo "unknown error. useradd returned code $?."
        fi

        mkdir -p ${HOME_DIR}
        chown ${RUN_USER}:${RUN_USER} ${HOME_DIR}
        usermod --home ${HOME_DIR} ${RUN_USER}
    fi

    getent group gpio || groupadd gpio
    getent group audio || groupadd audio

    gpasswd -a ${RUN_USER} gpio > /dev/null
    gpasswd -a ${RUN_USER} audio > /dev/null

}

function gpio_permissions {

    local rulesFile="/etc/udev/rules.d/99-gpio.rules"

    if [ ! -f ${rulesFile} ]; then
        # shellcheck disable=SC2154
        cat >${rulesFile} <<'EOL'
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c '\
	chown -R root:gpio /sys/class/gpio && chmod -R 770 /sys/class/gpio;\
	chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 770 /sys/devices/virtual/gpio;\
	chown -R root:gpio /sys$devpath && chmod -R 770 /sys$devpath\
'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value ; chmod 660 /sys%p/active_low /sys%p/direction /sys%p/edge /sys%p/value'"
EOL
    fi

}

function install_shairport-sync_from_source {

    cd ${TMP_DIR}

    git clone https://github.com/mikebrady/shairport-sync.git
    cd shairport-sync
    autoreconf -i -f
    ./configure --with-alsa --with-avahi --with-ssl=openssl --with-soxr --with-metadata --with-pipe --with-systemd
    make
    getent group shairport-sync &>/dev/null || sudo groupadd -r shairport-sync >/dev/null
    getent passwd shairport-sync &> /dev/null || sudo useradd -r -M -g shairport-sync -s /usr/bin/nologin -G audio shairport-sync >/dev/null
    make install

    rm -rf ${TMP_DIR}/shairport-sync

}

# global variable $CONFIG_FILE
function config_get {
    grep -o -P "(?<=${1}:).*" "${CONFIG_FILE}" | sed 's/^ *//;s/ *$//;s/"//g'
}

# $1 field name
# $2 user input
# global array config_defaults
# global variable $CONFIG_FILE
function config_set {
    local name=${1}
    local value=${2}

    if [ "${value}" == "" ]; then
        # shellcheck disable=SC2154
        value="${config_defaults[${name}]}"
    fi
    sed -i -e 's/ '"${name}"'.*/ '"${name}"': "'"${value}"'"/g' "${CONFIG_FILE}"
}

function handle_root_platform {
    echo "Unfortunately, to use LEDs or trigger button on this platform (${1}) you have to"
    echo "a) run space as root"
    echo "b) and switch the device platform in the configuration file."
    echo "If you wish to do that, please see the section in our wiki for instructions: https://github.com/Space-Monkey-KD/space/wiki/Devices"
}
