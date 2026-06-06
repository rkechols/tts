from pathlib import Path


def scrape():
    p = Path("data/text/asdf.txt")
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        print("Hello, Pohatu!", file=f)


if __name__ == "__main__":
    scrape()
