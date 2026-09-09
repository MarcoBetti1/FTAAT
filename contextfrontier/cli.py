import argparse
import json
import os
from pathlib import Path
from .tasks import make_case, make_suite
from .runner import run, validate
from .report import report
from .providers import local_text_tokens


def main():
    from dotenv import load_dotenv
    load_dotenv(Path.cwd() / ".env", override=False)
    parser = argparse.ArgumentParser(description="ContextFrontier / FTAAT reproducible context games")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("doctor", help="Check key presence without exposing credentials")
    p = sub.add_parser("example")
    p.add_argument("--task", default="needle")
    p = sub.add_parser("tokens", help="Model-specific LOCAL text count, not an API request count")
    p.add_argument("--model", required=True)
    p.add_argument("--file", required=True)
    for command in ("plan", "run"):
        p = sub.add_parser(command)
        p.add_argument("config")
        p.add_argument("--output", required=True)
        p.add_argument("--budget", type=float, required=True)
        if command == "run":
            p.add_argument("--live", action="store_true", help="Allow paid API calls; otherwise dry run")
    p = sub.add_parser("report")
    p.add_argument("directory")
    args = parser.parse_args()
    if args.command == "doctor":
        result = {key: "set" if os.environ.get(key) else "missing" for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")}
    elif args.command == "example":
        result = make_case(args.task, n=8, seed=7).to_dict()
    elif args.command == "tokens":
        result = local_text_tokens(args.model, Path(args.file).read_text())
    elif args.command == "report":
        result = report(args.directory)
    else:
        config = json.loads(Path(args.config).read_text())
        result = run(config, args.output, args.budget, live=getattr(args, "live", False))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
