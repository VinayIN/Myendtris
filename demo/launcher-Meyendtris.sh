function drawline() {
    printf '%*s\n' "${COLUMNS:-$(tput cols)}" '' | tr ' ' -
}

function statuscheck() {
    drawline
    echo "[${BLUE}Status Check${NOCOLOR}]"
    echo    "host: ${USER}"
    echo    "cwd: `pwd`"
    echo;
    if [[ -s "${USER}\lsl_api\lsl_api.cfg" ]]; then
        echo    "${GREEN}${USER}\lsl_api\lsl_api.cfg found in user directory${NOCOLOR}"
        echo;
    else
        echo    "${RED}${USER}\lsl_api\lsl_api.cfg not found in user directory${NOCOLOR}"
        echo;
    fi
}

function toggle_lsl_sessionid() {
    drawline
    echo "[${BLUE}Toggle LSL SessionID${NOCOLOR}]"
    if [[ -s "${USER}\lsl_api\lsl_api.cfg" ]]; then
        echo    "DELETE ${USER}\lsl_api\? [y/n]"
        read r
        if [ $r -eq 'y' ]; then
            rm -rf ${USER}\lsl_api
        elif [ $r -e 'n' ]; then
            echo    "WRITE ${USER}\lsl_api\lsl_api.cfg settings SessionID to phypa? [y/n]"
            read r
            if [ $r -eq 'y' ]; then
                if [ ! -d ${USER}\lsl_api\ ]; then
                    mkdir ${USER}\lsl_api
                    ${USER}\lsl_api\lsl_api.cfg echo [lab]
                    ${USER}\lsl_api\lsl_api.cfg echo SessionID = phypa
                fi
            fi
        fi
    fi
}

cat << "LOGO"

 _____                     ______ _          ______  ___  
|_   _|                    | ___ \ |         | ___ \/ _ \ 
  | | ___  __ _ _ __ ___   | |_/ / |__  _   _| |_/ / /_\ \
  | |/ _ \/ _` | '_ ` _ \  |  __/| '_ \| | | |  __/|  _  |
  | |  __/ (_| | | | | | | | |   | | | | |_| | |   | | | |
  \_/\___|\__,_|_| |_| |_| \_|   |_| |_|\__, \_|   \_| |_/
                                         __/ |            
                                        |___/             
          

Physiological Parameters for Adaptation  :___/  teamphypa.org


LOGO

# color variables
RED='\033[0;31m'   
GREEN='\033[0;32m'   
YELLOW='\033[1;33m'   
BLUE='\033[0;34m'
NOCOLOR='\033[0m'
VERSION="v0.1.2"

echo    "Launcher version: ${GREEN}${VERSION}${NOCOLOR}"

while
    drawline
    echo    "Enter an option, (${RED}CTLR+C${NOCOLOR} to exit anytime)"
    echo    "1. Calibration (Alpha)"
    echo    "2. Classifier Test (Bar)"
    echo    "3. Meyendtris"
    read n
    [ $n -le 3 ]
do
    statuscheck
    echo;
    toggle_lsl_sessionid
    echo;
    case $n in
  "1")
    drawline
    echo    "Running ${YELLOW}Calibration (Alpha)${NOCOLOR}"
    ;;
  "2")
    drawline
    echo    "Running ${YELLOW}Classifier Test (Bar)${NOCOLOR}"
    ;;
  "3")
  drawline
    echo    "Running ${YELLOW}Meyendtris${NOCOLOR}"
    ;;
esac
done

