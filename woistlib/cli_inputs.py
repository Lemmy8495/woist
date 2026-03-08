from pathlib import Path


def uniq(values: list[str]) -> list[str]:
    out = []
    for value in values:
        if value not in out:
            out.append(value)
    return out


def normalize_target(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Kein Ziel übergeben.")

    for prefix in ("http://", "https://"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]

    if "/" in cleaned:
        cleaned = cleaned.split("/", 1)[0]

    if cleaned.startswith("[") and "]" in cleaned:
        cleaned = cleaned[1:].split("]", 1)[0]
    elif cleaned.count(":") == 1 and not cleaned.replace(":", "").isdigit():
        cleaned = cleaned.rsplit(":", 1)[0]

    return cleaned.strip().rstrip(".")


def read_targets(single_targets: list[str], file_path: str | None) -> list[str]:
    targets: list[str] = []
    targets.extend(single_targets)

    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"Datei nicht gefunden: {file_path}")

        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                targets.append(line)

    targets = uniq(targets)

    if not targets:
        raise ValueError("Keine Ziele angegeben.")

    return targets


def parse_ports(value: str | None) -> list[int] | None:
    if value is None:
        return None

    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Portliste ist leer.")

    ports: list[int] = []
    for raw_part in cleaned.split(","):
        part = raw_part.strip()
        if not part:
            raise ValueError("Ungültige Portliste: leere Elemente sind nicht erlaubt.")

        if "-" in part:
            start_raw, end_raw = part.split("-", 1)
            if not start_raw.isdigit() or not end_raw.isdigit():
                raise ValueError(f"Ungültiger Portbereich: {part}")

            start = int(start_raw)
            end = int(end_raw)
            if start > end:
                raise ValueError(f"Ungültiger Portbereich: {part}")
            if start < 1 or end > 65535:
                raise ValueError(f"Port außerhalb des gültigen Bereichs (1-65535): {part}")
            ports.extend(range(start, end + 1))
            continue

        if not part.isdigit():
            raise ValueError(f"Ungültiger Port: {part}")

        port = int(part)
        if port < 1 or port > 65535:
            raise ValueError(f"Port außerhalb des gültigen Bereichs (1-65535): {part}")
        ports.append(port)

    if not ports:
        raise ValueError("Portliste ist leer.")

    return sorted(set(ports))

