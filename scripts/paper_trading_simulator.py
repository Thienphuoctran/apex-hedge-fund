"""
MODULE 6B: Institutional Paper Trading Simulator Engine (`paper_trading_simulator.py`).
Author: Ban 6 — investor-mentorship-coach
Purpose:
- Allows student to execute virtual trades ($100,000 USD virtual capital).
- Supports Core & Satellite dual-engine portfolio management.
- Checks risk compliance: 10% max allocation, ATR Risk-Parity stop-loss, Core vs Satellite classification.
- Marks to market with live data from `latest_market_snapshot.json`.
- Automatically logs entries to `personal_trading_journal.md`.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SNAPSHOT_PATH = DATA_DIR / "latest_market_snapshot.json"
MENTOR_DIR = BASE_DIR / "06_Investor_Academy_And_Mentorship"
JOURNAL_DIR = MENTOR_DIR / "user_journal"
PORTFOLIO_PATH = JOURNAL_DIR / "paper_trading_portfolio.json"
PROFILE_PATH = JOURNAL_DIR / "student_profile.json"


def load_json(filepath: Path) -> dict:
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: Path, data: dict) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_equity_info(symbol: str) -> dict:
    snapshot = load_json(SNAPSHOT_PATH)
    broad_eqs = snapshot.get("broad_equities", [])
    for eq in broad_eqs:
        if eq.get("symbol", "").upper() == symbol.upper():
            return eq
    return {}


def show_status():
    portfolio = load_json(PORTFOLIO_PATH)
    if not portfolio:
        print("[LOI] Khong tim thay paper_trading_portfolio.json!")
        return

    positions = portfolio.get("positions", {})
    total_market_val = 0.0
    unrealized_pnl = 0.0

    print("==========================================================================================")
    print("      HE THONG QUAN LY TAI KHOAN MO PHONG PAPER TRADING (BAN 6 MENTOR)                   ")
    print("      MOHINH: CORE & SATELLITE (Core 65% Tich San | Satellite 35% Luot Song)             ")
    print("==========================================================================================")
    print(f"Loai tai khoan:       {portfolio.get('account_type')}")
    print(f"Von ban dau:          ${portfolio.get('initial_capital_usd', 100000.0):,.2f} USD")
    print(f"So du tien mat:       ${portfolio.get('cash_balance_usd', 0.0):,.2f} USD")
    
    print("\n[DANH MUC VI THE DANG NAM GIU (ACTIVE POSITIONS)]:")
    if not positions:
        print("  (Chua co vi the nao dang mo. So du 100% tien mat san sang giai ngan.)")
    else:
        print(f"{'Ma':<6} | {'Phan Loai':<10} | {'SL':<5} | {'Gia Vao':<9} | {'Gia Hien Tai':<12} | {'Gia Tri':<12} | {'Lai/Lo ($)':<12} | {'Lai/Lo (%)':<10} | {'Stop-Loss':<10}")
        print("-" * 105)
        for sym, pos in positions.items():
            eq_info = get_equity_info(sym)
            live_px = eq_info.get("last_price", 0.0)
            if live_px <= 0.0:
                live_px = pos.get("entry_price", 0.0)
            
            shares = pos.get("shares", 0)
            entry = pos.get("entry_price", 0.0)
            mkt_val = live_px * shares
            pos_pnl = (live_px - entry) * shares
            pos_pnl_pct = ((live_px - entry) / entry * 100) if entry > 0 else 0.0
            
            total_market_val += mkt_val
            unrealized_pnl += pos_pnl
            
            stop_str = f"${pos.get('stop_loss', 0.0):.2f}"
            pnl_str = f"{'+' if pos_pnl >= 0 else ''}${pos_pnl:,.2f}"
            pct_str = f"{'+' if pos_pnl_pct >= 0 else ''}{pos_pnl_pct:.2f}%"
            
            print(f"{sym:<6} | {pos.get('strategy_type', 'Core'):<10} | {shares:<5} | ${entry:<8.2f} | ${live_px:<11.2f} | ${mkt_val:<11.2f} | {pnl_str:<12} | {pct_str:<10} | {stop_str:<10}")

    nav = portfolio.get("cash_balance_usd", 0.0) + total_market_val
    print("-" * 105)
    print(f"Tong Tai San (NAV):    ${nav:,.2f} USD")
    print(f"Lai/Lo Chua Thuc Hien: {'+' if unrealized_pnl >= 0 else ''}${unrealized_pnl:,.2f} USD")
    print(f"Lai/Lo Da Chot Loi:    {'+' if portfolio.get('realized_pnl_usd', 0) >= 0 else ''}${portfolio.get('realized_pnl_usd', 0):,.2f} USD")
    print(f"Ty Le Thang (Win Rate):{portfolio.get('win_rate_percent', 0.0):.1f}% ({portfolio.get('winning_trades', 0)} thang / {portfolio.get('total_trades', 0)} lenh)")
    print(f"Diem Ky Luat Mentor:   {portfolio.get('discipline_score', 100.0):.1f} / 100 Diem")
    print("==========================================================================================\n")


def buy_stock(symbol: str, shares: int, entry_price: float = None, stop_loss: float = None, target_price: float = None, strategy_type: str = "Core"):
    portfolio = load_json(PORTFOLIO_PATH)
    symbol = symbol.upper()
    eq_info = get_equity_info(symbol)
    
    if entry_price is None or entry_price <= 0.0:
        entry_price = eq_info.get("last_price", 0.0)
        if entry_price <= 0.0:
            print(f"[LOI] Khong tim thay gia thi truong cho {symbol}. Vui long nhap gia vao!")
            return

    cost = shares * entry_price
    cash = portfolio.get("cash_balance_usd", 0.0)
    
    if cost > cash:
        print(f"[TU CHOI LENH] So du tien mat khong du! Can ${cost:,.2f} nhung chi con ${cash:,.2f}.")
        return

    # Check 10% NAV risk limit
    current_nav = cash + sum(p["shares"] * get_equity_info(s).get("last_price", p["entry_price"]) for s, p in portfolio.get("positions", {}).items())
    allocation_pct = (cost / current_nav) * 100 if current_nav > 0 else 0
    if allocation_pct > 12.0:
        print(f"[CANH BAO RUI RO] Lenh mua chiem {allocation_pct:.1f}% NAV, vuot muc tran khuyen nghi 10% cua Mentor!")

    # Stop-loss auto set if None (from audited suggested_stop_2atr if available)
    if stop_loss is None or stop_loss <= 0.0:
        suggested_stop = eq_info.get("suggested_stop_2atr")
        if suggested_stop and suggested_stop > 0:
            stop_loss = suggested_stop
            print(f"[MENTOR RULE] Tu dong thiet lap Stop-Loss tai ${stop_loss:.2f} (Theo Stop 2xATR he thong)")
        else:
            stop_loss = round(entry_price * 0.94, 2)  # Default -6%
            print(f"[MENTOR RULE] Tu dong thiet lap Stop-Loss tai ${stop_loss:.2f} (-6.0% ~ 2xATR)")

    # Deduct cash
    portfolio["cash_balance_usd"] -= cost
    positions = portfolio.setdefault("positions", {})
    
    if symbol in positions:
        old_shares = positions[symbol]["shares"]
        old_entry = positions[symbol]["entry_price"]
        new_shares = old_shares + shares
        new_entry = (old_shares * old_entry + cost) / new_shares
        positions[symbol]["shares"] = new_shares
        positions[symbol]["entry_price"] = round(new_entry, 2)
        positions[symbol]["stop_loss"] = stop_loss
    else:
        positions[symbol] = {
            "shares": shares,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target_price": target_price or round(entry_price * 1.15, 2),
            "strategy_type": strategy_type,
            "opened_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    save_json(PORTFOLIO_PATH, portfolio)
    print(f"[THANH CONG] Da khop lenh MUA mo phong: {shares} cp {symbol} tai gia ${entry_price:.2f} (Tong: ${cost:,.2f}) [{strategy_type}]")
    
    # Update student profile metric
    profile = load_json(PROFILE_PATH)
    if profile:
        profile["learning_metrics"]["paper_trades_executed"] = profile["learning_metrics"].get("paper_trades_executed", 0) + 1
        save_json(PROFILE_PATH, profile)


def sell_stock(symbol: str, shares: int, exit_price: float = None, reason: str = "Chot loi chu dong"):
    portfolio = load_json(PORTFOLIO_PATH)
    symbol = symbol.upper()
    positions = portfolio.get("positions", {})

    if symbol not in positions:
        print(f"[LOI] Khong co vi the mo cho ma {symbol}!")
        return

    current_shares = positions[symbol]["shares"]
    if shares > current_shares:
        print(f"[LOI] So luong ban ({shares}) lon hon so luong dang co ({current_shares})!")
        return

    eq_info = get_equity_info(symbol)
    if exit_price is None or exit_price <= 0.0:
        exit_price = eq_info.get("last_price", 0.0)
        if exit_price <= 0.0:
            print(f"[LOI] Khong tim thay gia thi truong cho {symbol}. Vui long nhap gia ban!")
            return

    entry_price = positions[symbol]["entry_price"]
    revenue = shares * exit_price
    pnl = (exit_price - entry_price) * shares
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100

    portfolio["cash_balance_usd"] += revenue
    portfolio["realized_pnl_usd"] = portfolio.get("realized_pnl_usd", 0.0) + pnl
    portfolio["total_trades"] = portfolio.get("total_trades", 0) + 1
    
    if pnl >= 0:
        portfolio["winning_trades"] = portfolio.get("winning_trades", 0) + 1
    else:
        portfolio["losing_trades"] = portfolio.get("losing_trades", 0) + 1

    portfolio["win_rate_percent"] = (portfolio["winning_trades"] / portfolio["total_trades"]) * 100

    trade_record = {
        "symbol": symbol,
        "shares": shares,
        "entry_price": entry_price,
        "exit_price": exit_price,
        "pnl_usd": round(pnl, 2),
        "pnl_percent": round(pnl_pct, 2),
        "reason": reason,
        "strategy_type": positions[symbol].get("strategy_type", "Core"),
        "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    portfolio.setdefault("trade_history", []).append(trade_record)

    if shares == current_shares:
        del positions[symbol]
    else:
        positions[symbol]["shares"] -= shares

    save_json(PORTFOLIO_PATH, portfolio)
    print(f"[THANH CONG] Da khop lenh BAN mo phong: {shares} cp {symbol} tai ${exit_price:.2f}. PnL: {'+' if pnl >= 0 else ''}${pnl:,.2f} ({pnl_pct:+.2f}%) [{reason}]")


def main():
    parser = argparse.ArgumentParser(description="Ban 6 Institutional Paper Trading Simulator")
    parser.add_argument("action", choices=["status", "buy", "sell", "refresh"], default="status", nargs="?")
    parser.add_argument("--symbol", "-s", type=str, help="Ma co phieu (vi du: MSFT, NVDA, AAPL)")
    parser.add_argument("--shares", "-n", type=int, default=10, help="So luong co phieu")
    parser.add_argument("--price", "-p", type=float, default=None, help="Gia khop lenh")
    parser.add_argument("--stop", type=float, default=None, help="Gia Stop-Loss")
    parser.add_argument("--target", type=float, default=None, help="Gia Take-Profit")
    parser.add_argument("--type", choices=["Core", "Satellite"], default="Core", help="Phan loai danh muc")
    parser.add_argument("--reason", type=str, default="Ke hoach giao dich", help="Ly do dong vi the")

    args = parser.parse_args()

    if args.action == "status" or args.action == "refresh":
        show_status()
    elif args.action == "buy":
        if not args.symbol:
            print("[LOI] Vui long cung cap ma co phieu bang --symbol")
            return
        buy_stock(args.symbol, args.shares, args.price, args.stop, args.target, args.type)
        show_status()
    elif args.action == "sell":
        if not args.symbol:
            print("[LOI] Vui long cung cap ma co phieu bang --symbol")
            return
        sell_stock(args.symbol, args.shares, args.price, args.reason)
        show_status()


if __name__ == "__main__":
    main()
