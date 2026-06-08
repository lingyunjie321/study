#!/usr/bin/env python3
"""
Generate ~1000 financial & economics QA pairs for AEARPO/ARAEPO training.

8 domains with equal distribution (~125 each):
  Financial Statement Analysis | Macroeconomic Policy | Corporate Finance
  Investment & Portfolio | Banking & Money Markets | Financial Regulation
  Microeconomics | Financial Mathematics

Output:
  - finance_train.parquet  (~800 rows)
  - finance_valid.parquet  (~100 rows)
  - evaluation JSONL files
"""

import argparse, json, math, os, random, sys

import pandas as pd

random.seed(42)
QA = []  # global corpus

def add(question, answer, domain, difficulty="medium", tools=None):
    QA.append({"question": question, "answer": answer, "domain": domain,
               "difficulty": difficulty, "tools_required": tools or []})

# ═══════════════════════════════════════════════════════════════════════════
# PART 1: CURATED CORE QUESTIONS (~15 per domain = 120)
# ═══════════════════════════════════════════════════════════════════════════

def curated():
    D="financial_statement_analysis"
    add("A company reports revenue of $12,500,000, COGS of $7,200,000, operating expenses of $3,100,000, and interest expense of $450,000. Tax rate is 25%. Calculate net income.",
        "Gross Profit = 12.5M - 7.2M = 5.3M. Operating Income = 5.3M - 3.1M = 2.2M. Pre-tax = 2.2M - 0.45M = 1.75M. Net = 1.75M * 0.75 = $1,312,500.", D, "medium")
    add("A firm has current assets $850K, current liabilities $425K, inventory $200K, prepaid expenses $50K. Compute current ratio and quick ratio.",
        "Current Ratio = 850/425 = 2.0. Quick Ratio = (850-200-50)/425 = 600/425 = 1.41.", D, "easy")
    add("EBITDA is $4.8M, depreciation $600K, amortization $200K, interest $300K, tax 21%. Calculate net income and interest coverage ratio.",
        "EBIT = 4.8-0.6-0.2 = 4.0M. Pre-tax = 4.0-0.3 = 3.7M. Net = 3.7*(1-0.21) = $2.923M. ICR = 4.0/0.3 = 13.33.", D, "medium")
    add("A retailer's AR turnover is 8x per year. Annual credit sales are $3.2M. Find average AR balance and average collection period.",
        "Avg AR = 3.2M/8 = $400K. Collection Period = 365/8 = 45.6 days.", D, "medium")
    add("ROE is 18%, total asset turnover is 1.5, equity multiplier is 2.0. Use DuPont analysis to find net profit margin.",
        "0.18 = NPM * 1.5 * 2.0 → NPM = 0.18/3.0 = 0.06 = 6%.", D, "medium")
    add("Goodwill impairment of $500M: pre-impairment assets $5B, equity $2B. Calculate D/E ratio before and after impairment.",
        "Before: D/E = (5-2)/2 = 1.5. After: Assets=4.5B, Equity=1.5B, Debt=3B. D/E = 3/1.5 = 2.0. Leverage risk increases significantly.", D, "hard")
    add("R&D capitalization of $2M, 5-year amortization, vs immediate expensing. Tax rate 25%. Compare EBITDA and net income in year 1.",
        "Expensing: EBITDA -2M, net -1.5M. Capitalized: no EBITDA impact (amortization below EBITDA), net = -$300K. Capitalization inflates EBITDA by $2M vs expensing.", D, "hard")
    add("Operating cash flow $5.2M, capex $2.8M, dividends $1.2M. Calculate FCFE.",
        "FCFE = OCF - Capex = 5.2-2.8 = $2.4M. After dividends: $1.2M retained.", D, "medium")
    add("Revenue $50M, gross margin 40%, SG&A 25% of revenue, depreciation $2M, interest $1M. Tax 20%. Operating and net income?",
        "Gross = 50*0.4=20M. OpInc = 20-12.5-2 = $5.5M. Pre-tax = 5.5-1 = $4.5M. Net = 4.5*0.8 = $3.6M.", D, "medium")
    add("DSO increased from 35 to 52 days with flat revenue. What problems does this signal?",
        "Signals: (1) deteriorating collections, (2) relaxed credit standards, (3) potential channel stuffing, (4) customer distress. Investigate aging schedule, peer comparison, doubtful accounts adequacy, Q4 sales patterns.", D, "hard")
    add("Difference between operating lease and finance lease under IFRS 16? How does each affect the balance sheet?",
        "Both now on balance sheet (IFRS 16 eliminated off-balance-sheet for operating leases). Finance: front-loaded interest expense + straight-line depreciation. Operating: straight-line lease expense. Both increase reported assets/liabilities. P&L timing differs: finance = more expense early.", D, "hard")
    add("Inventory turnover decreased from 12x to 8x while gross margin expanded 30% to 38%. What does this trade-off suggest?",
        "Suggests shift to higher-margin, slower-moving products (premiumization), or holding prices while competitors cut. Risk: if inventory buildup is from slowing demand rather than mix shift, write-downs may follow. Segment analysis needed.", D, "hard")
    add("Contribution margin $800K, operating income $320K. Calculate degree of operating leverage (DOL). Impact of 10% sales increase?",
        "DOL = CM/OI = 800/320 = 2.5. A 10% sales increase yields ~25% operating income increase.", D, "easy")
    add("What does negative working capital mean? When is it positive vs negative for a company like Amazon?",
        "Negative WC (CA < CL) is positive for Amazon-type companies that collect cash before paying suppliers (negative cash conversion cycle). It indicates strong bargaining power. Negative if caused by liquidity crisis rather than efficient operations.", D, "hard")
    add("Total assets $80M, liabilities $50M, 2M shares. 500K more from convertibles. Calculate basic and diluted BVPS.",
        "Equity = 80-50 = $30M. Basic BVPS = 30/2 = $15. Diluted BVPS = 30/2.5 = $12.", D, "medium")
    add("Revenue $200M, COGS $120M, DIO=73, DSO=55, DPO=60. Calculate the cash conversion cycle.",
        "CCC = 73+55-60 = 68 days.", D, "medium")
    add("How does stock-based compensation ($5M grant, 4-year vest, 25% tax) affect the three statements in year 1?",
        "IS: $1.25M SBC expense, net income -$0.9375M. CFS: add back $1.25M non-cash SBC to operating CF. BS: retained earnings -$0.9375M, APIC +$1.25M, DTA +$0.3125M. Net equity effect: +$0.3125M (tax benefit).", D, "hard")
    add("EBIT $6M, interest $2.4M. Calculate degree of financial leverage.",
        "DFL = 6/(6-2.4) = 6/3.6 = 1.67.", D, "easy")
    add("Comprehensive income $45M but net income $52M. What explains the $7M difference and what does it signal?",
        "OCI = -$7M. Causes: unrealized losses on AFS securities, FX translation losses, pension adjustments. While core ops generated $52M, market/currency movements eroded $7M. Important to examine both NI and OCI.", D, "hard")
    add("100M shares at $25, 3:2 stock split. New share count, price, market cap?",
        "Shares = 100*3/2 = 150M. Price ≈ $25*2/3 = $16.67. Market cap unchanged at $2.5B. Stock splits don't change fundamentals.", D, "easy")

    D="macroeconomic_policy"
    add("CPI increased from 250 to 262.5. Annual inflation rate?",
        "Inflation = (262.5-250)/250 * 100 = 5%.", D, "easy")
    add("Nominal GDP $25T, GDP deflator 125. Real GDP?",
        "Real GDP = 25T/1.25 = $20T.", D, "easy")
    add("Required reserve ratio 12.5%, central bank injects $100B via OMO. Maximum money supply increase?",
        "Multiplier = 1/0.125 = 8. Max increase = $100B*8 = $800B.", D, "easy")
    add("Labor force 165M, employed 157M, unemployed 8M. Unemployment rate? If natural rate is 3.5%, cyclical rate?",
        "U-rate = 8/165 = 4.85%. Cyclical = 4.85-3.5 = 1.35%.", D, "medium")
    add("Fed raises federal funds rate 75bp from 3.75%. Describe new rate and impact on aggregate demand via transmission mechanism.",
        "New rate = 4.50%. Transmission: higher rates → costlier borrowing → reduced consumption (mortgages, credit) and business investment → stronger USD reduces net exports → lower AD → downward inflation pressure.", D, "hard")
    add("Compare expansionary fiscal policy under liquidity trap vs normal conditions. G increases $200B, MPC=0.75. What's the multiplier?",
        "Normal: multiplier = 1/0.25 = 4.0, GDP +$800B. Liquidity trap: central bank can't offset, multiplier exceeds 4.0 (no crowding out). Real rates may fall from rising inflation expectations, further stimulating investment.", D, "hard")
    add("M2 velocity = 1.3, M2 = $21T, price level index = 125. Real GDP?",
        "MV=PY → Nominal GDP = 21*1.3 = $27.3T. Real GDP = 27.3/1.25 = $21.84T.", D, "medium")
    add("GDP $800B: C=$500B, I=$150B, G=$200B, X=$120B, M=$170B. Verify via expenditure approach, calculate trade balance.",
        "GDP = 500+150+200+120-170 = $800B. Trade balance = -$50B (deficit).", D, "medium")
    add("Taylor Rule: neutral real=1%, target π=2%, actual π=4.5%, output gap=-1.5%. Equal weights (0.5). Prescribed fed funds rate?",
        "r = 1+4.5+0.5(4.5-2)+0.5(-1.5) = 5.5+1.25-0.75 = 6.0%. Significantly restrictive to combat high inflation.", D, "hard")
    add("Phillips Curve: unemployment 2% below NAIRU, sacrifice ratio 3.5. Expected inflation increase?",
        "Inflationary pressure ≈ 2%/3.5 = 0.57% above expected inflation. Sacrifice ratio: reducing inflation by 1% costs 3.5% of annual GDP.", D, "medium")
    add("Explain Ricardian Equivalence. How does it challenge deficit-financed tax cuts?",
        "Barro (1974): forward-looking consumers internalize government budget constraint. Tax cut financed by debt ≠ increased consumption because rational agents anticipate future tax increases → save the tax cut. Challenges Keynesian fiscal stimulus: multiplier ≈ 0, not >1. Assumptions: perfect capital markets, lump-sum taxes, infinite horizons.", D, "hard")
    add("Structural vs cyclical budget deficit. Actual deficit 5.2% GDP, output gap -2.5%, fiscal sensitivity 0.5. Estimate structural deficit.",
        "Cyclical = 2.5%*0.5 = 1.25% of GDP. Structural = 5.2-1.25 = 3.95% of potential GDP.", D, "hard")
    add("Quantity Theory of Money: M grows 7%, V constant, real GDP grows 2.5%. Predicted inflation?",
        "MV=PY → %ΔM+%ΔV=%ΔP+%ΔY → 7+0 = π+2.5 → π=4.5%.", D, "medium")
    add("Real GDP per capita $40K (2000) to $56K (2020). CAGR? Using Rule of 72, doubling time?",
        "CAGR = (56/40)^(1/20)-1 = 1.4^0.05-1 ≈ 1.7%. Rule of 72: 72/1.7 ≈ 42.4 years to double.", D, "medium")
    add("Compare CPI, PCE, GDP deflator. Which tends highest and why?",
        "CPI tends highest: (1) fixed basket ignores substitution (PCE uses chain-weighting), (2) only out-of-pocket expenditures. GDP deflator is broadest (all domestic goods), CPI/PCE include imports. PCE is typically 0.2-0.3% below CPI. Fed targets PCE.", D, "hard")
    add("How do automatic stabilizers work during recession? Estimate impact on $500B GDP decline.",
        "1. Progressive taxes: lower incomes → lower effective rates. 2. Unemployment insurance: automatic transfers to jobless. 3. SNAP/welfare: increased enrollment. For $500B GDP decline with tax elasticity ~0.4, stabilizers offset ~30-40% ($150-200B), reducing the multiplier effect.", D, "hard")
    add("Dual mandate dilemma: inflation 6.5% (target 2%), unemployment 7.0% (NAIRU 4.5%). What's the policy tension?",
        "Stagflation-like conditions: high inflation calls for tightening, high unemployment for easing. Inflation gap=+4.5pp, unemployment gap=+2.5pp. Central banks typically prioritize inflation in such scenarios. This tension defined 1970s policy failures and shaped modern inflation-targeting.", D, "hard")
    add("Mundell-Fleming trilemma: fixed exchange rate + open capital account. What happens to monetary policy autonomy?",
        "Monetary policy is NOT autonomous. Any rate change triggers capital flows that pressure the peg. Example: rate cut → capital outflows → currency weakens → central bank must buy domestic currency (losing reserves) or raise rates. This is why Eurozone countries lose monetary independence under the single currency.", D, "hard")
    add("Define stagflation and explain why it poses a unique challenge. What caused the 1970s stagflation?",
        "Stagflation: simultaneous high inflation + high unemployment + stagnant demand, contradicting the traditional Phillips Curve trade-off. 1970s causes: (1) oil price shocks (1973, 1979), (2) overly accommodative monetary policy, (3) structural rigidities in labor markets. It challenged Keynesian orthodoxy and led to the rise of monetarism and supply-side economics.", D, "hard")
    add("What is the Laffer Curve? At what tax rate does revenue maximization theoretically occur?",
        "The Laffer Curve illustrates the relationship between tax rates and tax revenue, showing that beyond some rate t*, further increases reduce revenue (due to reduced work effort, tax avoidance, evasion). The revenue-maximizing rate is theoretically t* = 1/(1+e) where e is the elasticity of taxable income. Empirical estimates suggest t* ≈ 50-70% for high-income earners, though estimates vary widely.", D, "hard")

    D="corporate_finance"
    add("A project requires $500K initial investment, generates $150K/year for 5 years. Discount rate 10%. NPV? Accept?",
        "NPV = -500 + 150*(1-1.1^-5)/0.1 = -500 + 150*3.7908 = -500+568.62 = $68,620. NPV>0, accept.", D, "easy")
    add("A company expects to pay $3.60 dividend next year, growing at 5% annually. Required return 14%. Intrinsic value?",
        "Value = D1/(r-g) = 3.60/(0.14-0.05) = 3.60/0.09 = $40.00.", D, "easy")
    add("Acquiring Company B: FCFF=$80M next year, growth 4%, WACC=11%, debt=$200M, cash=$50M, 25M shares. Fair value per share?",
        "EV = 80/(0.11-0.04) = 80/0.07 = $1,142.86M. Equity = 1142.86-200+50 = $992.86M. Per share = $39.71.", D, "medium")
    add("WACC: equity $800M (cost 12%), debt $200M (pre-tax 6%), tax rate 25%.",
        "After-tax debt = 6%*0.75 = 4.5%. WACC = 0.80*12%+0.20*4.5% = 9.6+0.9 = 10.5%.", D, "medium")
    add("EBITDA $25M, comparable EV/EBITDA 8-12x (median 10x), debt $40M, cash $15M, 5M shares. Equity value range per share?",
        "EV range = $200M-$300M. Equity range = $175M-$275M. Per share = $35-$55.", D, "medium")
    add("MM Theorem with vs without taxes. Firm: EBIT $500M, tax 30%, switches to 50% debt at 5%. How does value change?",
        "MM (no taxes): capital structure irrelevant. MM (with taxes): VL = VU + D*t. With 50% debt, annual tax shield = (0.5*VL)*5%*30% = 0.0075*VL annually. Tax shield creates value by making interest tax-deductible.", D, "hard")
    add("Two mutually exclusive projects. A: $1M cost, $300K/yr*5yr. B: $800K cost, $250K/yr*5yr. Discount 10%. Which to choose?",
        "NPV_A = -1000+300*3.7908 = $137.24K. NPV_B = -800+250*3.7908 = $147.70K. Choose B (higher NPV).", D, "medium")
    add("Unlevered beta: equity beta=1.5, D/E=0.6, tax 25%.",
        "Unlevered β = 1.5/(1+0.75*0.6) = 1.5/1.45 = 1.034.", D, "medium")
    add("Stock price $75, EPS $5, BVPS $30. Calculate P/E and P/B. Industry: 18x, 3.0x. Interpretation?",
        "P/E = 75/5 = 15x, P/B = 75/30 = 2.5x. Both below industry: suggests either undervaluation, lower growth/RoE expectations, or higher perceived risk.", D, "medium")
    add("Terminal value: Year-5 FCF $120M, growth 3%, WACC 10%, exit EBITDA $180M at 12x. Compare methods.",
        "Perpetuity: TV = 120*1.03/(0.10-0.03) = 123.6/0.07 = $1,765.7M. Exit multiple: TV = 180*12 = $2,160M. TV typically represents 60-80% of DCF value — the wide range highlights sensitivity.", D, "hard")
    add("Enterprise value vs equity value: EV=$1.5B, debt=$300M, cash=$80M, minority interest=$50M, 40M shares. Equity per share?",
        "Equity = 1500-300+80-50 = $1,230M. Per share = $30.75.", D, "medium")
    add("EVA: NOPAT=$120M, invested capital=$800M, WACC=9.5%. Calculate EVA and ROIC.",
        "EVA = 120 - 800*0.095 = 120-76 = $44M (value-creating). ROIC = 120/800 = 15% > WACC 9.5%.", D, "medium")
    add("LBO: Target EBITDA=$60M, entry 8x, 60% debt at 7%, exit year 5 at 9x with EBITDA=$80M. 40% initial equity. Expected IRR?",
        "Entry EV = 60*8 = $480M. Initial equity = 480*0.4 = $192M. Exit EV = 80*9 = $720M. Equity at exit ≈ 720-288 = $432M (assuming no principal paydown). IRR = (432/192)^(1/5)-1 ≈ 17.6%.", D, "hard")
    add("Spin-off vs carve-out vs split-off in corporate restructuring?",
        "Spin-off: 100% subsidiary shares distributed to existing shareholders pro-rata, no cash raised. Carve-out/IPO: parent sells minority stake (<50%) to public, raising cash. Split-off: shareholders choose between parent/subsidiary shares (voluntary exchange). Spin-offs and split-offs typically tax-free under IRS Section 355 if qualifying conditions met.", D, "medium")
    add("A company with $2B all-equity assets, EBIT $300M, tax 25%, adds 40% debt at 6%. What happens to ROE?",
        "All-equity: NI = 300*0.75 = $225M, ROE = 225/2000 = 11.25%. With debt: D=$800M, E=$1200M. Interest=800*0.06=$48M. NI = (300-48)*0.75=$189M. ROE=189/1200=15.75%. ROE increases due to financial leverage, but risk increases.", D, "hard")
    add("Define the pecking order theory of capital structure. How does it differ from the trade-off theory?",
        "Pecking order (Myers & Majluf, 1984): firms prefer internal financing → debt → equity (as last resort) due to asymmetric information. Trade-off theory: firms balance tax benefits of debt against bankruptcy costs to find optimal D/E ratio. Key difference: pecking order implies no well-defined target D/E; profitable firms use less debt (contrary to trade-off).", D, "hard")
    add("What is the difference between a hostile and friendly takeover? What is a poison pill defense?",
        "Friendly: target board approves, negotiated terms. Hostile: acquirer bypasses target board (tender offer directly to shareholders, proxy fight). Poison pill (shareholder rights plan): allows existing shareholders (except the acquirer) to buy shares at a discount if any entity acquires >15-20%, massively diluting the acquirer. Adopted after Delaware court validation in Moran v. Household International (1985).", D, "hard")

    D="investment_portfolio"
    add("Portfolio: 60% Stock A (E(R)=12%), 40% Stock B (E(R)=8%). Expected portfolio return?",
        "E(Rp) = 0.60*12% + 0.40*8% = 10.4%.", D, "easy")
    add("Stock X σ=25%, Stock Y σ=18%, ρ=0.3. Equally weighted portfolio standard deviation?",
        "σp² = 0.5²*0.25² + 0.5²*0.18² + 2*0.5*0.5*0.3*0.25*0.18 = 0.015625+0.0081+0.00675 = 0.030475. σp = 17.46%.", D, "medium")
    add("Sharpe Ratio: expected return 14%, Rf=3%, σ=22%.",
        "Sharpe = (14-3)/22 = 11/22 = 0.50.", D, "easy")
    add("$10M bond portfolio, modified duration=6.5. Rates rise 50bp. Dollar change?",
        "ΔPrice ≈ -6.5*0.005 = -3.25%. Dollar = -3.25%*$10M = -$325K.", D, "medium")
    add("CAPM: Stock Z β=1.35, MRP=8%, Rf=2.5%. Expected return?",
        "E(R) = 2.5 + 1.35*8 = 2.5+10.8 = 13.3%.", D, "easy")
    add("Fund alpha 2.8%, tracking error 7.5%. Information ratio. Statistically significant?",
        "IR = 2.8/7.5 = 0.373. t-stat over 36 months = 0.373*√36 = 2.24 > 1.96. Statistically significant at 95%, but economic magnitude is modest (IR < 0.5).", D, "hard")
    add("Achieve 11% return combining Rf=3% with risky portfolio (15% return, 25% σ). Portfolio weights?",
        "0.11 = w*0.15 + (1-w)*0.03 → 0.08 = w*0.12 → w=0.667. 66.7% risky, 33.3% risk-free. Portfolio σ = 16.67%.", D, "medium")
    add("Stock covariance with market = 0.045, market variance = 0.03. Beta? If E(R)=13%, Rf=3%, implied MRP?",
        "β = 0.045/0.03 = 1.5. MRP = (13-3)/1.5 = 6.67%.", D, "medium")
    add("VaR vs Expected Shortfall. 95% VaR=$2.5M, 95% ES=$4.2M. What does the gap imply?",
        "Gap ($2.5M vs $4.2M) indicates significant tail risk/fat tails. When losses exceed VaR threshold, they're far worse. ES is coherent (satisfies sub-additivity); VaR does not. Basel III FRTB uses ES at 97.5%.", D, "hard")
    add("Fama-French 3-factor model. What factor loadings characterize small-cap value stocks?",
        "3F: E(R) = Rf + β*(Rm-Rf) + β_SMB*SMB + β_HML*HML. Small-cap value: positive SMB (small market cap premium), positive HML (high book-to-market/value premium). Historical SMB ~2%/yr, HML ~4%/yr (US, 1926-2020).", D, "medium")
    add("Jensen's alpha and Treynor ratio: actual return 17.5%, β=1.6, Rf=2%, market return 11%.",
        "CAPM expected = 2+1.6*9 = 16.4%. Alpha = 17.5-16.4 = 1.1%. Treynor = (17.5-2)/1.6 = 9.69%. Market Treynor = (11-2)/1.0 = 9.0%.", D, "medium")
    add("Strategic vs tactical asset allocation. Example of tactical shift given forecast of rising rates?",
        "Strategic AA: long-term target weights (e.g., 60/40 equity/bonds). Tactical AA: short-term deviations (±5-15%) to exploit market conditions. Rising rates forecast → underweight long-duration bonds by 10% (reallocating to short-term TIPS or cash), expecting duration-driven losses. Reviewed quarterly.", D, "medium")
    add("Sortino ratio: return 16%, MAR=2% (Rf), downside deviation 12%. Compare to portfolio with same Sharpe but downside dev 8%.",
        "Sortino = (16-2)/12 = 14/12 = 1.17. Portfolio with downside dev 8%: Sortino = 14/8 = 1.75. Higher Sortino = better downside protection. Sortino preferred when investors care more about downside risk.", D, "hard")
    add("Minimum variance portfolio: σ_A=25%, σ_B=18%, ρ = -1, 0, +1. Minimum possible σ for each?",
        "ρ=-1: min σ=0 (perfect diversification at w=18/43=41.86%). ρ=0: min w_A=324/(625+324)=34.1%, σp≈14.4%. ρ=+1: min σ=18% (100% in B). Diversification benefit decreases as correlation increases.", D, "hard")
    add("Efficient frontier and tangency portfolio. Why does every investor on the CML hold the same risky portfolio?",
        "Efficient frontier = max return for given risk. Tangency portfolio = highest Sharpe ratio (where CAL from Rf is tangent). Tobin's Separation Theorem: all investors, regardless of risk aversion, hold the same tangency portfolio of risky assets, differing only in mix of this portfolio vs risk-free asset. Theoretical basis for market-cap indexing.", D, "hard")
    add("What is the difference between active return and alpha? Calculate active return for portfolio returning 12.5% against benchmark returning 9.8%.",
        "Active return = portfolio return - benchmark return = 12.5-9.8 = 2.7%. Alpha is active return adjusted for beta exposure: α = Rp - [Rf + βp*(Rm-Rf)]. Active return can come from beta timing (market exposure), while alpha isolates manager skill.", D, "medium")
    add("Explain factor investing (smart beta). How does a value factor ETF differ from a market-cap ETF?",
        "Factor investing systematically targets specific drivers of return (value, momentum, quality, low volatility, size). Value factor ETF: weights stocks by fundamentals (P/B, P/E, etc.) rather than market cap. Differs from cap-weighted ETF: (1) higher exposure to value factor (HML), (2) higher turnover, (3) potentially higher tracking error, (4) historically higher returns but periods of significant underperformance (2017-2020).", D, "hard")
    add("Calculate the maximum Sharpe ratio portfolio from two risky assets: μ_A=10%, σ_A=20%, μ_B=6%, σ_B=12%, ρ=0.2, Rf=2%.",
        "w_A* = [(0.10-0.02)*0.12² - (0.06-0.02)*0.2*0.20*0.12] / [(0.10-0.02)*0.12² + (0.06-0.02)*0.20² - (0.10-0.02+0.06-0.02)*0.2*0.20*0.12]. = [0.08*0.0144-0.04*0.0048] / [0.08*0.0144+0.04*0.04-0.12*0.0048] = [0.001152-0.000192]/[0.001152+0.0016-0.000576] = 0.00096/0.002176 = 44.1%. w_B = 55.9%.", D, "hard")

    D="banking_money_markets"
    add("Bank with $1.2B deposits, 10% reserve ratio, holds $150M reserves. Excess reserves and additional lending capacity?",
        "Required = 1.2B*0.10 = $120M. Excess = 150-120 = $30M. Can lend $30M more.", D, "easy")
    add("90-day T-bill, face $10K, priced at $9,850. Discount yield and bond equivalent yield?",
        "Discount yield = (150/10000)*(360/90) = 0.015*4 = 6.0%. BEY = (150/9850)*(365/90) = 0.015228*4.0556 = 6.18%.", D, "medium")
    add("Bank: total assets $50B, RWA $35B, Tier 1=$2.8B, Tier 2=$1.4B. CET1, Tier 1, Total Capital ratios? Meet Basel III minimums?",
        "CET1 = 2.8/35 = 8.0%. Tier 1 = 8.0%. Total = 4.2/35 = 12.0%. Basel III: CET1≥4.5%, Tier 1≥6%, Total≥8%. All minimums met, but CET1 may not meet CCB requirement of 7.0%.", D, "hard")
    add("Yield curve inversion: 2Y vs 10Y spread at -0.45%. What does this signal about recession risk?",
        "Inverted yield curve preceded every US recession since 1955 (one false signal). -45bp spread: short rates > long rates → tight near-term monetary policy + expected long-term slowdown. NY Fed: 30-40% recession probability within 12 months. Inversion reflects market pricing of 'hard landing' scenario.", D, "hard")
    add("Bank net interest income $800M on average earning assets of $20B. Cost of funds 2.5%. NIM and implied asset yield?",
        "NIM = 800/20000 = 4.0%. Asset Yield = NIM + Cost of Funds = 6.5%.", D, "medium")
    add("LIBOR to SOFR transition: key differences and why necessary?",
        "LIBOR: bank panel submissions (not actual transactions), vulnerable to manipulation (2012 scandal, ~$200T contracts). SOFR: transaction-based (overnight Treasury repo), nearly risk-free. Differences: LIBOR had term structure + bank credit risk; SOFR is overnight only. Represents largest benchmark reform in history.", D, "hard")
    add("Repo: dealer sells $50M Treasuries, repurchase at $50,025K in 30 days. Implied repo rate (360-day)?",
        "Interest = $25K. Repo rate = (25K/50000K)*(360/30) = 0.0005*12 = 0.60%.", D, "medium")
    add("Bank CET1=$4.2B, AT1=$1.5B, T2=$2.0B, RWA=$48B, CCB=2.5%. Capital adequacy? Dividend restrictions?",
        "CET1 = 4.2/48 = 8.75%. CCB minimum = 7.0%. Bank 1.75pp above CCB → no dividend restrictions. If CET1 < 7.0%, automatic restrictions on dividends, bonuses, AT1 coupons per Basel III.", D, "hard")
    add("Interbank market vs federal funds market. How does EFFR relate to FOMC target range?",
        "FF market: depository institutions lend reserve balances overnight. FOMC sets target range (e.g., 4.25-4.50%), EFFR = volume-weighted median of actual trades. Fed uses ON RRP (floor) and IORB (ceiling) to keep EFFR in range. Interbank market is broader (term lending, Eurodollars). Persistent EFFR near upper bound may signal reserve scarcity.", D, "hard")
    add("CD: $500K, 180-day, 4.8% rate (360-day convention). Maturity proceeds?",
        "Interest = 500K*0.048*(180/360) = 500K*0.024 = $12K. Proceeds = $512K.", D, "easy")
    add("Discount window: primary credit vs secondary credit vs seasonal credit?",
        "Primary: for generally sound banks, rate ~100bp above IORB. Secondary: for banks not eligible for primary, higher rates, more scrutiny. Seasonal: for small institutions with seasonal liquidity swings (agricultural banks). Historically, stigma reduced usage → Fed created Bank Term Funding Program (BTFP) in 2023 as alternative.", D, "hard")
    add("Bank maturity gap: RSA=$300M, RSL=$450M (1-yr horizon). Impact of 100bp rate rise on NII?",
        "Gap = 300-450 = -$150M (liability-sensitive). ΔNII ≈ -150M*0.01 = -$1.5M. Rising rates reduce NII short-term. Bank should shorten liability duration or lengthen asset duration to close gap.", D, "medium")
    add("What is the role of the FDIC? What is the current standard maximum deposit insurance coverage?",
        "FDIC: (1) insures deposits at member banks (standard max $250K per depositor, per insured bank, per ownership category), (2) examines/supervises financial institutions, (3) manages receiverships of failed banks. Created by Banking Act of 1933 (Glass-Steagall) in response to the Great Depression bank runs. Funded by premiums assessed on member banks, not taxpayer funds.", D, "easy")
    add("What is a bank run? How does the lender of last resort function prevent it?",
        "Bank run: depositors rush to withdraw funds simultaneously due to solvency concerns. Since banks hold fractional reserves, even solvent banks can fail from liquidity crises. Lender of last resort (central bank): provides emergency liquidity against good collateral, preventing fire sales. Classically articulated by Bagehot (1873): 'lend freely, at a penalty rate, against good collateral.'", D, "medium")
    add("Difference between nominal and real interest rates. If nominal rate is 7.2% and expected inflation is 3.8%, what is the real rate (Fisher equation)?",
        "Fisher: 1+r = (1+i)/(1+π). Simplified: r ≈ i-π = 7.2-3.8 = 3.4%. Exact: r = (1.072/1.038)-1 = 3.28%. The ex-ante real rate is based on expected (not actual) inflation.", D, "medium")
    add("Explain the concept of duration gap management. Bank has asset duration=4.2, liability duration=2.1, equity/assets=10%. Rates rise 100bp. Impact on equity?",
        "DGAP = D_A - D_L*(L/A) = 4.2 - 2.1*0.9 = 4.2-1.89 = 2.31. ΔEquity/Assets ≈ -DGAP*Δi = -2.31*0.01 = -2.31%. ΔEquity = -2.31%/10% = -23.1%. Significant equity erosion from rising rates: the bank is asset-sensitive (D_A >> D_L).", D, "hard")
    add("What is securitization? Walk through a basic mortgage-backed security (MBS) structure.",
        "Securitization: pooling illiquid assets (mortgages, auto loans, credit card receivables) and issuing tradable securities backed by the cash flows. MBS: (1) originator underwrites mortgages, (2) sold to SPV/trust (bankruptcy-remote), (3) SPV issues tranches (senior AAA → junior/unrated equity) with waterfall cash flow structure, (4) credit enhancement via subordination, overcollateralization, and/or insurance wraps. Transforms illiquid loans into liquid securities but contributed to 2008 GFC via misaligned incentives in originate-to-distribute model.", D, "hard")
    add("What is a credit default swap (CDS)? How does it function as both insurance and speculation?",
        "CDS: buyer pays periodic premium to seller in exchange for payment if a credit event (default, restructuring) occurs on the reference entity. Insurance: bondholder buys CDS to hedge default risk. Speculation: investor buys CDS without owning the underlying bond (naked CDS), profiting if the reference entity's creditworthiness deteriorates. Notional CDS outstanding peaked at ~$60T pre-2008. Post-crisis, standardized CDS moved to central clearing (Dodd-Frank Title VII).", D, "hard")

    D="financial_regulation"
    add("Basel III minimum CET1 ratio including capital conservation buffer?",
        "4.5% + 2.5% CCB = 7.0%. G-SIBs: additional 1.0-3.5%.", D, "easy")
    add("Dodd-Frank Act: primary regulations and the Volcker Rule?",
        "Dodd-Frank (2010): CFPB, enhanced prudential standards, derivatives regulation (Title VII), Volcker Rule (prohibits proprietary trading, limits HF/PE investments to 3% of Tier 1 capital). Response to 2008 GFC — separated commercial banking from speculative activities.", D, "medium")
    add("SEC vs CFTC jurisdiction under Dodd-Frank Title VII for: (a) corporate bond swap, (b) S&P 500 futures?",
        "(a) SEC: security-based swaps (corporate bond underlying). (b) CFTC: broad-based index futures. Mixed swaps may have joint SEC-CFTC oversight.", D, "hard")
    add("Foreign Corrupt Practices Act (FCPA): two main provisions?",
        "(1) Anti-bribery: prohibits US persons/issuers from bribing foreign officials. (2) Accounting: requires accurate books and internal controls for issuers. Penalties: up to $2M/violation for companies, $250K+5yrs imprisonment for individuals. DOJ+SEC joint enforcement. Extraterritorial: applies to any company with US-listed securities.", D, "medium")
    add("Basel III vs Basel IV: key changes to standardized approach for credit risk?",
        "Basel IV (2017, phased 2023-2028): (1) standardized approach more risk-sensitive (LTV-based weights for real estate), (2) output floor at 72.5% of standardized RWA (limits internal model benefits to 27.5%), (3) revised CVA framework, (4) operational risk replaced with SMA, (5) leverage ratio buffer for G-SIBs. Output floor is most significant — caps RWA reduction from internal models.", D, "hard")
    add("SEC's three main divisions and responsibilities?",
        "1. Corp Fin: reviews corporate filings, ensures disclosure compliance. 2. Enforcement: investigates violations, brings civil actions. 3. Investment Management: regulates mutual funds, ETFs, advisers. Mission: protect investors, maintain fair/efficient markets, facilitate capital formation.", D, "medium")
    add("Sarbanes-Oxley Act (SOX): key provisions regarding corporate governance?",
        "SOX (2002, post-Enron/WorldCom): Section 302: CEO/CFO certify financials. Section 404: management assesses internal controls. Section 906: criminal penalties for false certification (up to 20 years). Created PCAOB for auditor oversight. Compliance costs $1-5M/year for midsize companies, but studies show reduced fraud and improved reporting quality.", D, "medium")
    add("Broker-dealer vs investment adviser vs registered investment company under US securities laws?",
        "Broker-dealer ('34 Act): executes trades, earns commissions, registered with SEC+FINRA. Investment adviser ('40 Act): provides advice for compensation, fiduciary duty, SEC or state registration. Registered investment company ('40 Act): pooled vehicle (mutual fund/ETF), regulated by SEC Division of Investment Management.", D, "hard")
    add("Key AML requirements under BSA and USA PATRIOT Act?",
        "1. Customer Identification Program (CIP). 2. Currency Transaction Reports (CTR) for cash >$10K. 3. Suspicious Activity Reports (SAR). 4. AML compliance program with designated BSA officer. 5. Enhanced due diligence for foreign correspondent/private banking (PATRIOT Act §312). Violations can incur millions in daily penalties.", D, "hard")
    add("MiFID II: research unbundling requirements and impact?",
        "MiFID II (EU, 2018) required unbundling research costs from trading commissions. Previously: 'soft dollar' arrangements let fund managers pay for research via inflated commissions (client assets). Now: research priced separately, paid by manager (P&L) or Research Payment Account with client consent. Drove equity research consolidation, fewer sell-side analysts, rise of independent research.", D, "hard")
    add("Basel III leverage ratio requirement? Calculate for a bank with Tier 1=$8B, total exposure=$160B including off-balance sheet $40B.",
        "Leverage Ratio = Tier 1 / Total Exposure = $8B / $200B = 4.0%. Basel III minimum: 3%. The bank meets the minimum. US enhanced supplementary leverage ratio (eSLR) for G-SIBs: 5% at holding company, 6% at insured depository institution. Off-balance sheet items are included with credit conversion factors.", D, "hard")
    add("What is a Systemically Important Financial Institution (SIFI)? What additional requirements do G-SIBs face?",
        "SIFI: institution whose distress/failure would threaten financial stability (too big to fail). G-SIBs identified by BCBS methodology (size, interconnectedness, substitutability, complexity, cross-jurisdictional activity). Additional requirements: (1) higher capital surcharges (1.0-3.5% CET1), (2) total loss-absorbing capacity (TLAC), (3) enhanced supervision, (4) living wills/resolution plans, (5) stress testing (CCAR/DFAST).", D, "hard")
    add("What are the three pillars of Basel II/III?",
        "Pillar 1: Minimum Capital Requirements (credit, market, operational risk). Pillar 2: Supervisory Review Process (ICAAP — banks assess own capital adequacy, supervisors review/evaluate). Pillar 3: Market Discipline (public disclosure of risk exposures, capital adequacy, risk management). This three-pillar structure remains in Basel III/IV with enhanced requirements in each area.", D, "medium")
    add("What is the difference between GAAP and IFRS in financial reporting?",
        "GAAP (US, FASB): rules-based, historical cost emphasis, LIFO inventory allowed. IFRS (international, IASB): principles-based, fair value emphasis, LIFO prohibited. Key differences: (1) revenue recognition (ASC 606 vs IFRS 15 — substantially converged), (2) inventory (LIFO under GAAP only), (3) financial instruments classification (IFRS 9 vs ASC 320/825), (4) lease accounting (IFRS 16 single model vs ASC 842 dual model). Convergence efforts ongoing since Norwalk Agreement (2002).", D, "medium")
    add("What is regulatory arbitrage? Give an example in the context of Basel capital requirements.",
        "Regulatory arbitrage: exploiting differences between economic risk and regulatory treatment to reduce regulatory burdens without reducing actual risk. Example: banks shifting assets from banking book (credit risk capital charges) to trading book (market risk charges with potentially lower capital), or securitizing loans to reduce RWA density. Basel IV's output floor at 72.5% of standardized approach explicitly targets regulatory arbitrage via internal models.", D, "hard")

    D="microeconomics"
    add("Firm faces P=100-2Q, TC=50+10Q. Profit-maximizing Q, P, and max profit?",
        "MR=100-4Q=10 → Q=22.5, P=55. TR=22.5*55=1237.5. TC=50+225=275. Profit=962.5.", D, "medium")
    add("Cournot duopoly: P=120-Q, MC=30 each. Equilibrium quantities, price, profit per firm?",
        "q1=q2=(120-30)/3=30. Total Q=60. P=60. Per firm profit=(60-30)*30=$900.", D, "medium")
    add("Adverse selection in insurance: 60% low-risk (claims $2K), 40% high-risk ($8K). Actuarially fair premium? Low-risk WTP=$5K vs $3.5K?",
        "Fair premium = 0.6*2000+0.4*8000 = $4,400. WTP=$5K > $4,400: low-risk buy, no death spiral. WTP=$3,500 < $4,400: low-risk exit, premium rises to $8K, potential complete market unraveling (Akerlof's 'Lemons').", D, "hard")
    add("$5 per-unit tax: demand P=50-Q, supply P=10+Q. Deadweight loss?",
        "No tax: Q=20, P=30. With tax P=15+Q: Q_tax=17.5, P_buyer=32.5. DWL=0.5*(20-17.5)*5=$6.25.", D, "hard")
    add("Third-degree price discrimination: P_A=80-2Q_A, P_B=60-Q_B, MC=20. Optimal prices?",
        "MR_A=80-4Q_A=20 → Q_A=15, P_A=$50 (η=1.67). MR_B=60-2Q_B=20 → Q_B=20, P_B=$40 (η=2.0). Higher price in less elastic segment A.", D, "hard")
    add("Gini coefficient: bottom 40% get 18% of income. Closer to 0.3 or 0.5?",
        "Perfect equality: bottom 40% = 40%. 18/40 ratio=0.45. Gini ~0.45-0.50, closer to 0.5 (cf. US ~0.41, South Africa ~0.63).", D, "medium")
    add("Prisoner's dilemma: (C,C)=(5,5), (D,D)=(2,2), (D,C)=(8,0), (C,D)=(0,8). Nash equilibrium?",
        "Defect is strictly dominant (5<8 if other colludes; 0<2 if other defects). NE = (Defect, Defect) = (2,2). Both worse off than (5,5), but can't sustain collusion without repeated interaction or enforcement.", D, "medium")
    add("Pigouvian tax: factory external cost $15/unit, private MC=$40, demand P=100-2Q. Optimal tax and output change?",
        "Private: 100-2Q=40 → Q=30. Social MC=55. Social optimum: 100-2Q=55 → Q=22.5. Optimal tax=$15/unit (marginal external cost). Tax internalizes externality, reducing output 30→22.5.", D, "medium")
    add("Price elasticity: 10% price increase → 15% quantity decrease. Elasticity? Total revenue effect?",
        "η = -15%/10% = -1.5 (elastic, |η|>1). Price increase reduces TR (Q decrease outweighs P increase). New TR ≈ 0.99*original, ~1% decrease.", D, "easy")
    add("Pareto efficiency and First Welfare Theorem: why is competitive equilibrium Pareto efficient?",
        "First Welfare Theorem: any competitive equilibrium is Pareto efficient because MRS between goods equal across consumers (=price ratio), MRTS between inputs equal across firms, MRS=MRT (marginal rate of transformation). No unexploited gains. Assumptions: no externalities, no public goods, perfect information, no market power — all required.", D, "hard")
    add("Coase Theorem: conditions and practical limitations?",
        "If property rights are well-defined and transaction costs are zero, private bargaining achieves efficiency regardless of initial rights allocation. Limitations: (1) TC rarely zero (legal, negotiation, asymmetric information), (2) property rights hard to define (air pollution), (3) wealth effects, (4) holdout/free-rider problems with many affected parties. Value: highlights importance of property rights and TC.", D, "hard")
    add("Monopolist's Lerner Index: P=$80, MC=$35. Calculate Lerner Index and implied demand elasticity.",
        "Lerner Index = (P-MC)/P = (80-35)/80 = 0.5625. At optimum, L = 1/|η| → |η| = 1/0.5625 = 1.78. The monopolist operates where demand is elastic.", D, "medium")
    add("Price ceiling set below equilibrium: market implications? P*=50, P_ceiling=30. D: P=100-2Q, S: P=Q.",
        "At P=30: Qd = (100-30)/2 = 35, Qs = 30. Shortage = 5 units. Effects: (1) deadweight loss, (2) non-price rationing (queues, black markets), (3) quality deterioration, (4) reduced long-run supply. Classic example: rent control reducing housing supply and quality.", D, "medium")
    add("What is the difference between compensating variation and equivalent variation in welfare economics?",
        "CV: amount of money needed to compensate consumer after a price change to restore original utility level. EV: amount of money consumer would pay BEFORE a price change to avoid it. CV uses original utility as reference; EV uses new utility. CV is commonly used for policy evaluation (cost-benefit analysis). CV ≠ EV when income effect is non-zero.", D, "hard")
    add("Public goods: non-rival and non-excludable. Why do markets underprovide them?",
        "Public goods have two features: non-rival (marginal cost of additional user ≈ 0), non-excludable (impossible/impractical to exclude non-payers). Private provision fails because: (1) free-rider problem — no incentive to pay since can't be excluded, (2) MRS summed over individuals ≠ individual MRS, (3) Pareto optimal requires ΣMRS = MC (Samuelson condition). Government provision or Pigouvian subsidies can correct underprovision.", D, "hard")
    add("Define moral hazard and give an example in financial markets. How does it differ from adverse selection?",
        "Moral hazard: after a transaction, one party takes excessive risks because another party bears the cost (post-contractual information asymmetry). Example: bank takes excessive risks knowing it's 'too big to fail' (implicit government guarantee). Different from adverse selection: AS is pre-contractual (hidden information — bad types self-select into market); MH is post-contractual (hidden action — behavior changes after contract).", D, "medium")
    add("What is a natural monopoly? Under what cost conditions does it arise?",
        "Natural monopoly: single firm can serve entire market at lower cost than multiple firms. Arises when there are large fixed costs and declining average costs over the relevant output range (subadditive cost function). Historically common in utilities (water, electricity grid, railways). Regulation: (1) price caps (RPI-X), (2) rate-of-return regulation (Averch-Johnson effect — overinvestment), (3) public ownership.", D, "medium")
    add("Explain the concept of perfect competition. What five conditions must hold?",
        "1. Many buyers and sellers (all price-takers). 2. Homogeneous products. 3. Perfect information. 4. Free entry and exit (no barriers). 5. No externalities. In equilibrium: P=MC=min ATC (productive efficiency), P=MC (allocative efficiency). No economic profit in long run. It's a benchmark — no real market satisfies all conditions, but the model is useful for understanding deviations and welfare losses.", D, "medium")

    D="financial_mathematics"
    add("$25K invested at 7% compounded monthly for 10 years. Future value?",
        "r/month = 0.07/12 = 0.5833%. n = 120. FV = 25000*(1.005833)^120 = 25000*2.00966 = $50,241.50.", D, "easy")
    add("Perpetuity: $4K annually, discount rate 8%. Present value?",
        "PV = 4000/0.08 = $50,000.", D, "easy")
    add("Bond: face $10K, 5% semi-annual coupon, 8yr maturity, YTM 6%. Price?",
        "Coupon = $250, n=16, r=3%. PV = 250*(1-1.03^-16)/0.03 + 10000*1.03^-16 = 250*12.5611 + 10000*0.6232 = $9,372.28 (discount).", D, "medium")
    add("Black-Scholes d1, d2: S=100, K=105, r=3%, T=0.5, σ=25%.",
        "d1 = [ln(100/105)+(0.03+0.25²/2)*0.5]/(0.25*√0.5) = [-0.04879+0.030625]/0.17678 = -0.1028. d2 = -0.1028-0.1768 = -0.2796.", D, "hard")
    add("Monte Carlo GBM: S0=50, μ=8%, σ=30%, Δt=0.01. Expected price after 1yr under risk-neutral (r=2%) vs real-world?",
        "Risk-neutral: E[ST] = 50*exp(0.02*1) = $51.01. Real-world: E[ST] = 50*exp(0.08) = $54.17. Difference = risk premium ($3.16). Risk-neutral drift (r-σ²/2) for pricing; real-world μ for forecasting/risk management.", D, "hard")
    add("Zero-coupon bond: face $50K, 15yr maturity, YTM 5.5%. Current price?",
        "Price = 50000/1.055^15 = 50000/2.2325 = $22,396.", D, "easy")
    add("Bought 10yr, $10K face bond, 6% annual coupon, for $9,500. Estimate YTM (average method).",
        "Coupon=$600/yr. Capital gain=$500/10=$50/yr. Avg investment=(9500+10000)/2=$9,750. Approx YTM=(600+50)/9750=650/9750=6.67%.", D, "medium")
    add("EAR for 18% stated annual rate compounded monthly?",
        "EAR = (1+0.18/12)^12 - 1 = 1.015^12 - 1 = 1.1956-1 = 19.56%.", D, "easy")
    add("Modified duration: 5yr, 6% annual coupon bond, face $1K, YTM 5%. Calculate modified duration.",
        "PV(C1-4)=60, PV(C5)=1060. Discounted at 5%: PV = 57.14+54.42+51.83+49.36+830.51 = $1,043.26. Macaulay D = (1*57.14+2*54.42+3*51.83+4*49.36+5*830.51)/1043.26 = 4,671.31/1043.26 = 4.477yr. Mod D = 4.477/1.05 = 4.264.", D, "hard")
    add("Convexity: bond MD=4.264, convexity=24.5. Price change for +200bp yield shock?",
        "ΔP ≈ -4.264*0.02 + 0.5*24.5*(0.02)² = -0.08528 + 0.0049 = -8.038%. Convexity adjustment adds +0.49% to duration estimate of -8.528%. Positive convexity always benefits (reduces loss from rate increases, amplifies gains from rate decreases).", D, "hard")
    add("Forward vs futures: why might futures prices differ from forward prices?",
        "Both: buy/sell asset at future date at fixed price. Futures: standardized, exchange-traded, daily mark-to-market, require margin. Forwards: OTC, customized, settled at maturity, counterparty credit risk. Price difference (Cox-Ingersoll-Ross effect): when interest rates correlated with asset price, daily settlement creates value difference. Positive correlation → futures > forwards (margin gains earn interest); negative correlation → futures < forwards.", D, "hard")
    add("Put-call parity: call with K=100, T=0.5, call=$8.50, S=$102, r=3%. Put price?",
        "C+PV(K)=P+S. PV(K)=100*exp(-0.03*0.5)=98.51. P=8.50+98.51-102=$5.01. If market put differs, arbitrage: buy undervalued, sell overvalued, lock risk-free profit.", D, "medium")
    add("PV of annuity: $12K/year for 20 years, discount 5.5%.",
        "PV = 12000*(1-1.055^-20)/0.055 = 12000*0.6573/0.055 = 12000*11.9513 = $143,415.", D, "easy")
    add("Binomial option pricing: S0=50, u=1.2 (S=60), d=0.9 (S=45), K=52, r=4%. Price European call.",
        "p = (e^0.04-0.9)/(1.2-0.9) = (1.0408-0.9)/0.3 = 0.4693. Payoffs: up=max(60-52,0)=8, down=0. C=exp(-0.04)*(0.4693*8+0) = 0.9608*3.754 = $3.61.", D, "hard")
    add("What is delta in options? If a call option has delta=0.65 and the stock rises $2, what is the approximate change in option price?",
        "Delta = ∂C/∂S (rate of change of option price w.r.t. underlying). Call delta ranges 0 to 1. ΔC ≈ delta * ΔS = 0.65 * $2 = $1.30. Delta also approximates the probability the option will expire ITM (under certain assumptions). For ATM options, delta ≈ 0.5.", D, "medium")
    add("What is implied volatility? If an ATM option has a market price of $7.50 but the Black-Scholes price with σ=22% is $6.80, what does this suggest?",
        "Implied volatility is the σ that equates the Black-Scholes model price to the market price. Market price $7.50 > model price $6.80 (at σ=22%) implies IV > 22% — the market expects higher volatility than the historical estimate. IV reflects market expectations of future volatility, demand/supply for options, and risk premiums. The VIX index is the 30-day IV of S&P 500 options.", D, "hard")
    add("Calculate Macaulay duration for a 3-year bond with 8% annual coupon, face $1000, YTM 6%.",
        "CF: 80, 80, 1080. PV = 80/1.06 + 80/1.06² + 1080/1.06³ = 75.47+71.20+906.58 = $1,053.25. Macaulay D = (1*75.47+2*71.20+3*906.58)/1053.25 = 2937.11/1053.25 = 2.79 years.", D, "medium")
    add("What is the difference between simple interest and compound interest? $10K for 5 years at 6%: compare outcomes.",
        "Simple: FV = 10000*(1+5*0.06) = 10000*1.30 = $13,000. Compound (annual): FV = 10000*(1.06)^5 = 10000*1.3382 = $13,382. Difference = $382 due to interest-on-interest. The gap widens with longer horizons and higher rates.", D, "easy")


