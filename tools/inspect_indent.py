import itertools

p='app.py'
start=2238
end=2265
with open(p, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, start=1):
        if i < start:
            continue
        if i > end:
            break
        leading = line[:len(line)-len(line.lstrip('\r\n '))]
        # show ordinals
        ords = [ord(c) for c in leading]
        print(f"{i:4}: len={len(line.rstrip())} repr={line.rstrip()!r} lead_len={len(leading)} ords={ords}")
