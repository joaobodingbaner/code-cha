import io
import os
import tempfile


def last_lines(filename: str, buffer_size: int = io.DEFAULT_BUFFER_SIZE, encoding: str = "utf-8"):
    """
    Lê um arquivo de trás para frente, retornando as linhas em ordem reversa.

    Args:
        filename (str): Caminho para o arquivo.
        buffer_size (int): Tamanho do buffer de leitura em bytes.
        encoding (str): Codificação usada para decodificar os bytes.

    Yields:
        str: Linhas do arquivo, da última para a primeira.
    """
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
            buffer = chunk + buffer  # prepend dados

            try:
                text = buffer.decode(encoding)
            except UnicodeDecodeError:
                continue  # Pode ter quebrado caractere multibyte

            lines = text.splitlines(keepends=True)

            if file_pos > 0 and lines:
                incomplete_line = lines.pop(0).encode(encoding)
                buffer = incomplete_line
            else:
                buffer = b''

            for line in reversed(lines):
                yield line

        if buffer:
            try:
                yield buffer.decode(encoding)
            except UnicodeDecodeError:
                pass


def normalize_newlines(lines):
    """
    Normaliza quebras de linha de Windows para Unix.
    """
    return [line.replace('\r\n', '\n') for line in lines]


def create_temp_file(content: str, encoding: str, truncate_last_byte: bool = False) -> str:
    """
    Cria um arquivo temporário com o conteúdo especificado.

    Args:
        content (str): Conteúdo do arquivo.
        encoding (str): Codificação do arquivo.
        truncate_last_byte (bool): Se True, remove o último byte (simula linha incompleta).

    Returns:
        str: Caminho do arquivo temporário.
    """
    if truncate_last_byte:
        encoded = content.encode(encoding)[:-1]
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            f.write(encoded)
            f.flush()
            return f.name
    else:
        with tempfile.NamedTemporaryFile("w+", encoding=encoding, newline='', delete=False) as f:
            f.write(content)
            f.flush()
            return f.name


def run_test_case(case: dict, buffer_size: int):
    """
    Executa um único caso de teste com o buffer especificado.
    """
    path = create_temp_file(
        content=case["content"],
        encoding=case["encoding"],
        truncate_last_byte=case.get("truncate_last_byte", False)
    )

    try:
        result = list(last_lines(path, buffer_size=buffer_size, encoding=case["encoding"]))
        result_norm = normalize_newlines(result)

        assert result_norm == case["expected"], (
            f"❌ {case['name']} failed with buffer_size={buffer_size}\n"
            f"Expected: {case['expected']}\nGot:      {result}"
        )
        print(f"✅ {case['name']} passed with buffer_size={buffer_size}")
    finally:
        os.remove(path)


def test_last_lines():
    """
    Executa uma bateria de testes em diferentes cenários e tamanhos de buffer.
    """
    buffer_sizes = [4, 8, 16, 32, io.DEFAULT_BUFFER_SIZE]

    test_cases = [
        {
            "name": "Simple three lines",
            "content": "This is a file\nThis is line 2\nAnd this is line 3\n",
            "expected": ["And this is line 3\n", "This is line 2\n", "This is a file\n"],
            "encoding": "utf-8"
        },
        {
            "name": "No newline at EOF",
            "content": "line1\nline2\nline3",
            "expected": ["line3", "line2\n", "line1\n"],
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
            "content": "This is a test.\nLast line is incomplete: 文字化け\n",
            "expected": [
                "Last line is incomplete: 文字化け",
                "This is a test.\n"
            ],
            "encoding": "utf-8",
            "truncate_last_byte": True
        }
    ]

    for case in test_cases:
        for buffer_size in buffer_sizes:
            run_test_case(case, buffer_size)


if __name__ == "__main__":
    test_last_lines()
