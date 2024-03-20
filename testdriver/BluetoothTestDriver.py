#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import logging
import asyncio
import sys
import os
from binascii import hexlify


from bumble.device import Device, Peer
from bumble.host import Host
from bumble.gatt import show_services
from bumble.core import ProtocolError
from bumble.controller import Controller
from bumble.link import LocalLink
from bumble.transport import open_transport_or_link
from bumble.utils import AsyncRunner
from bumble.colors import color
import logging

class BluetoothTestDriver(Device.Listener):
    def __init__(self):
        self.server_url = "http://127.0.0.1:9000/"
        self.got_advertisement = False
        self.advertisement = None
        self.connection = None
    
    # oracle to pass in
    async def run_test(self, target, attribute, type, bytes):
        """
        used by oracle 
        """

        response = None
                
        # dummy
        if type:
            # example write
            response = await self.write_target(target, attribute, bytes)
        else:
            # example read
            response = await self.read_target(target, attribute)
        
        logging.debug("======RESPONSE======")
        logging.debug(response)
        logging.debug("======RESPONSE======")
        self.analyze_results(response)
            

    def analyze_results(self, response):
        # Analyze the results of the server response
        pass
    
    def interpret(self, input_data):
        # interpret ASCII to fit to request
        
        return 0

    def on_advertisement(self, advertisement):

        # logging.debug(f'{color("Advertisement", "cyan")} <-- 'f'{color(advertisement.address, "yellow")}')
        
        # Indicate that an from target advertisement has been received
        self.advertisement = advertisement
        self.got_advertisement = True

    @AsyncRunner.run_in_task()
    # pylint: disable=invalid-overridden-method
    async def on_connection(self, connection):
        # logging.debug(color(f'[OK] Connected!', 'green'))
        self.connection = connection

        # Discover all attributes (services, characteristitcs, descriptors, etc)
        # logging.debug('=== Discovering services')
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

        # logging.debug(color('[OK] Services discovered', 'green'))
        show_services(target.services)
        
        # -------- Main interaction with the target here --------
        # logging.debug('=== Read/Write Attributes (Handles)')
        for attribute in attributes:
            await self.run_test(target, attribute, 1, [0x01])
            await self.run_test(target, attribute, 0, [])
        
        logging.debug('---------------------------------------------------------------')
        logging.debug('[OK] Communication Finished')
        logging.debug('---------------------------------------------------------------')
        # ---------------------------------------------------
        
    
    async def write_target(self, target, attribute, bytes):
        # Write data to bluetooth target
        outputs = []
        try:
            bytes_to_write = bytearray(bytes)
            await target.write_value(attribute, bytes_to_write, True)
            # logging.debug(color(f'[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}', 'green'))
            outputs.append(f'[OK] WRITE Handle 0x{attribute.handle:04X} --> Bytes={len(bytes_to_write):02d}, Val={hexlify(bytes_to_write).decode()}')
            return True
        except ProtocolError as error:
            # logging.debug(color(f'[!]  Cannot write attribute 0x{attribute.handle:04X}:', 'yellow'), error)
            outputs.append(f'[!]  Cannot write attribute 0x{attribute.handle:04X}:')
        except TimeoutError:
            # logging.debug(color('[X] Write Timeout', 'red'))
            outputs.append('[X] Write Timeout')
            
        return outputs


    async def read_target(self, target, attribute):
        # Read data from bluetooth target
        outputs = []
        try: 
            read = await target.read_value(attribute)
            value = read.decode('latin-1')
            # logging.debug(color(f'[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}', 'cyan'))
            outputs.append(f'[OK] READ  Handle 0x{attribute.handle:04X} <-- Bytes={len(read):02d}, Val={read.hex()}')
            return value
        except ProtocolError as error:
            # logging.debug(color(f'[!]  Cannot read attribute 0x{attribute.handle:04X}:', 'yellow'), error)
            outputs.append(f'[!]  Cannot read attribute 0x{attribute.handle:04X}:')
        except TimeoutError:
            # logging.debug(color('[!] Read Timeout'))
            outputs.append('[!] Read Timeout')
        
        return outputs

# -----------------------------------------------------------------------------
# How oracle will run the test driver first i guess
async def main():
    if len(sys.argv) != 2:
        # logging.debug('Usage: run_controller.py <transport-address>')
        # logging.debug('example: ./run_ble_tester.py tcp-server:0.0.0.0:9000')
        return

    # logging.debug('>>> Waiting connection to HCI...')
    async with await open_transport_or_link(sys.argv[1]) as (hci_source, hci_sink):
        # logging.debug('>>> Connected')

        # Create a local communication channel between multiple controllers
        link = LocalLink()

        # Create a first controller for connection with host interface (Zephyr)
        zephyr_controller = Controller('Zephyr', host_source=hci_source,
                                 host_sink=hci_sink,
                                 link=link)


        # Create our own device (tester central) to manage the host BLE stack
        device = Device.from_config_file('../../SoftwareTestingRepo/bluetooth/tester_config.json')
        # Create a host for the second controller
        device.host = Host() 
        # Create a second controller for connection with this test driver (Bumble)
        device.host.controller = Controller('Fuzzer', link=link)
        # Connect class to receive events during communication with target
        device.listener = BluetoothTestDriver()
        
        # Start BLE scanning here
        await device.power_on()
        await device.start_scanning() # this calls "on_advertisement"

        # logging.debug('Waiting Advertisment from BLE Target')
        while device.listener.got_advertisement is False:
            await asyncio.sleep(0.5)
        await device.stop_scanning() # Stop scanning for targets

        # logging.debug(color('\n[OK] Got Advertisment from BLE Target!', 'green'))
        target_address = device.listener.advertisement.address

        # Start BLE connection here
        # logging.debug(f'=== Connecting to {target_address}...')
        await device.connect(target_address) # this calls "on_connection"
        
        # Wait in an infinite loop
        await hci_source.wait_for_termination()




# Usage
if __name__ == "__main__":     
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)
    # -----------------------------------------------------------------------------
    logging.basicConfig(level=os.environ.get('BUMBLE_LOGLEVEL', 'INFO').upper())
    asyncio.run(main())