import time, re, sys, logging
import telnetlib
import sierrakeygen
import luhn
from colorlog import ColoredFormatter

# Colored logs
LOG_LEVEL = logging.DEBUG
LOGFORMAT = "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s"
logging.root.setLevel(LOG_LEVEL)
formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(formatter)
logger = logging.getLogger('pythonConfig')
logger.setLevel(LOG_LEVEL)
logger.addHandler(stream)


HOST = sys.argv[1]
PORT = 5510
TIMEOUT = 3

def verifyImei(new_imei):
    if not luhn.verify(new_imei):
        logger.error("Not a valid IMEI Number!")
        sys.exit(1)
    if not new_imei.isdigit():
        logger.error("IMEI should only contain numbers!")
        sys.exit(1)
    if len(new_imei) != 15:
        logger.error("IMEI should be 15 digits!")
        sys.exit(1)

def connectToDevice():
    try:
        telnet = telnetlib.Telnet(HOST, PORT, TIMEOUT)
        logger.info("Connection established")
        return telnet
    except Exception as e:
        logger.error(f"Error connecting to device: {e}")
        sys.exit(1)

def getCurrentImei(telnet):
    telnet.write(b"ATI\r\n")
    time.sleep(5)
    response = telnet.read_very_eager().decode('utf-8')
    imei_match = re.search(r"IMEI: (\d+)", response)
    if imei_match:
        current_imei = imei_match.group(1)
        logger.info(f"Device Current IMEI: {current_imei}")
        return current_imei
    else:
        logger.error("Could not retrieve current IMEI")
        sys.exit(1)

def getOpenLockChallenge(telnet):
    telnet.write(b"AT!OPENLOCK?\r\n")
    time.sleep(5)
    response = telnet.read_very_eager().decode('utf-8')
    challenge = response[15:-8]
    if "OK" in response:
        logger.info(f"Open Lock Challenge: {challenge}")
        return challenge
    else:
        logger.error("Could not retrieve Open Lock Challenge")
        sys.exit(1)

def generateOpenLockHash(challenge):
    keygen = sierrakeygen.SierraGenerator()
    devicegeneration = "MDM9x40"
    resp = keygen.run(devicegeneration, challenge, 0)
    logger.info(f"Key Generator Response: {resp}")
    return resp

def disableOpenLock(telnet, resp):
    logger.info("Disabling Open Lock")
    openlockWrite = "AT!OPENLOCK=\"" + resp + "\"\r\n"
    telnet.write(openlockWrite.encode('ascii'))
    time.sleep(5)
    response = telnet.read_very_eager().decode('utf-8')
    if "OK" in response:
        logger.info("Open Lock disabled successfully")
    else:
        logger.error("Failed to disable Open Lock")
        sys.exit(1)

def updateImei(telnet, newImei):
    logger.info("Unlocking IMEI")
    telnet.write(b"AT!NVIMEIUNLOCK\r\n")
    time.sleep(5)
    response = telnet.read_very_eager().decode('utf-8')
    if 'OK' in response:
        fullImei = luhn.append(newImei)
        encryptImei = ','.join(fullImei[i:i + 2] for i in range(0, len(fullImei), 2))
        encryptImeiWrite = "AT!NVENCRYPTIMEI=" + encryptImei + "\r\n"
        telnet.write(encryptImeiWrite.encode('ascii'))
        time.sleep(5)
        logger.info(f"IMEI updated successfully: {fullImei}")
    else:
        logger.error("Failed to update IMEI")
        sys.exit(1)

def rebootRouter(telnet):
    logger.info("IMEI Restored. Rebooting Router")
    telnet.write(b"AT!RESET\r\n")
    time.sleep(5)
    telnet.close()
    logger.info("Router rebooted successfully")

if __name__ == "__main__":
    new_imei = sys.argv[2]
    verifyImei(new_imei)
    with connectToDevice() as telnet:
        current_imei = getCurrentImei(telnet)
        challenge = getOpenLockChallenge(telnet)
        resp = generateOpenLockHash(challenge)
        disableOpenLock(telnet, resp)
        updateImei(telnet, new_imei)
        getCurrentImei(telnet)
        rebootRouter(telnet)