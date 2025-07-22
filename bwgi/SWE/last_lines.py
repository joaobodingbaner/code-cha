import io
import os
import tempfile

def last_lines(filename, buffer_size=io.DEFAULT_BUFFER_SIZE, encoding="utf-8"):
    with open(filename, 'rb') as f:
        f.seek(0, os.SEEK_END)
        file_pos = f.tell()
        buffer = b''
        incomplete_line = b''

        while file_pos > 0:
            read_size = min(buffer_size, file_pos)
            file_pos -= read_size
            f.seek(file_pos)
            chunk = f.read(read_size)

            buffer = chunk + buffer  # prepend chunk aos dados já acumulados

            try:
                text = buffer.decode(encoding)
            except UnicodeDecodeError:
                # Pode estar cortando caractere multibyte, ler mais dados
                continue

            lines = text.splitlines(keepends=True)

            # A primeira linha (linha mais antiga, no começo do arquivo) pode estar incompleta
            # Salvamos ela no buffer para próxima iteração, removendo do yield
            if file_pos > 0 and lines:
                incomplete_line = lines.pop(0).encode(encoding)
                buffer = incomplete_line
            else:
                buffer = b''

            for line in reversed(lines):
                yield line

        # Após ler tudo, se sobrou linha incompleta, yield ela (decodificada)
        if buffer:
            try:
                yield buffer.decode(encoding)
            except UnicodeDecodeError:
                pass




def test_last_lines():
    buffer_sizes = [4, 8, 16, 32, io.DEFAULT_BUFFER_SIZE]

    basic_cases = [
        {
            "name": "Simple three lines",
            "content": "This is a file\nThis is line 2\nAnd this is line 3\n",
            "expected": [
                "And this is line 3\n",
                "This is line 2\n",
                "This is a file\n",
            ],
            "encoding": "utf-8"
        },
        {
            "name": "No newline at EOF",
            "content": "line1\nline2\nline3",
            "expected": [
                "line3",
                "line2\n",
                "line1\n"
            ],
            "encoding": "utf-8"
        },
        {
            "name": "Empty file",
            "content": "",
            "expected": [],
            "encoding": "utf-8"
        },
        {
            "name": "Single line with newline",
            "content": "only one line\n",
            "expected": ["only one line\n"],
            "encoding": "utf-8"
        },
        {
            "name": "Single line without newline",
            "content": "lonely line",
            "expected": ["lonely line"],
            "encoding": "utf-8"
        },
        {
            "name": "UTF-8 with accents",
            "content": "café\nmañana\nfaçade\n",
            "expected": ["façade\n", "mañana\n", "café\n"],
            "encoding": "utf-8"
        },
        {
            "name": "Latin1 encoding",
            "content": "Olá\nMundo\nAté logo\n",
            "expected": ["Até logo\n", "Mundo\n", "Olá\n"],
            "encoding": "latin1"
        },
        {
            "name": "UTF-8 incomplete last line",
            # Texto com caracteres multibyte no final, truncado no último byte
            "content": "This is a test.\nLast line is incomplete: 文字化け\n",
            "expected": [
                "Last line is incomplete: 文字化け",
                "This is a test.\n"
            ],
            "encoding": "utf-8",
            "truncate_last_byte": True  # sinal para truncar no teste
        }
    ]

    # windows
    def normalize_newlines(lines):
        return [line.replace('\r\n', '\n') for line in lines]

    for case in basic_cases:
        for buf in buffer_sizes:
            # Cria arquivo temporário
            if case.get("truncate_last_byte"):
                # Codifica e trunca o último byte
                encoded = case["content"].encode(case["encoding"])[:-1]
                with tempfile.NamedTemporaryFile("wb", delete=False) as f:
                    f.write(encoded)
                    f.flush()
                    path = f.name
            else:
                with tempfile.NamedTemporaryFile("w+", encoding=case["encoding"], newline='', delete=False) as f:
                    f.write(case["content"])
                    f.flush()
                    path = f.name

            try:
                result = list(last_lines(path, buffer_size=buf, encoding=case["encoding"]))
                result_norm = normalize_newlines(result)
                assert result_norm == case["expected"], (
                    f"❌ {case['name']} failed with buffer_size={buf}\n"
                    f"Expected: {case['expected']}\nGot:      {result}"
                )
                print(f"✅ {case['name']} passed with buffer_size={buf}")
            finally:
                os.remove(path)

if __name__ == "__main__":
    test_last_lines()
