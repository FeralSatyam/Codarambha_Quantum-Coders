import yaml
from pathlib import Path

def main():
    cfg = yaml.safe_load(Path("config/config.yaml").read_text())
    print("Loaded config for:", cfg["intersection"]["name"])
    print("Approaches:", [a["id"] for a in cfg["intersection"]["approaches"]])
    print("Strategy:", cfg["control"]["strategy"])

if __name__ == "__main__":
    main()