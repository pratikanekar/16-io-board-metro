import socket
from time import sleep
from loguru import logger

# IPAddress = "192.168.1.251"
logger.info(f"Please confirm the Modbus_to_rtu convertor protocol is set None")
IPAddress = str(input("Please Enter IP_address where Io_Board is connected :"))
port = 4196  # This is Final Port NOT 5000


def read_data():
    try:
        # following code for set slave id
        # set_slave_id = f"001000000001020033EBD5"
        set_slave_id = str(input("Please Provide Raw_data_string to set Slave_id :"))
        display_slave_id = int(set_slave_id[16:-4], 16)
        socket.send(bytes.fromhex(set_slave_id))
        logger.info(f"Send set_command successfully to Io_Board, Now trying to receive Data")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.info(f"Received Data from Io_Board: {recv_data}")
        sleep(0.1)
        logger.info(f"Successfully set Slave id {display_slave_id} to Io_Board")


        # following code for rely on
        # relay_on = f"3302000000087DDE"
        relay_on = str(input("Please Provide Raw_data_string to relay on :"))
        socket.send(bytes.fromhex(relay_on))
        logger.info(f"Send relay_on successfully to Io_Board, Now trying to receive Data")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.info(f"Successfully relay_on: {recv_data}")
        sleep(0.1)


        # following code for relay off
        # relay_off = f"33050000FF008828"
        relay_off = str(input("Please Provide Raw_data_string to relay off :"))
        socket.send(bytes.fromhex(relay_off))
        logger.info(f"Send relay_off successfully to Io_Board, Now trying to receive Data")
        socket.settimeout(2)
        recv_data = socket.recv(1024).hex().upper()
        logger.info(f"Successfully relay_off: {recv_data}")
        sleep(0.1)
    except Exception as e:
        logger.error(f"{e}")


if __name__ == '__main__':
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info("socket is open waiting for connection")
    socket.connect((IPAddress, port))
    logger.info(f"connected successfully to {IPAddress} and port {port}")
    read_data()
    sleep(0.1)