# ═══════════════════════════════════════════════════════════════════════════
# PART 2: TEMPLATED NUMERICAL VARIATIONS (~85 per domain ≈ 680)
# ═══════════════════════════════════════════════════════════════════════════

def rand_range(base, pct=20):
    """Vary base by +/-pct% randomly."""
    lo = int(base * (1 - pct/100))
    hi = int(base * (1 + pct/100))
    v = random.randint(lo, hi)
    return round(v, -3) if v > 1000 else round(v, -1) if v > 100 else v

def templated():
    # --- Financial Statement Analysis ---
    D = "financial_statement_analysis"
    for i in range(85):
        r = random.randint
        rev = rand_range(15000)
        cogs = rand_range(int(rev * 0.55))
        opex = rand_range(int(rev * 0.25))
        intexp = rand_range(int(rev * 0.04))
        tax = random.choice([21, 25, 30])
        gross = rev - cogs
        op_inc = gross - opex
        pretax = op_inc - intexp
        net = round(pretax * (1 - tax/100), 1)
        add(f"A company reports revenue of ${rev:,}, COGS of ${cogs:,}, operating expenses of ${opex:,}, and interest expense of ${intexp:,}. Tax rate is {tax}%. Calculate the company's net income.",
            f"Gross Profit = {rev:,} - {cogs:,} = {gross:,}. Operating Income = {gross:,} - {opex:,} = {op_inc:,}. Pre-tax Income = {op_inc:,} - {intexp:,} = {pretax:,}. Net Income = {pretax:,} * (1 - {tax/100}) = {net:,}.", D, "easy")

        ca = rand_range(600)
        cl = rand_range(int(ca * 0.5))
        inv = rand_range(int(ca * 0.25))
        cr = round(ca/cl, 2)
        qr = round((ca-inv)/cl, 2)
        add(f"A firm has current assets of ${ca:,}, current liabilities of ${cl:,}, and inventory of ${inv:,}. Calculate the current ratio and quick ratio.",
            f"Current Ratio = {ca}/{cl} = {cr}. Quick Ratio = ({ca}-{inv})/{cl} = {ca-inv}/{cl} = {qr}.", D, "easy")

        sales = rand_range(5000)
        turn = random.choice([4, 6, 8, 10, 12])
        ar = round(sales / turn, 0)
        cp = round(365 / turn, 1)
        add(f"Annual credit sales are ${sales:,} and accounts receivable turnover is {turn} times. Find average AR balance and average collection period in days.",
            f"Avg AR = {sales:,} / {turn} = {ar:,}. Collection Period = 365 / {turn} = {cp} days.", D, "medium")

        roe = random.randint(12, 25)
        at = round(random.uniform(0.8, 2.5), 1)
        em = round(random.uniform(1.5, 3.5), 1)
        npm = round(roe / 100 / (at * em) * 100, 1)
        add(f"ROE is {roe}%, total asset turnover is {at}, equity multiplier is {em}. Use DuPont analysis to find net profit margin.",
            f"ROE = NPM * Asset Turnover * Equity Multiplier → {roe/100} = NPM * {at} * {em} → NPM = {roe/100} / ({at}*{em}) = {npm}%.", D, "medium")

        ebitda = rand_range(8000)
        depr = rand_range(int(ebitda*0.12))
        amort = rand_range(int(ebitda*0.05))
        ie = rand_range(int(ebitda*0.06))
        t = random.choice([21, 25, 30])
        ebit = ebitda-depr-amort
        pti = ebit-ie
        ni = round(pti*(1-t/100), 1)
        icr = round(ebit/ie, 1)
        add(f"EBITDA is ${ebitda:,}, depreciation ${depr:,}, amortization ${amort:,}, interest ${ie:,}, tax {t}%. Calculate net income and interest coverage ratio.",
            f"EBIT = {ebitda}-{depr}-{amort} = {ebit:,}. Pre-tax = {ebit}-{ie} = {pti:,}. Net = {pti:,}*{1-t/100} = {ni:,}. ICR = {ebit}/{ie} = {icr}.", D, "medium")

    # --- Macroeconomic Policy ---
    D = "macroeconomic_policy"
    for i in range(85):
        cpi0 = random.randint(200, 300)
        cpi1 = cpi0 + random.randint(5, 30)
        inf = round((cpi1 - cpi0) / cpi0 * 100, 1)
        add(f"CPI increased from {cpi0} to {cpi1}. Annual inflation rate?",
            f"Inflation = ({cpi1}-{cpi0})/{cpi0} * 100 = {inf}%.", D, "easy")

        ngdp = random.randint(15, 35)
        deflator = random.randint(110, 140)
        rgdp = round(ngdp / (deflator/100), 1)
        add(f"Nominal GDP ${ngdp}T, GDP deflator {deflator}. Real GDP?",
            f"Real GDP = {ngdp}T / {deflator/100} = ${rgdp}T.", D, "easy")

        rr = random.choice([8, 10, 12.5, 15, 20])
        injection = random.randint(50, 200)
        mm = round(1 / (rr/100), 1)
        max_m = round(injection * mm, 1)
        add(f"Reserve ratio {rr}%, central bank injects ${injection}B through OMO. Maximum money supply increase?",
            f"Money Multiplier = 1/{rr/100} = {mm}. Maximum increase = ${injection}B * {mm} = ${max_m}B.", D, "easy")

        lf = random.randint(120, 200)
        emp = random.randint(int(lf*0.9), int(lf*0.97))
        unemp = lf - emp
        ur = round(unemp/lf*100, 1)
        nat = random.choice([3.5, 4.0, 4.5, 5.0])
        cyc = round(ur - nat, 1)
        add(f"Labor force {lf}M, employed {emp}M. Unemployment rate? If natural rate is {nat}%, cyclical rate?",
            f"U-rate = {unemp}/{lf} * 100 = {ur}%. Cyclical = {ur} - {nat} = {cyc}%.", D, "medium")

        m = random.randint(15, 25)
        v = round(random.uniform(1.0, 1.8), 1)
        p_idx = random.randint(110, 135)
        ngdp_v = round(m * v, 1)
        rgdp_v = round(ngdp_v / (p_idx/100), 1)
        add(f"M2 velocity = {v}, M2 = ${m}T, price level index = {p_idx}. Real GDP?",
            f"MV=PY → Nominal GDP = {m}*{v} = ${ngdp_v}T. Real GDP = {ngdp_v}/{p_idx/100} = ${rgdp_v}T.", D, "medium")

        gd = random.randint(600, 1500)
        c_val = random.randint(int(gd*0.5), int(gd*0.7))
        i_val = random.randint(int(gd*0.1), int(gd*0.25))
        g_val = random.randint(int(gd*0.15), int(gd*0.30))
        x_val = random.randint(int(gd*0.08), int(gd*0.18))
        m_val = x_val + random.randint(int(gd*0.02), int(gd*0.1))
        gdp_check = c_val+i_val+g_val+(x_val-m_val)
        tb = x_val-m_val
        add(f"GDP: C=${c_val}B, I=${i_val}B, G=${g_val}B, X=${x_val}B, M=${m_val}B. Verify via expenditure approach, calculate trade balance.",
            f"GDP = {c_val}+{i_val}+{g_val}+({x_val}-{m_val}) = ${gdp_check}B. Trade Balance = {x_val}-{m_val} = ${tb}B ({'surplus' if tb>=0 else 'deficit'}).", D, "medium")

        nr = random.choice([0.5, 1.0, 1.5, 2.0])
        ti = random.choice([2.0, 2.5, 3.0])
        ai = ti + random.randint(2, 5)
        og = random.choice([-2.0, -1.5, -1.0, 0.0, 0.5, 1.0])
        ffr = round(nr + ai + 0.5*(ai-ti) + 0.5*og, 1)
        add(f"Taylor Rule: neutral real={nr}%, target π={ti}%, actual π={ai}%, output gap={og}%. Equal weights. Fed funds rate?",
            f"r = {nr}+{ai}+0.5({ai}-{ti})+0.5({og}) = {ffr}%.", D, "hard")

        mg = random.randint(4, 10)
        vg = 0
        yg = round(random.uniform(1.5, 3.5), 1)
        pi_pred = mg + vg - yg
        add(f"Quantity Theory: M grows {mg}%, V constant, real GDP grows {yg}%. Predicted inflation?",
            f"MV=PY → {mg}+{vg} = π+{yg} → π = {mg}-{yg} = {pi_pred}%.", D, "medium")

        gdp0 = random.randint(30, 50)
        gdp20 = random.randint(55, 80)
        yrs = 20
        cagr = round(((gdp20/gdp0)**(1/yrs)-1)*100, 1)
        dt = round(72/cagr, 1)
        add(f"Real GDP per capita ${gdp0}K (2000) to ${gdp20}K (2020). CAGR? Rule-of-72 doubling time?",
            f"CAGR = ({gdp20}/{gdp0})^(1/{yrs})-1 = {cagr}%. Doubling time = 72/{cagr} = {dt} years.", D, "medium")

        add(f"Central bank faces inflation at {ai}% (target 2%) and unemployment at {round(ai+2,1)}% (natural 4.5%). What policy dilemma?",
            f"Stagflation-like: high inflation ({ai}% vs 2% target) calls for tightening (rate hikes); high unemployment ({round(ai+2,1)}% vs 4.5% NAIRU) calls for easing. Inflation gap > unemployment gap, so central bank likely prioritizes inflation, accepting above-natural unemployment. This tension defined 1970s policy failures and shaped modern inflation-targeting frameworks.", D, "hard")

    # --- Corporate Finance ---
    D = "corporate_finance"
    for i in range(85):
        inv = rand_range(800)
        cf = rand_range(int(inv*0.25))
        yrs = random.choice([4, 5, 6, 7])
        dr = random.choice([8, 10, 12, 15])
        pvaf = round((1-(1+dr/100)**-yrs)/(dr/100), 4)
        npv = round(-inv + cf * pvaf, 1)
        add(f"A project requires ${inv:,} investment, generates ${cf:,}/yr for {yrs} years. Discount {dr}%. NPV? Accept?",
            f"NPV = -{inv:,} + {cf:,} * (1-{1+dr/100}^(-{yrs}))/{dr/100} = -{inv:,} + {cf:,}*{pvaf} = {npv:,}. {'Accept' if npv>0 else 'Reject'} (NPV {'>' if npv>0 else '<'} 0).", D, "medium")

        d1 = random.randint(2, 6)
        g = random.randint(3, 7)
        r_r = g + random.randint(4, 10)
        iv = round(d1/((r_r-g)/100), 2)
        add(f"Dividend next year ${d1}, growth {g}%, required return {r_r}%. Intrinsic value (Gordon Growth)?",
            f"Value = D1/(r-g) = {d1}/({r_r/100}-{g/100}) = {d1}/{round(r_r/100-g/100, 3)} = ${iv}.", D, "easy")

        eq = rand_range(1000)
        debt = rand_range(int(eq*0.3))
        ke = random.choice([10, 12, 14])
        kd = random.choice([4, 5, 6, 7])
        t = random.choice([21, 25, 30])
        atd = round(kd*(1-t/100), 1)
        wacc = round(eq/(eq+debt)*ke + debt/(eq+debt)*atd, 1)
        add(f"WACC: equity ${eq}M (cost {ke}%), debt ${debt}M (pre-tax {kd}%), tax {t}%.",
            f"After-tax debt = {kd}*{1-t/100} = {atd}%. E weight = {eq}/{eq+debt} = {round(eq/(eq+debt),2)}. D weight = {debt}/{eq+debt} = {round(debt/(eq+debt),2)}. WACC = {round(eq/(eq+debt),2)}*{ke}+{round(debt/(eq+debt),2)}*{atd} = {wacc}%.", D, "medium")

        ebitda_v = rand_range(40)
        lo = random.randint(6, 10)
        hi = lo + random.randint(3, 6)
        d = rand_range(int(ebitda_v*1.5))
        c = rand_range(int(ebitda_v*0.3))
        sh = random.randint(3, 8)
        ev_lo = ebitda_v*lo
        ev_hi = ebitda_v*hi
        eq_lo = round((ev_lo-d+c)/sh, 1)
        eq_hi = round((ev_hi-d+c)/sh, 1)
        add(f"EBITDA ${ebitda_v}M, comps EV/EBITDA {lo}x-{hi}x, debt ${d}M, cash ${c}M, {sh}M shares. Equity per share range?",
            f"EV = ${ev_lo}M-${ev_hi}M. Equity = ${ev_lo-d+c}M-${ev_hi-d+c}M. Per share = ${eq_lo}-{eq_hi}.", D, "medium")

        beta_e = round(random.uniform(1.0, 2.0), 2)
        de = round(random.uniform(0.3, 1.0), 2)
        t_c = random.choice([21, 25, 30])
        beta_u = round(beta_e/(1+(1-t_c/100)*de), 3)
        add(f"Unlevered beta: equity beta {beta_e}, D/E {de}, tax {t_c}%.",
            f"Unlevered β = {beta_e}/(1+{1-t_c/100}*{de}) = {beta_e}/{round(1+(1-t_c/100)*de,3)} = {beta_u}.", D, "medium")

        sp = random.randint(40, 120)
        eps = round(random.uniform(sp*0.04, sp*0.10), 1)
        bvps = round(random.uniform(sp*0.3, sp*0.7), 1)
        pe = round(sp/eps, 1)
        pb = round(sp/bvps, 1)
        add(f"Stock ${sp}, EPS ${eps}, BVPS ${bvps}. Calculate P/E and P/B.",
            f"P/E = {sp}/{eps} = {pe}x. P/B = {sp}/{bvps} = {pb}x.", D, "easy")

        ev_val = rand_range(2000)
        d_val = rand_range(int(ev_val*0.25))
        c_val = rand_range(int(ev_val*0.08))
        mi = rand_range(int(ev_val*0.04))
        sha = random.randint(20, 60)
        eq_val = ev_val-d_val+c_val-mi
        ps = round(eq_val/sha, 2)
        add(f"EV ${ev_val}M, debt ${d_val}M, cash ${c_val}M, minority interest ${mi}M, {sha}M shares. Equity per share?",
            f"Equity = {ev_val}-{d_val}+{c_val}-{mi} = ${eq_val}M. Per share = {eq_val}/{sha} = ${ps}.", D, "medium")

        nopat = rand_range(200)
        ic = rand_range(nopat*4, nopat*8)
        w = random.choice([8, 9, 10, 11, 12])
        eva_val = round(nopat-ic*w/100, 1)
        roic = round(nopat/ic*100, 1)
        add(f"EVA: NOPAT ${nopat}M, invested capital ${ic}M, WACC {w}%.",
            f"EVA = {nopat} - {ic}*{w/100} = {eva_val}M. ROIC = {nopat}/{ic}*100 = {roic}%. {'Value-creating' if eva_val>0 else 'Value-destroying'} (ROIC {'>' if roic>w else '<'} WACC).", D, "medium")

    # --- Investment & Portfolio ---
    D = "investment_portfolio"
    for i in range(85):
        wa = random.randint(30, 70)
        wb = 100 - wa
        era = random.randint(6, 16)
        erb = random.randint(3, 10)
        erp = round(wa/100*era + wb/100*erb, 1)
        add(f"Portfolio: {wa}% Stock A (E(R)={era}%), {wb}% Stock B (E(R)={erb}%). Expected return?",
            f"E(Rp) = {wa/100}*{era} + {wb/100}*{erb} = {erp}%.", D, "easy")

        beta = round(random.uniform(0.8, 2.0), 2)
        mrp = random.choice([6, 7, 8, 9])
        rf = random.choice([2, 2.5, 3, 3.5])
        er_capm = round(rf+beta*mrp, 1)
        add(f"CAPM: β={beta}, MRP={mrp}%, Rf={rf}%. Expected return?",
            f"E(R) = {rf} + {beta}*{mrp} = {er_capm}%.", D, "easy")

        er_p = random.randint(11, 18)
        rf_p = random.choice([2, 3, 4])
        sig = random.randint(15, 30)
        sharpe = round((er_p-rf_p)/sig, 2)
        add(f"Sharpe Ratio: expected return {er_p}%, Rf={rf_p}%, σ={sig}%.",
            f"Sharpe = ({er_p}-{rf_p})/{sig} = {sharpe}.", D, "easy")

        port_val = rand_range(15)
        dur = round(random.uniform(3.0, 10.0), 1)
        bp = random.choice([25, 50, 75, 100])
        pct_chg = round(-dur*bp/10000, 2)
        dollar_chg = round(pct_chg/100*port_val*1000000, 1)
        add(f"${port_val}M bond portfolio, modified duration {dur}. Rates change {bp}bp. Dollar change?",
            f"ΔPrice ≈ -{dur}*{bp/10000} = {pct_chg}%. Dollar = {pct_chg}%*${port_val}M = ${dollar_chg:,.1f}.", D, "medium")

        sig_a = random.randint(20, 35)
        sig_b = random.randint(12, 25)
        rho = round(random.uniform(-0.2, 0.6), 1)
        var_p = round(0.25*sig_a**2/10000 + 0.25*sig_b**2/10000 + 2*0.25*rho*sig_a/100*sig_b/100, 6)
        sig_p = round(math.sqrt(var_p)*100, 1)
        add(f"Stock X σ={sig_a}%, Stock Y σ={sig_b}%, ρ={rho}. Equally weighted portfolio σ?",
            f"Variance = 0.5²*{sig_a/100}² + 0.5²*{sig_b/100}² + 2*0.5*0.5*{rho}*{sig_a/100}*{sig_b/100} = {var_p}. σp = {sig_p}%.", D, "medium")

        tar = random.randint(10, 15)
        rf2 = random.choice([2, 3, 4])
        risky = random.randint(14, 20)
        risky_sig = random.randint(20, 35)
        w_risky = round((tar-rf2)/(risky-rf2), 3)
        w_safe = round(1-w_risky, 3)
        port_sig = round(w_risky*risky_sig, 1)
        add(f"Target return {tar}% combining Rf={rf2}% with risky portfolio ({risky}%, σ={risky_sig}%). Optimal weights?",
            f"E(Rp) = w*{risky} + (1-w)*{rf2} = {tar} → w = {w_risky}. Portfolio: {w_risky*100:.0f}% risky, {w_safe*100:.0f}% risk-free. σp = {port_sig}%.", D, "medium")

        cov = round(random.uniform(0.03, 0.08), 3)
        mvar = round(random.uniform(0.02, 0.05), 2)
        b_val = round(cov/mvar, 2)
        er_stk = random.randint(12, 18)
        rf_stk = random.choice([2, 3])
        mrp_imp = round((er_stk-rf_stk)/b_val, 1)
        add(f"Stock covariance with market = {cov}, market variance = {mvar}. Beta? If E(R)={er_stk}%, Rf={rf_stk}%, implied MRP?",
            f"β = {cov}/{mvar} = {b_val}. MRP = ({er_stk}-{rf_stk})/{b_val} = {mrp_imp}%.", D, "medium")

        act = random.randint(13, 20)
        bm = random.randint(7, 12)
        b_act = round(random.uniform(1.1, 1.8), 2)
        capm_exp = round(rf_stk+b_act*(bm-rf_stk), 1)
        alpha = round(act-capm_exp, 1)
        treynor = round((act-rf_stk)/b_act, 2)
        mkt_tr = bm-rf_stk
        add(f"Actual return {act}%, β={b_act}, Rf={rf_stk}%, market {bm}%. Alpha and Treynor ratio?",
            f"CAPM expected = {rf_stk}+{b_act}*({bm}-{rf_stk}) = {capm_exp}%. Alpha = {act}-{capm_exp} = {alpha}%. Treynor = ({act}-{rf_stk})/{b_act} = {treynor}. Market Treynor = {mkt_tr}.", D, "medium")

    # --- Banking & Money Markets ---
    D = "banking_money_markets"
    for i in range(80):
        depo = rand_range(2000)
        rr_b = random.choice([8, 10, 12, 15])
        res = rand_range(int(depo*(rr_b/100 + 0.03)))
        req = round(depo*rr_b/100, 0)
        exc = round(res-req, 0)
        add(f"Bank: ${depo}M deposits, {rr_b}% reserve ratio, ${res}M reserves. Excess reserves and lending capacity?",
            f"Required = {depo}*{rr_b/100} = ${req}M. Excess = {res}-{req} = ${exc}M. Can lend ${exc}M more.", D, "easy")

        face = random.choice([10000, 25000, 50000, 100000])
        price = int(face * random.uniform(0.96, 0.995))
        days_t = random.choice([30, 60, 90, 180])
        disc_y = round((face-price)/face*(360/days_t)*100, 2)
        bey = round((face-price)/price*(365/days_t)*100, 2)
        add(f"{days_t}-day T-bill, face ${face:,}, priced at ${price:,}. Discount yield and bond equivalent yield?",
            f"Discount Yield = ({face-price})/{face} * (360/{days_t}) = {disc_y}%. BEY = ({face-price})/{price} * (365/{days_t}) = {bey}%.", D, "medium")

        ta = rand_range(80)
        rwa = rand_range(int(ta*0.7))
        t1 = rand_range(int(rwa*0.07))
        t2 = rand_range(int(rwa*0.04))
        cet1r = round(t1/rwa*100, 1)
        t1r = round(t1/rwa*100, 1)
        tcr = round((t1+t2)/rwa*100, 1)
        meets = cet1r >= 7.0
        add(f"Bank: assets ${ta}B, RWA ${rwa}B, Tier 1=${t1}B, Tier 2=${t2}B. Capital ratios? Meet Basel III CCB?",
            f"CET1 = {t1}/{rwa} = {cet1r}%. Tier 1 = {t1r}%. Total Capital = {t1+t2}/{rwa} = {tcr}%. {'Meets' if meets else 'Does NOT meet'} Basel III CCB (7.0% CET1).", D, "hard")

        nii = rand_range(1200)
        aea = rand_range(nii*15, nii*30)
        cof = round(random.uniform(1.5, 3.5), 1)
        nim = round(nii/aea*100, 2)
        ay = round(nim+cof, 1)
        add(f"Bank NII ${nii}M on average earning assets ${aea}M. Cost of funds {cof}%. NIM and implied asset yield?",
            f"NIM = {nii}/{aea} = {nim}%. Asset Yield = {nim}+{cof} = {ay}%.", D, "medium")

        rsa = rand_range(500)
        rsl = rand_range(500)
        gap = rsa-rsl
        bp_chg = random.choice([25, 50, 75, 100, 150, 200])
        nii_chg = round(gap*bp_chg/10000, 1)
        add(f"Bank: RSA ${rsa}M, RSL ${rsl}M (1yr). Impact of {bp_chg}bp rate change on NII?",
            f"Gap = {rsa}-{rsl} = ${gap}M ({'asset' if gap>0 else 'liability'}-sensitive). ΔNII ≈ {gap}*{bp_chg/10000} = ${nii_chg}M.", D, "medium")

        principal = rand_range(100)
        rate_cd = round(random.uniform(3.0, 6.0), 1)
        days_cd = random.choice([30, 60, 90, 180, 270, 360])
        interest_cd = round(principal*1000*rate_cd/100*days_cd/360, 1)
        add(f"CD: ${principal*1000:,}, {days_cd}-day, {rate_cd}% rate (360-day). Maturity proceeds?",
            f"Interest = {principal*1000:,}*{rate_cd/100}*({days_cd}/360) = ${interest_cd:,.1f}. Proceeds = ${principal*1000+interest_cd:,.1f}.", D, "easy")

        nom = round(random.uniform(5.0, 9.0), 1)
        exp_inf = round(random.uniform(2.5, 5.0), 1)
        real_f = round(nom-exp_inf, 1)
        real_exact = round((1+nom/100)/(1+exp_inf/100)*100-100, 2)
        add(f"Nominal rate {nom}%, expected inflation {exp_inf}%. Real rate (Fisher equation, both approximate and exact)?",
            f"Approximate: r ≈ {nom}-{exp_inf} = {real_f}%. Exact: r = (1+{nom/100})/(1+{exp_inf/100})-1 = {real_exact}%.", D, "medium")

        da_val = round(random.uniform(3.0, 6.0), 1)
        dl_val = round(random.uniform(1.5, 3.5), 1)
        eq_ratio = random.randint(8, 15)
        la = 1 - eq_ratio/100
        dgap = round(da_val-dl_val*la, 2)
        eq_chg = round(-dgap*0.01*100/eq_ratio, 1)
        add(f"Duration gap: D_A={da_val}, D_L={dl_val}, equity/assets={eq_ratio}%. +100bp impact on equity?",
            f"DGAP = {da_val}-{dl_val}*{la} = {dgap}. ΔEquity ≈ -{dgap}*0.01 = -{round(dgap*0.01*100,1)}% of assets. Equity/Assets = {eq_ratio}%, so equity changes by approx {eq_chg}%.", D, "hard")

    # --- Financial Regulation ---
    D = "financial_regulation"
    for i in range(80):
        cet1 = round(random.uniform(5.5, 12.0), 1)
        meets_min = cet1 >= 4.5
        meets_ccb = cet1 >= 7.0
        add(f"Bank CET1 ratio: {cet1}%. Does it meet Basel III minimum (4.5%) and CCB (7.0%)?",
            f"Minimum 4.5%: {'Yes' if meets_min else 'No'}. CCB 7.0%: {'Yes' if meets_ccb else 'No'}. {'Dividend/bonus restrictions apply' if not meets_ccb else 'No restrictions'}.", D, "easy")

        t1_cap = rand_range(15)
        exp = rand_range(t1_cap*15, t1_cap*25)
        lev = round(t1_cap/exp*100, 1)
        meets_lev = lev >= 3.0
        add(f"Bank Tier 1=${t1_cap}B, total exposure=${exp}B. Leverage ratio? Meet Basel III (3%)?",
            f"Leverage Ratio = {t1_cap}/{exp} = {lev}%. {'Meets' if meets_lev else 'Below'} 3% minimum.", D, "medium")

        fine = random.randint(100, 500)
        add(f"A financial institution is fined ${fine}M for AML violations. Under the Bank Secrecy Act, what three main reporting requirements might have been violated?",
            f"1. Failure to file Currency Transaction Reports (CTR) for cash transactions >$10,000. 2. Failure to file Suspicious Activity Reports (SAR) for suspected money laundering. 3. Inadequate Customer Identification Program (CIP) or Customer Due Diligence (CDD). Penalties can reach millions per day under BSA/AML. Post-9/11, USA PATRIOT Act §312 enhanced requirements for foreign correspondent/private banking.", D, "hard")

        sox_cost = round(random.uniform(0.5, 8.0), 1)
        add(f"A mid-size public company spends ${sox_cost}M annually on SOX compliance. What are the key requirements driving these costs?",
            f"Primary cost drivers: Section 404(b) — external auditor attestation of internal controls over financial reporting (most expensive — requires IT system documentation, control testing, remediation). Section 302 — CEO/CFO certification processes. PCAOB audit standard compliance. While costly, research shows SOX reduced accounting restatements by ~60% and improved financial reporting quality.", D, "hard")

        add(f"What is the difference between AML (Anti-Money Laundering) and CFT (Countering the Financing of Terrorism)?",
            "AML focuses on criminal proceeds (making dirty money appear clean through layering/integration). CFT targets funds for terrorist activities (which may come from clean sources, in smaller amounts). Both share CDD/KYC frameworks, but CFT additionally requires: (1) screening against UN/OFAC sanctions lists, (2) detecting structuring/smurfing patterns, (3) monitoring nonprofit/cross-border transactions. FATF (Financial Action Task Force) sets global standards for both.", D, "hard")

        add(f"Explain the concept of 'living wills' (resolution plans) for large banks. What triggers their use?",
            "Living wills (Title I of Dodd-Frank, Section 165(d)): detailed plans for rapid, orderly resolution under bankruptcy code without taxpayer bailouts or systemic disruption. Required annually for banks with >$50B assets (now $250B threshold). Shows: (1) legal entity structure, (2) intercompany exposures, (3) critical operations/ services, (4) resolution strategy (SPOE vs MPOE). If regulators find plans not credible, they can impose: higher capital, leverage limits, growth restrictions, or ultimately require divestiture of assets (orderly liquidation).", D, "hard")

        add(f"What is GDPR and how does it affect financial institutions operating in the EU?",
            "General Data Protection Regulation (GDPR, 2018): regulates processing of personal data of EU residents. For financial institutions: (1) data subject rights (access, rectification, erasure/'right to be forgotten', portability), (2) mandatory breach notification within 72 hours, (3) Data Protection Officer (DPO) requirement, (4) Data Protection Impact Assessments (DPIA) for high-risk processing, (5) fines up to 4% of global annual turnover or €20M (whichever greater). Intersects with AML/KYC recordkeeping: GDPR right to erasure vs regulatory requirement to retain records (typically 5-10 years) — regulatory obligation is a lawful basis to retain data.", D, "hard")

        add(f"A US bank wants to open a branch in London. Which regulators does it need to engage with?",
            "UK: PRA (Prudential Regulation Authority, part of Bank of England) for prudential supervision; FCA (Financial Conduct Authority) for conduct regulation. US: Federal Reserve (primary federal supervisor for foreign branches of US banks under Regulation K), OCC (if national bank), FDIC (deposit insurance considerations). Also: home-host coordination under Basel Concordat — PRA and Fed coordinate on capital, liquidity, and resolution planning. Post-Brexit, UK diverged from EU passporting regime, requiring separate authorization.", D, "hard")

    # --- Microeconomics ---
    D = "microeconomics"
    for i in range(85):
        a = random.randint(80, 150)
        b = random.randint(1, 4)
        fc = random.randint(20, 100)
        mc = random.randint(5, 25)
        q_opt = (a-mc)/(2*b)
        p_opt = a - b*q_opt
        profit = p_opt*q_opt - (fc+mc*q_opt)
        add(f"Monopolist: P={a}-{b}Q, TC={fc}+{mc}Q. Optimal Q, P, and profit?",
            f"MR={a}-{2*b}Q={mc} → Q={round(q_opt,2)}, P={round(p_opt,2)}. TR={round(p_opt*q_opt,1)}, TC={fc}+{mc}*{round(q_opt,2)}={round(fc+mc*q_opt,1)}. Profit={round(profit,1)}.", D, "medium")

        p_dem = random.randint(100, 200)
        mc_c = random.randint(20, 50)
        q_c = (p_dem-mc_c)/3
        p_c = p_dem - 2*q_c
        prof_c = (p_c-mc_c)*q_c
        add(f"Cournot duopoly: P={p_dem}-2Q, MC={mc_c} each. Equilibrium quantity per firm, price, profit?",
            f"q1=q2=({p_dem}-{mc_c})/3 = {round(q_c,1)}. Total Q={round(2*q_c,1)}. P={p_dem}-{round(2*q_c,1)}={round(p_c,1)}. Each profit=({round(p_c,1)}-{mc_c})*{round(q_c,1)}={round(prof_c,1)}.", D, "medium")

        e_d = round(random.uniform(0.3, 1.5), 1)
        change_p = random.randint(5, 20)
        change_q = round(-e_d*change_p, 1)
        tr_effect = "increase" if e_d < 1 else "decrease"
        add(f"Price elasticity of demand = {e_d}. If price increases {change_p}%, how does quantity change? Effect on total revenue?",
            f"ΔQ ≈ -{e_d}*{change_p}% = {change_q}% (quantity {'decreases' if change_q<0 else 'increases'}). {'Inelastic' if e_d<1 else 'Elastic'} demand → price increase will {tr_effect} total revenue.", D, "easy")

        mc_mon = random.randint(15, 45)
        p_mon = mc_mon*random.randint(2, 4)
        li = round((p_mon-mc_mon)/p_mon, 3)
        el = round(1/li, 1)
        add(f"Monopolist: P=${p_mon}, MC=${mc_mon}. Calculate Lerner Index and implied demand elasticity.",
            f"Lerner Index = ({p_mon}-{mc_mon})/{p_mon} = {li}. At optimum: L = 1/|η| → |η| = 1/{li} = {el}. Operates in elastic region (|η|>1).", D, "medium")

        # Externality question
        ext_cost = random.randint(5, 25)
        priv_mc = random.randint(20, 50)
        demand_a_val = random.randint(80, 150)
        q_priv = (demand_a_val-priv_mc)/2
        q_soc = (demand_a_val-(priv_mc+ext_cost))/2
        add(f"Factory external cost ${ext_cost}/unit, private MC=${priv_mc}, demand P={demand_a_val}-2Q. Optimal Pigouvian tax and output change?",
            f"Private: Q={round(q_priv,1)}. Social MC={priv_mc+ext_cost}. Social: Q={round(q_soc,1)}. Optimal tax=${ext_cost}/unit (marginal external cost). Output decreases from {round(q_priv,1)} to {round(q_soc,1)}.", D, "medium")

        # Consumer surplus question
        wtp = random.randint(60, 120)
        eq_price = random.randint(30, wtp-10)
        cs = round((wtp-eq_price)**2/(2*(wtp/random.randint(8,15))), 1)
        add(f"Linear demand, max WTP={wtp}, equilibrium price={eq_price}. Estimate consumer surplus.",
            f"For linear demand P={wtp}-bQ where b={wtp}/Q_max. At P={eq_price}, Q=({wtp}-{eq_price})/b. CS = 0.5*({wtp}-{eq_price})*Q = 0.5*({wtp}-{eq_price})*(({wtp}-{eq_price})/b). CS ≈ {cs}. Consumer surplus measures the difference between what consumers are willing to pay and what they actually pay.", D, "hard")

        # Nash equilibrium
        a_val = random.randint(40, 80)
        b_val = a_val + random.randint(20, 60)
        add(f"Two firms: if both advertise, each earns ${a_val}M. If neither advertises, each earns ${b_val}M. If one advertises and the other doesn't, the advertiser earns ${b_val+40}M and the non-advertiser earns ${a_val-15}M. What is the Nash equilibrium?",
            f"Payoff matrix: (Advertise, Advertise)=({a_val},{a_val}), (Don't, Don't)=({b_val},{b_val}), (Advertise, Don't)=({b_val+40},{a_val-15}), (Don't, Advertise)=({a_val-15},{b_val+40}). Checking dominant strategies: Advertise yields {b_val+40}>{b_val} if opponent doesn't; {a_val}>{a_val-15} if opponent does. Advertise is dominant → unique NE = (Advertise, Advertise) = (${a_val}M, ${a_val}M). Pareto inferior to (Don't, Don't) = (${b_val}M, ${b_val}M) — classic prisoners' dilemma in advertising.", D, "hard")

    # --- Financial Mathematics ---
    D = "financial_mathematics"
    for i in range(80):
        pv = rand_range(20)
        rate = random.choice([4, 5, 6, 7, 8, 9, 10])
        yrs_m = random.choice([5, 8, 10, 12, 15, 20])
        freq = random.choice(["annually", "semi-annually", "quarterly", "monthly"])
        m = {"annually": 1, "semi-annually": 2, "quarterly": 4, "monthly": 12}
        n_per = yrs_m * m[freq]
        r_per = rate / 100 / m[freq]
        fv_val = round(pv*1000 * (1+r_per)**n_per, 1)
        add(f"${pv*1000:,} invested at {rate}% compounded {freq} for {yrs_m} years. Future value?",
            f"r/period = {rate}%/{m[freq]} = {round(r_per*100,4)}%. n = {yrs_m}*{m[freq]} = {n_per}. FV = {pv*1000:,}*(1+{round(r_per,4)})^{n_per} = ${fv_val:,.1f}.", D, "easy")

        pmt = rand_range(3, 15)
        disc = random.choice([5, 6, 7, 8, 9, 10])
        pv_perp = round(pmt*1000/(disc/100), 1)
        add(f"Perpetuity: ${pmt*1000:,}/yr, discount rate {disc}%. Present value?",
            f"PV = {pmt*1000:,}/{disc/100} = ${pv_perp:,.1f}.", D, "easy")

        fv_ann = rand_range(50)
        pmt_ann = rand_range(int(fv_ann*0.1))
        yr_ann = random.choice([5, 8, 10, 12])
        r_ann = random.choice([4, 5, 6, 7, 8])
        pv_ann = round(pmt_ann*1000*(1-(1+r_ann/100)**-yr_ann)/(r_ann/100), 1)
        add(f"Annuity: ${pmt_ann*1000:,}/yr for {yr_ann} years, discount {r_ann}%. Present value?",
            f"PV = {pmt_ann*1000:,}*(1-{1+r_ann/100}^(-{yr_ann}))/{r_ann/100} = ${pv_ann:,.1f}.", D, "easy")

        face_zc = random.choice([10000, 25000, 50000, 100000])
        yrs_zc = random.choice([5, 8, 10, 15, 20, 25])
        ytm_zc = random.choice([3, 4, 5, 6, 7])
        price_zc = round(face_zc/(1+ytm_zc/100)**yrs_zc, 1)
        add(f"Zero-coupon bond: face ${face_zc:,}, {yrs_zc}yr maturity, YTM {ytm_zc}%. Current price?",
            f"Price = {face_zc:,}/{1+ytm_zc/100}^{yrs_zc} = ${price_zc:,.1f}.", D, "easy")

        ear_nom = random.choice([12, 15, 18, 21, 24])
        ear_m = random.choice([4, 12, 365])
        ear_val = round(((1+ear_nom/100/ear_m)**ear_m-1)*100, 2)
        add(f"EAR for {ear_nom}% stated annual rate compounded {'monthly' if ear_m==12 else 'quarterly' if ear_m==4 else 'daily'}?",
            f"EAR = (1+{ear_nom/100}/{ear_m})^{ear_m} - 1 = {ear_val}% — significantly higher than the stated rate due to compounding frequency.", D, "easy")

        s_opt = random.randint(40, 120)
        k_opt = s_opt + random.randint(-10, 15)
        r_opt = random.choice([2, 3, 4])
        t_opt = round(random.uniform(0.25, 1.0), 2)
        sig_opt = random.randint(20, 40)
        d1_opt = round((math.log(s_opt/k_opt)+(r_opt/100+sig_opt**2/20000)*t_opt)/(sig_opt/100*math.sqrt(t_opt)), 3)
        d2_opt = round(d1_opt - sig_opt/100*math.sqrt(t_opt), 3)
        add(f"Black-Scholes: S=${s_opt}, K=${k_opt}, r={r_opt}%, T={t_opt}, σ={sig_opt}%. Calculate d1 and d2.",
            f"d1 = [ln({s_opt}/{k_opt})+({r_opt/100}+{sig_opt}²/20000)*{t_opt}]/({sig_opt/100}*√{t_opt}) = {d1_opt}. d2 = {d1_opt}-{sig_opt/100}*√{t_opt} = {d2_opt}.", D, "hard")

        # Bond price question
        f_bond = random.choice([1000, 5000, 10000])
        c_rate = random.choice([3, 4, 5, 6, 7, 8])
        ytm = c_rate + random.choice([1, 2, 3])
        yrs_b = random.choice([3, 5, 7, 10])
        cpn = f_bond*c_rate/100
        r_ytm = ytm/100
        pv_cpn = sum([cpn/(1+r_ytm)**t for t in range(1, yrs_b+1)])
        pv_face = f_bond/(1+r_ytm)**yrs_b
        bond_p = round(pv_cpn+pv_face, 1)
        add(f"Bond: face ${f_bond:,}, {c_rate}% annual coupon, {yrs_b}yr maturity, YTM {ytm}%. Price?",
            f"PV(coupons) = sum of {cpn}/{1+ytm/100}^t = ${round(pv_cpn,1):,.1f}. PV(face) = {f_bond}/{1+ytm/100}^{yrs_b} = ${round(pv_face,1):,.1f}. Price = ${bond_p:,.1f}. {'Trades at a discount (YTM > coupon).' if ytm>c_rate else 'Trades at a premium (YTM < coupon).'}", D, "medium")


