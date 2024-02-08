from generalFuzzer import *

def main():
    host = "127.0.0.1"
    port = 5683

    fuzzer = GeneralFuzzer(host, port)
    #while(1):
    #    try:
    fuzzer.fuzz_and_send_requests_django(num_requests=3, num_bytes=5)
    #    except:
    fuzzer.close_connection()

if __name__ == "__main__":
    main()
