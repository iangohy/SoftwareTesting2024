import logging
import asyncio
from subprocess import Popen, PIPE, STDOUT
from binascii import hexlify

import subprocess
from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link, Transport
from bumble.utils import AsyncRunner
from bumble.colors import color
import logging
import os

logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

def find_and_kill_processes(port):
    try:
        # Run the lsof command to find processes using the specified port
        result = subprocess.run(['lsof', '-t', '-i', f':{port}'], capture_output=True, text=True, check=True)
        # Extract process IDs
        pids = result.stdout.splitlines()
        if pids:
            logger.info(f"Found processes on port {port}: {pids}")
            # Kill the processes
            for pid in pids:
                subprocess.run(['kill', pid])
                # os.kill(int(pid), 2)
                logger.info(f"Killed process {pid} using port {port}")
        else:
            logger.info(f"No processes found running on port {port}")
    except Exception as e:
        logger.info("Error")
    
class TargetEventsListener(Device.Listener):

    def __init__(self):
        self.got_advertisement = False
        self.advertisement = None
        self.connection = None
    
    async def write_target(self, target, attribute, bytes):
        # Write data to bluetooth target
        outputs = ""
        try:
            bytes_to_write = bytearray(bytes)
            await target.write_value(attribute, bytes_to_write, True)
            outputs =f'[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}'
            return outputs
        except ProtocolError as error:
            outputs = f'[!]  Cannot write attribute 0x{attribute.handle:04X}:'
        except TimeoutError:
            logger.info("=====Write Timeout=====")
            outputs = '[X] Write Timeout'
            find_and_kill_processes(9000)
        except Exception as ex:
            logger.info(ex)
            find_and_kill_processes(9000)
            
        return outputs


    async def read_target(self, target, attribute):
        # Read data from bluetooth target
        outputs = ""
        try: 
            read = await target.read_value(attribute)
            value = read.decode('latin-1')
            outputs=f'[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}, decoded={value}'
            return outputs
        except ProtocolError as error:
            outputs=f'[!]  Cannot read attribute 0x{attribute.handle:04X}:'
        except TimeoutError:
            logger.info("=====Read Timeout=====")
            outputs ='[!] Read Timeout'
            find_and_kill_processes(9000)
        except Exception as ex:
            logger.info(ex)
            find_and_kill_processes(9000)
        
        return outputs

    def on_advertisement(self, advertisement):
        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        logger.info("=====Connected=====")
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        target = Peer(connection)
        attributes = []
        await target.discover_services()
        for service in target.services:
            attributes.append(service)
            await service.discover_characteristics()
            for characteristic in service.characteristics:
                attributes.append(characteristic)
                await characteristic.discover_descriptors()
                for descriptor in characteristic.descriptors:
                    attributes.append(descriptor)

        logger.info("=====Services discovered=====")
        show_services(target.services)
        
        
        # -------- Main interaction with the target here --------
        logger.info('=== Read/Write Attributes (Handles)')
        for i in range(len(attributes)):
            logger.info("==================================")
            logger.info(target)
            logger.info(attributes[i])
            # if attributes[i].handle == |replace_handle|:
            if attributes[i].handle == 37:
                # response_write = await self.write_target(target, attributes[i], [|replace_byte|])
                response_write = await self.write_target(target, attributes[i], [0x0037])
                response_read = await self.read_target(target, attributes[i])
                logger.info("response_write:"+response_write)
                logger.info("response_read:"+response_read)
        logger.info('---------------------------------------------------------------')
        logger.info('[OK] Communication Finished')
        logger.info('---------------------------------------------------------------')
        
        find_and_kill_processes(9000)
        # ---------------------------------------------------

def run_target():
    os.chdir("|bluetooth_dir|")
    command = "GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ./zephyr.exe --bt-dev=127.0.0.1:9000"
    
    # Open a new terminal window and execute the command
    p = subprocess.Popen(command, shell=True)
    return p


async def run_controller():
    logger.info('>>> Waiting connection to HCI...')
    find_and_kill_processes(9000)
    async with await open_transport_or_link("tcp-server:127.0.0.1:9000") as (hci_source, hci_sink):

        # Create a local communication channel between multiple controllers
        link = LocalLink()

        # Create a first controller for connection with host interface (Zephyr)
        zephyr_controller = Controller('Zephyr', host_source=hci_source,
                                    host_sink=hci_sink,
                                    link=link)


        # Create our own device (tester central) to manage the host BLE stack
        device = Device.from_config_file('|bluetooth_dir|/tester_config.json')
        # Create a host for the second controller
        device.host = Host() 
        # Create a second controller for connection with this test driver (Bumble)
        device.host.controller = Controller('Fuzzer', link=link)
        # Connect class to receive events during communication with target
        device.listener = TargetEventsListener()
        
        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning() # this calls "on_advertisement"

        logger.info('Waiting Advertisment from BLE Target')
        
        # initialing target
        p = run_target()
        
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning() # Stop scanning for targets

        logger.info(color('\n[OK] Got Advertisment from BLE Target!', 'green'))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        logger.info(f'=== Connecting to {target_address}...')
        await device.connect(target_address) # this calls "on_connection"
        
        
        # Wait in an infinite loop
        await hci_source.wait_for_termination()
        
if __name__ == "__main__":         
    asyncio.run(run_controller())