# ═══════════════════════════════════════════════════════════════════════════
# PART 3: CONCEPTUAL QUESTIONS (~100)
# ═══════════════════════════════════════════════════════════════════════════

def conceptual():
    concepts = [
        ("financial_statement_analysis", "What is the difference between cash basis and accrual basis accounting? Which provides a more accurate picture of financial health?",
         "Cash basis: revenue/expenses recognized when cash is received/paid. Accrual basis: recognized when earned/incurred regardless of cash timing. Accrual provides more accurate picture because it matches revenues with related expenses and reflects economic reality (e.g., AR represents earned-but-uncollected revenue, AP represents incurred-but-unpaid obligations). GAAP and IFRS both require accrual basis for public companies. Cash basis is simpler but can materially distort financial position and performance."),
        ("financial_statement_analysis", "What does negative shareholders' equity indicate? Is it always a bad sign?",
         "Negative equity (liabilities > assets) typically indicates: (1) cumulative losses exceeding contributed capital (financial distress), (2) large treasury stock buybacks (reducing paid-in capital), (3) significant dividend payments exceeding retained earnings, (4) for some companies like McDonald's (historical), aggressive share repurchases create negative equity while the business is healthy. Context is critical: check retained earnings trend, leverage ratios, and cash flow generation."),
        ("financial_statement_analysis", "Explain deferred tax assets (DTA) and deferred tax liabilities (DTL). What causes them?",
         "DTA/DTL arise from temporary differences between book (GAAP/IFRS) and tax basis of assets/liabilities. DTL: book income > taxable income (e.g., accelerated depreciation for tax, straight-line for books — paying less tax now, more later). DTA: book income < taxable income (e.g., warranty expense accrued for books, deductible when paid for tax, or NOL carryforwards). DTA requires valuation allowance if 'more likely than not' (>50%) that benefit won't be realized. DTL reverses when temporary differences reverse."),
        ("macroeconomic_policy", "What is quantitative easing (QE)? How does it differ from conventional open market operations?",
         "QE: central bank purchases longer-duration assets (government bonds, MBS) to lower long-term interest rates when short-term rates are near zero (ZLB). Differs from conventional OMO: (1) targets long-end of yield curve vs overnight rates, (2) expands central bank balance sheet significantly, (3) works through portfolio balance channel (investors rebalance into riskier assets). Fed QE rounds: QE1 (2008): $1.75T; QE2 (2010): $600B; QE3 (2012): open-ended $40B/month MBS; COVID QE (2020): unlimited. Transmission: lower long yields → higher asset prices → wealth effect → increased consumption/investment."),
        ("macroeconomic_policy", "What is the natural rate of unemployment (NAIRU)? Why does it change over time?",
         "NAIRU (Non-Accelerating Inflation Rate of Unemployment): unemployment rate consistent with stable inflation — the rate where labor market is in equilibrium (structural + frictional unemployment only). Changes due to: (1) demographics (aging population → lower NAIRU), (2) labor market institutions (unionization, minimum wage, unemployment benefits), (3) technological change (skill-biased technical change → higher structural unemployment), (4) globalization, (5) hysteresis (prolonged high unemployment raises NAIRU as workers lose skills/attachment). CBO estimates US NAIRU declined from ~6% (1980s) to ~4.4% (2020s)."),
        ("corporate_finance", "What is the difference between enterprise value (EV) and equity value? When would you use each?",
         "EV = market value of equity + market value of debt - cash & equivalents + minority interest + preferred stock. Equity value = market cap (shares * price). Use EV for: comparing companies with different capital structures (EV/EBITDA, EV/Sales). Use equity value for: P/E, P/B, transactions involving only equity (stock-for-stock M&A). Bridge: EV is the value of the entire business to all capital providers; equity value is the residual claim for common shareholders. EV is capital-structure neutral."),
        ("corporate_finance", "What is a leveraged buyout (LBO)? What makes a company a good LBO candidate?",
         "LBO: acquisition of a company using significant debt (typically 60-80% of purchase price), with the target's cash flows used to service and repay debt. Good LBO candidate: (1) stable, predictable cash flows (to service debt), (2) low existing leverage, (3) strong market position/moat, (4) low CapEx requirements (high FCF conversion), (5) tangible assets for collateral, (6) opportunities for operational improvement (margin expansion, working capital optimization), (7) strong management team, (8) clear exit path (IPO, strategic sale, secondary buyout) in 3-7 years."),
        ("investment_portfolio", "What is the difference between systematic and unsystematic risk? How many stocks are needed for effective diversification?",
         "Systematic (market/non-diversifiable): macroeconomic factors (interest rates, GDP, inflation, geopolitics) — affects all securities. Unsystematic (idiosyncratic/diversifiable): firm-specific (management, product failures, competitive dynamics). Studies (Evans & Archer, 1968; Statman, 1987) show: ~15-20 stocks eliminate ~85-90% of diversifiable risk; ~30 stocks eliminate ~95%. Beyond 30, marginal benefit is small. However, concentrated portfolios may be optimal if the investor has information advantages."),
        ("investment_portfolio", "What are the key assumptions and limitations of the Capital Asset Pricing Model (CAPM)?",
         "Assumptions: (1) investors are rational, risk-averse, mean-variance optimizers, (2) all investors have the same one-period horizon, (3) homogeneous expectations (same inputs), (4) no taxes, transaction costs, or restrictions on short selling, (5) unlimited borrowing/lending at the risk-free rate, (6) all information is publicly available. Limitations: (1) single-factor (market beta) fails to explain cross-sectional variation (Fama-French added size, value, profitability, investment), (2) empirical evidence shows flat/inverted SML (low-beta stocks outperform CAPM predictions), (3) assumptions unrealistic. Despite limitations, CAPM remains foundational for cost of capital estimation and portfolio performance evaluation."),
        ("banking_money_markets", "What is fractional reserve banking? How does it create money?",
         "Fractional reserve banking: banks hold only a fraction of deposits as reserves, lending out the rest. Money creation: when a bank makes a loan, it credits the borrower's deposit account (creating new money). The borrower spends these deposits; the recipient's bank receives new deposits and can lend out the excess reserves. This cycle repeats, creating a multiple expansion of the money supply. The theoretical maximum multiplier = 1/reserve requirement. In practice, the multiplier is smaller due to: (1) excess reserves (banks hold more than required), (2) currency drain (public holds cash), (3) capital constraints, (4) credit demand limitations."),
        ("financial_regulation", "What is the difference between principles-based and rules-based regulation? Give examples.",
         "Principles-based: sets broad principles/outcomes, firms have flexibility in how to achieve them. Example: UK FCA's 'Treating Customers Fairly' (TCF) principle. Rules-based: prescribes specific rules that must be followed exactly. Example: US securities laws (exact disclosure requirements, bright-line tests). Trade-offs: principles-based is more flexible, adaptable, and harder to arbitrage but creates uncertainty; rules-based provides clarity and enforceability but creates opportunities for regulatory arbitrage (following the letter but not the spirit). Most systems are hybrid."),
        ("financial_regulation", "What is the role of stress testing in bank regulation? Describe the CCAR process.",
         "Stress testing assesses bank resilience under adverse economic scenarios. CCAR (Comprehensive Capital Analysis and Review): US Fed's annual exercise for large banks (>$100B). Process: (1) Fed provides macro scenarios (baseline, adverse, severely adverse), (2) banks project losses, revenues, and capital ratios over 9-quarter horizon under each scenario, (3) Fed evaluates both quantitative results and qualitative capital planning processes, (4) banks must maintain capital above regulatory minimums including CCB under severely adverse scenario. Non-objection: bank can proceed with planned capital actions (dividends, buybacks). Objection: restrictions on capital distributions. Post-2020, CCAR integrated with DFAST under the stress capital buffer (SCB) framework."),
        ("microeconomics", "What is the difference between a positive and normative economic statement? Give examples.",
         "Positive statements: describe what IS (factual, testable). Examples: 'raising minimum wage to $15 reduces employment among teenagers by 2-3%' (can be verified with data). Normative statements: prescribe what OUGHT to be (value judgment). Example: 'the government should raise the minimum wage to $15 to reduce income inequality' (involves values, cannot be tested). Economics as a science focuses on positive analysis; policy recommendations involve normative judgments. The distinction was articulated by Milton Friedman (1953) in 'The Methodology of Positive Economics.'"),
        ("microeconomics", "What is the tragedy of the commons? How can it be prevented?",
         "Tragedy of the commons (Hardin, 1968): when a shared resource (common property) is rivalrous and non-excludable, each individual has an incentive to over-exploit it because they receive full benefit of their use while costs are shared. Prevention: (1) privatization (assign property rights — Coase approach), (2) government regulation (quotas, licenses, Pigouvian taxes), (3) community management (Ostrom's research showed communities can self-govern commons with clear boundaries, participatory decision-making, monitoring, graduated sanctions, and conflict resolution mechanisms — won 2009 Nobel Prize). Examples: overfishing, deforestation, carbon emissions, groundwater depletion."),
        ("financial_mathematics", "What is the difference between simple and continuously compounded returns? When is each preferable?",
         "Simple return: R_t = (P_t - P_{t-1}) / P_{t-1}. Continuously compounded (log) return: r_t = ln(P_t / P_{t-1}). Properties: (1) log returns are time-additive (r_{0→T} = r_1+r_2+...+r_T), while simple returns are multiplicative (1+R = (1+R1)(1+R2)...), (2) log returns are approximately symmetric, (3) log returns are theoretically unbounded on both sides while simple returns are bounded below by -100%. Portfolio simple return = weighted average (log returns are not additive across assets). Financial modeling: log returns for time-series analysis (normality assumption), simple returns for portfolio reporting."),
    ]
    for domain, question, answer in concepts:
        add(question, answer, domain, "medium")


