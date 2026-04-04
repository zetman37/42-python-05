from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class DataProcessor(ABC):
    def __init__(self) -> None:
        self.processed_data = None

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        return self.processed_data
    
class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)):
            return True

        if isinstance(data, str):
            try:
                float(data)
                return True
            except ValueError:
                return False
                
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, (int, float)):
                    if isinstance(item, str):
                        try:
                            float(item)
                        except ValueError:
                            return False
                    else:
                        return False
            return True
            
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
            
        if isinstance(data, list):
            self.processed_data = [str(item) for item in data]
        else:
            self.processed_data = str(data)

class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if type(data) is str:
            return True
        if type(data) is list:
            for item in data:
                if type(item) is not str:
                    return False
            return True
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        if type(data) is list:
            self.processed_data = [str(item) for item in data]
        else:
            self.processed_data = str(data)

class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if type(data) is dict:
            if 'log_level' in data and 'log_message' in data:
                return True
            return False
        if type(data) is list:
            for item in data:
                if type(item) is not dict:
                    return False
                if 'log_level' not in item or 'log_message' not in item:
                    return False
                return True
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        if type(data) is list:
            self.processed_data = [f"{item['log_level']}: {item['log_message']}" for item in data]
        else:
            self.processed_data = f"{data['log_level']}: {data['log_message']}"

def num_processor():
    print("\nTesting Numeric Processor...")
    processor = NumericProcessor()
    print(f"Trying to validate input '42': {processor.validate('42')}")
    print(f"Trying to validate input 'Hello': {processor.validate('Hello')}")

    print("Testing invalid ingestion of string 'foo' without prior validation:")
    try:
        processor.ingest('foo')
    except Exception as e:
        print(f"Got exception: {e}")
    data_to_process = [1, 2, 3, 4, 5]
    print(f"Processing data: {data_to_process}")
    print("Extracting 3 values...")
    processor.ingest(data_to_process)
    result = processor.output()
    for i in range(3):
        print(f"Numeric value {i}: {result[i]}")

def text_processor() -> None:
    print("\nTesting Text Processor...")
    processor = TextProcessor()
    print(f"Trying to validate input '42': {processor.validate('42')}")
    data_to_process = ['Hello', '42', 'World']
    print(f"Processing data: {data_to_process}")
    print("Extracting 1 value...")
    processor.ingest(data_to_process)
    result = processor.output()
    for i in range(1):
        print(f"Text value {i}: {result[i]}")

def log_processor() -> None:
    print("\nTesting Log Processor...")
    processor = LogProcessor()

    print(f"Trying to validate input 'Hello': {processor.validate('Hello')}")
    data_to_process = [
        {'log_level': 'NOTICE', 'log_message': 'Connection to server'}, 
        {'log_level': 'ERROR', 'log_message': 'Unauthorized access!!'}
    ]
    print(f"Processing data: {data_to_process}")
    print("Extracting 2 values...")
    processor.ingest(data_to_process)
    result = processor.output()
    for i in range(2):
        print(f"Log entry {i}: {result[i]}")

def multiple_process() -> None:
    num_processor()
    text_processor()
    log_processor()

if __name__ == "__main__":
    multiple_process()
