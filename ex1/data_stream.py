from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class DataStream:
    def __init__(self) -> None:
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self.processors.append(proc)

    def process_stream(self, stream: list[typing.Any]) -> None:
        for element in stream:
            processed = False
            for processor in self.processors:
                if processor.validate(element):
                    processor.ingest(element)
                    processed = True
                    break
            if not processed:
                print(f"DataStream error - Can't process element in stream: {element}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self.processors:
            print("No processors found, no data")
            return
        for processor in self.processors:
            name = processor.__class__.__name__.replace("Processor", "Processor")
            total = processor.total_processed
            remaining = len(processor.processed_data)
            print(f"{name}: total {total} items processed, remaining {remaining} on processor")

def data_stream() -> None:
    print("=== Code Nexus - Data Stream ===\n")
    print("Initialize Data Stream...")
    stream = DataStream()

    stream.print_processor_stats()

    print("Registering Numeric Processor")
    num_proc = NumericProcessor()
    stream.register_processor(num_proc)
    batch = [
        'Hello world', 
        [3.14, -1, 2.71], 
        [{'log_level': 'WARNING', 'log_message': 'Telnet access! Use ssh instead'}, 
         {'log_level': 'INFO', 'log_message': 'User wil is connected'}], 
        42, 
        ['Hi', 'five']
    ]

    print(f"Send first batch of data on stream: {batch}")
    stream.process_stream(batch)
    stream.print_processors_stats()

    print("Registering other data processors")
    txt_proc = TextProcessor()
    log_proc = LogProcessor()
    stream.register_processor(txt_proc)
    stream.register_processor(log_proc)

    print("Send the same batch again")
    stream.process_stream(batch)
    stream.print_processor_stats()

    print("Consume some elements from the data processors: Numeric 3, Text 2, Log 1")
    for _ in range(3):
        num_proc.output()
    for _ in range(2):
        txt_proc.output(2)
    for _ in range(1):
        log_proc.output()
    stream.print_processors_stats()


if __name__ == "__main__":
    data_stream()
