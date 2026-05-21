def iter_chunks(content: bytes, chunk_size: int):
    for offset in range(0, len(content), chunk_size):
        yield offset // chunk_size, content[offset:offset + chunk_size]
