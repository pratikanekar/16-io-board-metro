import socket
import subprocess
from time import sleep
from loguru import logger

IPAddress = '10.129.6.25'
port = 4196  # This is Final Port NOT 5000


# following fuction is used to calculate the CRC16 for relay OFF of slaves
def find_relay_off_crc(slave_id, on_change_data):
    function_code = f"05"
    if slave_id <= 9:
        read_input_data = f"000{on_change_data}0000"
        checksum = crc16(f"0{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"0{slave_id}{function_code}{read_input_data}{checksum}"
    elif slave_id == 10:
        read_input_data = f"000{on_change_data}0000"
        checksum = crc16(f"{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"{slave_id}{function_code}{read_input_data}{checksum}"
    else:
        read_input_data = f"00{on_change_data}0000"
        checksum = crc16(f"{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"{slave_id}{function_code}{read_input_data}{checksum}"


# following fuction is used to calculate the CRC16 for relay ON of slaves
def find_relay_on_crc(slave_id, on_change_data):
    function_code = f"05"
    if slave_id <= 9:
        read_input_data = f"000{on_change_data}FF00"
        checksum = crc16(f"0{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"0{slave_id}{function_code}{read_input_data}{checksum}"
    elif slave_id == 10:
        read_input_data = f"000{on_change_data}FF00"
        checksum = crc16(f"{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"{slave_id}{function_code}{read_input_data}{checksum}"
    else:
        read_input_data = f"00{on_change_data}FF00"
        checksum = crc16(f"{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"{slave_id}{function_code}{read_input_data}{checksum}"


# following fuction is used to calculate the CRC16 for slaves
def find_slave_crc(slave_id):
    function_code = f"02"
    read_input_data = f"00000008"
    if slave_id <= 9:
        checksum = crc16(f"0{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"0{slave_id}{function_code}{read_input_data}{checksum}"
    else:
        checksum = crc16(f"{slave_id}{function_code}{read_input_data}").replace(" ", "0")
        return f"{slave_id}{function_code}{read_input_data}{checksum}"


# following function is used to calculate the CRC16 (cheksum) for modbus
def crc16(data, bits=8):
    crc = 0xFFFF
    for op, code in zip(data[0::2], data[1::2]):
        crc = crc ^ int(op + code, 16)
        for bit in range(0, bits):
            if (crc & 0x0001) == 0x0001:
                crc = ((crc >> 1) ^ 0xA001)
            else:
                crc = crc >> 1
    msb = crc >> 8
    lsb = crc & 0x00FF
    return '{:2X}{:2X}'.format(lsb, msb)


# following fuction is used to READ data on slaves
def read_slaves(send_read_salve, slave_id):
    try:
        socket.send(bytes.fromhex(send_read_salve))
        logger.info(f"Send info slave{slave_id} successfully, Now trying to receive Data")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.info(f"Received Data from Slave_{slave_id}: {recv_data}")
        sleep(0.1)
    except Exception as e:
        logger.error(f"{e}")


# following fuction is used to ON relay on slaves
def relay_on(send_on_relay, slave_id, on_change_data):
    try:
        socket.send(bytes.fromhex(send_on_relay))
        logger.debug(f"Relay_{on_change_data + 1} On of Slave_{slave_id}")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.debug(f"Received for Relay ON_{on_change_data + 1}: {recv_data}")
        sleep(0.1)
    except Exception as e:
        logger.error(f"{e}")


# following fuction is used to OFF relay on slaves
def relay_off(send_off_relay, slave_id, on_change_data):
    try:
        socket.send(bytes.fromhex(send_off_relay))
        logger.debug(f"Relay_{on_change_data + 1} OFF of Slave_{slave_id}")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.debug(f"Received for Relay OFF_{on_change_data + 1}: {recv_data}")
        sleep(0.1)
    except Exception as e:
        logger.error(f"{e}")


def ping_status(IPAddress):
    try:
        res = subprocess.Popen(f"ping -c 1 -w5 {IPAddress}", shell=True, stdout=subprocess.PIPE)
        res.wait()
        return_code = res.poll()
        if int(return_code) == 0:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"{e}")


def in_direction(connected_slaves):
    relay = 8
    try:
        for slave_id in range(1, connected_slaves + 1):
            for on_change_data in range(0, relay):
                send_on_relay = find_relay_on_crc(slave_id, on_change_data)  # calculate crc16 for relay on
                relay_on(send_on_relay, slave_id, on_change_data)  # it is used to on relays on slaves
                sleep(0.5)
                send_off_relay = find_relay_off_crc(slave_id, on_change_data)  # calculate crc16 for relay off
                relay_off(send_off_relay, slave_id, on_change_data)  # it is used to off relays on slaves
                sleep(1)
                if on_change_data % 2 == 1:
                    sleep(2)  # Delay between batches of two relays
    except Exception as e:
        logger.error(f"{e}")


def out_direction(connected_slaves):
    relay = 8
    try:
        for slave_id in range(connected_slaves, 0, -1):
            for on_change_data in range(relay - 1, -1, -1):
                send_on_relay = find_relay_on_crc(slave_id, on_change_data)  # calculate crc16 for relay on
                relay_on(send_on_relay, slave_id, on_change_data)  # it is used to on relays on slaves
                sleep(0.5)
                send_off_relay = find_relay_off_crc(slave_id, on_change_data)  # calculate crc16 for relay off
                relay_off(send_off_relay, slave_id, on_change_data)  # it is used to off relays on slaves
                sleep(1)
                if on_change_data % 2 == 0:
                    sleep(2)  # Delay between batches of two relays
    except Exception as e:
        logger.error(f"{e}")


if __name__ == '__main__':
    sleep(2)
    while not ping_status(IPAddress):
        logger.info(f"Ping to {IPAddress} failed. Retrying...")
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    logger.info("socket is open waiting for connection")
    socket.connect((IPAddress, port))
    logger.info(f"connected successfully to {IPAddress} and port {port}")
    connected_slaves = 2
    slave_id = 1
    while True:
        try:
            logger.info(f"Now Started testing of IN1 - IN8 Doors Registers")
            in_direction(connected_slaves)
            logger.info(f"Now Started testing of OUT8 - OUT1 Doors Registers")
            out_direction(connected_slaves)
        except Exception as e:
            logger.error(f'{e}')
        finally:
            slave_id = slave_id + 1
