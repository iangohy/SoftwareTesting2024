#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
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

class TargetEventsListener(Device.Listener):

    def __init__(self, ble_inputs):
        self.got_advertisement = False
        self.advertisement = None
        self.connection = None
        self.ble_inputs = ble_inputs
        self.status = 0
    
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
            # logging.info("=====Write Timeout=====")
            outputs = '[X] Write Timeout'
            
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
            outputs ='[!] Read Timeout'
        
        return outputs

    def on_advertisement(self, advertisement):
        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        # logging.info("=====Connected=====")
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        # logging.info('=== Discovering services')
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

        # logging.info("=====Services discovered=====")
        show_services(target.services)
        
        
        # -------- Main interaction with the target here --------
        logging.info('=== Read/Write Attributes (Handles)')
        for i in range(len(attributes)):
            logging.info("==================================")
            logging.info(target)
            logging.info(attributes[i])
            response_write = await self.write_target(target, attributes[i], self.ble_inputs["byte"])
            response_read = await self.read_target(target, attributes[i])
            logging.info("response_write:"+response_write)
            logging.info("response_read:"+response_read)
            if i == len(attributes) -1:
                self.status = 1
        logging.info('---------------------------------------------------------------')
        logging.info('[OK] Communication Finished')
        logging.info('---------------------------------------------------------------')
        
        # ---------------------------------------------------
        
        
class BluetoothTestDriver(Device.Listener):
    def __init__(self, tester_config_dir):
        self.server_url = "http://127.0.0.1:9000/"
        self.tester_config_dir = tester_config_dir
        self.task_map = {}
        self.taskStatus = 0
        self.targetPid = 0
        self.controllerPid = 0
        
    async def run_target(self):
        command = "GCOV_PREFIX=$(pwd) GCOV_PREFIX_STRIP=3 ../SoftwareTestingRepo/bluetooth/zephyr.exe --bt-dev=127.0.0.1:9000"
        Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
    
    async def run_coverage(self):
        command = "lcov --capture --directory ../SoftwareTestingRepo/bluetooth/ --output-file ../SoftwareTestingRepo/bluetooth/lcov.info -q --rc lcov_branch_coverage=1"
        Popen(command, stdout=PIPE, stderr=STDOUT, text=True, shell=True, start_new_session=True)
        logging.info('[OK] Coverage Done')
    
    async def run_test_with_controller(self, input):
        task1 = asyncio.create_task(self.run_test(input))
        await task1
        # try:
        #     task1 = asyncio.create_task(self.run_test(input))
            
        #     while self.taskStatus == 1:
        #         task1.cancel()
        #         self.taskStatus = 0
                
        #     self.controllerPid = await task1
        # except Exception as ex:
        #     logging.exception("An error occurred while running the task")  # Log the exception
        #     print("Task canceled")
    
    
        
    async def run_test(self, mutated_input, coverage=False):
        logging.info("\n\n\nAsync function is starting...")
        
        async with await open_transport_or_link('tcp-server:127.0.0.1:9000') as (hci_source, hci_sink):
            logging.info('>>> Connected to HCI')
            
            # Create a local communication channel between multiple controllers
            link = LocalLink()

            # Create a first controller for connection with host interface (Zephyr)
            zephyr_controller = Controller('Zephyr', host_source=hci_source,
                                    host_sink=hci_sink,
                                    link=link)


            # Create our own device (tester central) to manage the host BLE stack
            device = Device.from_config_file(self.tester_config_dir)
            # Create a host for the second controller
            device.host = Host() 
            
            # Create a second controller for connection with this test driver (Bumble)
            device.host.controller = Controller('Fuzzer', link=link)
            
            # Connect class to receive events during communication with target            
            # fuzzed input pass to targetevent listener
            device.listener = TargetEventsListener(mutated_input) 
            
            # Start BLE scanning here
            await device.power_on()
            await device.start_scanning() # this calls "on_advertisement"

            logging.info('Waiting Advertisment from BLE Target')
            
            # initialing target
            await self.run_target()
            
            while device.listener.got_advertisement is False:
                await asyncio.sleep(0.5)
            await device.stop_scanning() # Stop scanning for targets

            logging.info('[OK] Got Advertisment from BLE Target!')
            target_address = device.listener.advertisement.address

            # Start BLE connection here
            logging.info(f'=== Connecting to {target_address}...')
            await device.connect(target_address) # this calls "on_connection"
        
            # if done
            while device.listener.status == 0:
                await asyncio.sleep(0.5)
                
            #  disconnect device
            await device.disconnect(device.listener.connection, reason=0)
            logging.info('[OK] Disconnected!')
            
            transport = Transport(hci_source, hci_sink)
            await transport.close()

            # if coverage:
            #     await self.run_coverage()
            
            # self.taskStatus = 1
            
            # Wait in an infinite loop
            # await hci_source.wait_for_termination()
        
    
    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0
    
    

# Usage
if __name__ == "__main__":     
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    driver = BluetoothTestDriver("../SoftwareTestingRepo/bluetooth/tester_config.json")
    
    inputs = [ [0x05],  [0x06], [0xF5], [0xD5], [0xE5]]
    # Example
    for i in range(5):
        asyncio.run(driver.run_test_with_controller({"byte": inputs[i]}))  
        # if driver.taskStatus == 1:
        #     subprocess.run(["kill", "-9", str(driver.targetPid)])
        #     driver.taskStatus = 0
        
        