# ═══════════════════════════════════════════════════════════════════════════
# OUTPUT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

SYSTEM_MSGS = {
    "financial_statement_analysis": "You are a financial analyst. Analyze financial statements and calculate key metrics step by step.",
    "macroeconomic_policy": "You are a macroeconomist. Analyze economic indicators and policy implications with rigorous reasoning.",
    "corporate_finance": "You are a corporate finance expert. Evaluate investments, valuations, and capital structure decisions.",
    "investment_portfolio": "You are a portfolio manager. Apply modern portfolio theory and risk-return analysis.",
    "banking_money_markets": "You are a banking analyst. Evaluate bank balance sheets, money markets, and monetary policy transmission.",
    "financial_regulation": "You are a regulatory compliance expert. Apply financial regulations and assess compliance requirements.",
    "microeconomics": "You are a microeconomist. Analyze market structures, pricing, and welfare economics.",
    "financial_mathematics": "You are a quantitative analyst. Apply financial mathematics and derivative pricing models.",
}

def to_prompt(question, domain):
    sys_content = SYSTEM_MSGS.get(domain, "You are a financial economics expert. Think step by step and provide a rigorous, well-reasoned answer.")
    return [{"role": "system", "content": sys_content}, {"role": "user", "content": question}]

def build_parquet(qa_list, split_name):
    rows = []
    for idx, item in enumerate(qa_list):
        rows.append({
            "data_source": f"finance_economics/{item['domain']}",
            "prompt": to_prompt(item["question"], item["domain"]),
            "ability": f"finance/{item['domain']}",
            "reward_model": {"style": "rule", "ground_truth": item["answer"]},
            "extra_info": {"split": split_name, "index": idx, "domain": item["domain"],
                           "difficulty": item["difficulty"], "tools_required": item.get("tools_required", [])},
        })
    return pd.DataFrame(rows)

