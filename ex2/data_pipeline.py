import abc
import typing


class ExportPlugin(typing.Protocol):
    def process_output(self, data: list[tuple[int, str]]) -> None:
        ...


class CSVExportPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("CSV Output:")
        print(",".join(v for k, v in data))


class JSONExportPlugin:
    def process_output(self, data: list[tuple[int, str]]) -> None:
        print("JSON Output:")
        items = [f'"item_{k}": "{v}"' for k, v in data]
        print("{" + ", ".join(items) + "}")


class DataProcessor(abc.ABC):
    def __init__(self) -> None:
        self.processed_data: list[tuple[int, str]] = []
        self.total_processed: int = 0

    @abc.abstractmethod
    def validate(self, data: typing.Any) -> bool:
        pass

    @abc.abstractmethod
    def ingest(self, data: typing.Any) -> None:
        pass

    def output(self) -> typing.Optional[tuple[int, str]]:
        if self.processed_data:
            return self.processed_data.pop(0)
        return None


class NumericProcessor(DataProcessor):
    def validate(self, data: typing.Any) -> bool:
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

    def ingest(self, data: typing.Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")

        if isinstance(data, list):
            for item in data:
                self.processed_data.append((self.total_processed, str(item)))
                self.total_processed += 1
        else:
            self.processed_data.append((self.total_processed, str(data)))
            self.total_processed += 1


class TextProcessor(DataProcessor):
    def validate(self, data: typing.Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, str):
                    return False
            return True
        return False

    def ingest(self, data: typing.Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")

        if isinstance(data, list):
            for item in data:
                self.processed_data.append((self.total_processed, str(item)))
                self.total_processed += 1
        else:
            self.processed_data.append((self.total_processed, str(data)))
            self.total_processed += 1


class LogProcessor(DataProcessor):
    def validate(self, data: typing.Any) -> bool:
        if isinstance(data, dict):
            return 'log_level' in data and 'log_message' in data
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    return False
                if 'log_level' not in item or 'log_message' not in item:
                    return False
            return True
        return False

    def ingest(self, data: typing.Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")

        if isinstance(data, list):
            for item in data:
                lvl = item['log_level']
                msg = item['log_message']
                val = f"{lvl}: {msg}"
                self.processed_data.append((self.total_processed, val))
                self.total_processed += 1
        elif isinstance(data, dict):
            lvl = data['log_level']
            msg = data['log_message']
            val = f"{lvl}: {msg}"
            self.processed_data.append((self.total_processed, val))
            self.total_processed += 1


class DataStream:
    def __init__(self) -> None:
        self.processors: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self.processors.append(proc)

    def process_stream(self, stream: list[typing.Any]) -> None:
        for element in stream:
            processed = False
            for proc in self.processors:
                if proc.validate(element):
                    proc.ingest(element)
                    processed = True
                    break

            if not processed:
                print(
                    "DataStream error - Can't process element "
                    f"in stream: {element}"
                )

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self.processors:
            print("No processor found, no data")
            return

        for proc in self.processors:
            name = proc.__class__.__name__.replace("Processor", " Processor")
            total = proc.total_processed
            rem = len(proc.processed_data)
            print(
                f"{name}: total {total} items processed, "
                f"remaining {rem} on processor"
            )

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self.processors:
            collected: list[tuple[int, str]] = []
            for _ in range(nb):
                val = proc.output()
                if val is not None:
                    collected.append(val)

            if collected:
                plugin.process_output(collected)


def main() -> None:
    print("=== Code Nexus - Data Pipeline ===")
    print("Initialize Data Stream...")
    stream = DataStream()

    stream.print_processors_stats()

    print("Registering Processors")
    num_proc = NumericProcessor()
    txt_proc = TextProcessor()
    log_proc = LogProcessor()

    stream.register_processor(num_proc)
    stream.register_processor(txt_proc)
    stream.register_processor(log_proc)

    batch1: list[typing.Any] = [
        'Hello world',
        [3.14, -1, 2.71],
        [
            {
                'log_level': 'WARNING',
                'log_message': 'Telnet access! Use ssh instead'
            },
            {
                'log_level': 'INFO',
                'log_message': 'User wil is connected'
            }
        ],
        42,
        ['Hi', 'five']
    ]

    print(
        "Send first batch of data on stream: "
        "['Hello world', [3.14, -1, 2.71], [{'log_level': 'WARNING', "
        "'log_message': 'Telnet access! Use ssh instead'}, "
        "{'log_level': 'INFO', 'log_message': 'User wil is connected'}], "
        "42, ['Hi', 'five']]"
    )

    stream.process_stream(batch1)
    stream.print_processors_stats()

    print("Send 3 processed data from each processor to a CSV plugin:")
    csv_plugin = CSVExportPlugin()
    stream.output_pipeline(3, csv_plugin)

    stream.print_processors_stats()

    batch2: list[typing.Any] = [
        21,
        ['I love AI', 'LLMs are wonderful', 'Stay healthy'],
        [
            {'log_level': 'ERROR', 'log_message': '500 server crash'},
            {
                'log_level': 'NOTICE',
                'log_message': 'Certificate expires in 10 days'
            }
        ],
        [32, 42, 64, 84, 128, 168],
        'World hello'
    ]

    print(
        "Send another batch of data: "
        "[21, ['I love AI', 'LLMs are wonderful', 'Stay healthy'], "
        "[{'log_level': 'ERROR', 'log_message': '500 server crash'}, "
        "{'log_level': 'NOTICE', "
        "'log_message': 'Certificate expires in 10 days'}], "
        "[32, 42, 64, 84, 128, 168], 'World hello']"
    )

    stream.process_stream(batch2)
    stream.print_processors_stats()

    print("Send 5 processed data from each processor to a JSON plugin:")
    json_plugin = JSONExportPlugin()
    stream.output_pipeline(5, json_plugin)

    stream.print_processors_stats()


if __name__ == "__main__":
    main()
