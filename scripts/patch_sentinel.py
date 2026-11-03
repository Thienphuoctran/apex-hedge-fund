import os
import sys

path = 'scripts/intraday_portfolio_sentinel.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()
code = code.replace('\r\n', '\n')

# Check if --market is already there
if '--market' not in code:
    idx = code.find('broadcast-golden-window')
    if idx != -1:
        line_end = code.find('\n', idx)
        arg_add = '\n    parser.add_argument("--market", type=str, default=None, choices=["VN", "US", "ALL"], help="Loc thi truong can giam sat: VN, US, hoac ALL.")'
        code = code[:line_end] + arg_add + code[line_end:]

    target_filter = '    positions = load_all_active_positions()'
    if target_filter in code:
        filter_logic = '''    positions = load_all_active_positions()
    if args.market == "VN":
        positions = [p for p in positions if p["market"] == "VIETNAM"]
    elif args.market == "US":
        positions = [p for p in positions if p["market"] == "US_GLOBAL"]'''
        code = code.replace(target_filter, filter_logic, 1)

    target_daemon = 'current_positions = load_all_active_positions()'
    if target_daemon in code:
        daemon_logic = '''current_positions = load_all_active_positions()
                    if args.market == "VN":
                        current_positions = [p for p in current_positions if p["market"] == "VIETNAM"]
                    elif args.market == "US":
                        current_positions = [p for p in current_positions if p["market"] == "US_GLOBAL"]'''
        code = code.replace(target_daemon, daemon_logic, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully enhanced sentinel with --market support!")
else:
    print("--market already present.")