def build_eval_jsonl(qa_list, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, item in enumerate(qa_list):
            f.write(json.dumps({"id": idx, "question": item["question"], "answer": item["answer"],
                                "domain": item["domain"], "difficulty": item["difficulty"]}, ensure_ascii=False) + "\n")
    print(f"  -> {output_path} ({len(qa_list)} samples)")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_path", default=None)
    parser.add_argument("--valid_path", default=None)
    parser.add_argument("--eval_dir", default=None)
    args = parser.parse_args()

    # Build corpus
    print("Building curated core questions...")
    curated()
    print(f"  After curated: {len(QA)} items")
    print("Building templated numerical variations...")
    templated()
    print(f"  After templated: {len(QA)} items")
    print("Building conceptual questions...")
    conceptual()
    print(f"  After conceptual: {len(QA)} items")

    # Deduplicate by first 100 chars of question
    seen = set()
    unique = []
    for q in QA:
        key = q["question"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(q)
    QA.clear()
    QA.extend(unique)
    print(f"  After dedup: {len(QA)} unique items")

    random.shuffle(QA)

    # Split
    n = len(QA)
    n_train = int(n*0.80)
    n_valid = int(n*0.12)
    train_qa = QA[:n_train]
    valid_qa = QA[n_train:n_train+n_valid]
    eval_qa = QA[n_train+n_valid:]

    print(f"\nFinal: {n} items | Train: {len(train_qa)} | Valid: {len(valid_qa)} | Eval: {len(eval_qa)}")

    # Domain distribution
    from collections import Counter
    dom_dist = Counter(q["domain"] for q in QA)
    for d, c in sorted(dom_dist.items()):
        print(f"  {d}: {c}")

    # Output paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    aearpo_datasets = os.path.join(repo_root, "AEARPO", "rl_datasets")
    eval_data = os.path.join(repo_root, "evaluation", "data")

    train_path = args.train_path or os.path.join(aearpo_datasets, "finance_train.parquet")
    valid_path = args.valid_path or os.path.join(aearpo_datasets, "finance_valid.parquet")
    eval_dir = args.eval_dir or eval_data

    print("\n[1/5] Building training parquet...")
    df_train = build_parquet(train_qa, "train")
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    df_train.to_parquet(train_path, index=False)
    print(f"  -> {train_path} ({len(df_train)} rows)")

    print("\n[2/5] Building validation parquet...")
    df_valid = build_parquet(valid_qa, "valid")
    df_valid.to_parquet(valid_path, index=False)
    print(f"  -> {valid_path} ({len(df_valid)} rows)")

    print("\n[3/5] Finance evaluation JSONL...")
    build_eval_jsonl(eval_qa, os.path.join(eval_dir, "finance", "test.jsonl"))

    print("\n[4/5] FinBench hard evaluation JSONL...")
    hard_qa = [q for q in QA if q["difficulty"] == "hard"]
    random.shuffle(hard_qa)
    build_eval_jsonl(hard_qa[:200], os.path.join(eval_dir, "finbench", "test.jsonl"))

    print("\n[5/5] Domain-specific evaluation JSONLs...")
    for domain in sorted(set(q["domain"] for q in QA)):
        domain_qa = [q for q in QA if q["domain"] == domain]
        fname = domain.replace("_", "")
        build_eval_jsonl(domain_qa[:60], os.path.join(eval_dir, "finance_domains", f"{fname}.jsonl"))

    print("\n" + "="*60)
    print("Financial Economics 1K dataset generation complete.")
    print(f"  Total QA pairs: {len(QA)}")
    print(f"  Training:       {train_path}")
    print(f"  Validation:     {valid_path}")
    print(f"  Evaluation:     {eval_dir}/finance/test.jsonl")
    print(f"  FinBench:       {eval_dir}/finbench/test.jsonl")
    print("="*60)

if __name__ == "__main__":
    main()
