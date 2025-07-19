import io
import os
import tempfile

def last_lines(filename, buffer_size=io.DEFAULT_BUFFER_SIZE):
    with open(filename, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        buffer = b''
        position = file_size

        while position > 0:
            read_size = min(buffer_size, position)
            position -= read_size
            f.seek(position)
            chunk = f.read(read_size)
            buffer = chunk + buffer

            try:
                text = buffer.decode('utf-8')
            except UnicodeDecodeError:
                # Encontramos caractere UTF-8 cortado — ler mais dados
                continue

            lines = text.splitlines(keepends=True)
            # Se não estamos no início do arquivo, a primeira linha pode estar incompleta
            if position > 0 and not text.startswith(('\n', '\r')):
                buffer = lines.pop(0).encode('utf-8')
            else:
                buffer = b''

            for line in reversed(lines):
                yield line

        if buffer:
            try:
                yield buffer.decode('utf-8')
            except UnicodeDecodeError:
                pass

def normalize_newlines(lines):
    return [line.replace('\r\n', '\n') for line in lines]

def test_last_lines():
    buffer_sizes = [4, 8, 16, 32, io.DEFAULT_BUFFER_SIZE]

    test_cases = [
        {
            "name": "Simple three lines",
            "content": "This is a file\nThis is line 2\nAnd this is line 3\n",
            "expected": [
                "And this is line 3\n",
                "This is line 2\n",
                "This is a file\n",
            ]
        },
        {
            "name": "No newline at EOF",
            "content": "line1\nline2\nline3",
            "expected": [
                "line3",
                "line2\n",
                "line1\n"
            ]
        },
        {
            "name": "Empty file",
            "content": "",
            "expected": []
        },
        {
            "name": "Single line with newline",
            "content": "only one line\n",
            "expected": ["only one line\n"]
        },
        {
            "name": "Single line without newline",
            "content": "lonely line",
            "expected": ["lonely line"]
        },
        {
            "name": "UTF-8 with accents",
            "content": "café\nmañana\nfaçade\n",
            "expected": ["façade\n", "mañana\n", "café\n"]
        }
    ]

    for case in test_cases:
        for buf in buffer_sizes:
            with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as f:
                f.write(case["content"])
                f.flush()
                file_path = f.name

            try:
                result = list(last_lines(file_path, buffer_size=buf))
                result_norm = normalize_newlines(result)
                assert result_norm == case["expected"], (
                    f"❌ {case['name']} failed with buffer_size={buf}\n"
                    f"Expected: {case['expected']}\nGot:      {result}"
                )
                print(f"✅ {case['name']} passed with buffer_size={buf}")
            finally:
                os.remove(file_path)

# Run the tests
if __name__ == "__main__":
    test_last_lines()