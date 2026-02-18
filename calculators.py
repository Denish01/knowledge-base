"""
Calculator Templates
Embeddable JavaScript calculators for knowledge pages.

Each calculator is self-contained HTML/CSS/JS that can be injected into pages.
"""

# =============================================================================
# CALCULATOR REGISTRY
# Maps topics to their calculators
# =============================================================================

CALCULATOR_TOPICS = {
    # Finance
    "compound interest": "compound_interest",
    "mortgage amortization": "mortgage",
    "loan amortization": "mortgage",
    "annual percentage rate": "apr",
    "annual percentage yield": "apy",
    "credit score": None,  # No calc needed
    "net worth": "net_worth",
    "dollar cost averaging": "dca",
    "retirement planning": "retirement",
    "401k retirement plan": "retirement",
    "roth ira": "retirement",
    "traditional ira": "retirement",

    # Math
    "percentages": "percentage",
    "fractions": "fraction",
    "ratios": "ratio",
    "proportions": "proportion",
    "area of a circle": "circle_area",
    "perimeter": "perimeter",
    "volume": "volume",
    "pythagorean theorem": "pythagorean",
    "mean median mode": "statistics",
    "standard deviation": "std_dev",
    "probability": "probability",

    # Science
    "unit conversion": "unit_converter",

    # Economics
    "inflation": "inflation",
    "gross domestic product": "gdp_per_capita",
    "price elasticity": "elasticity",

    # Tool page mappings (calculator_key -> calculator_key)
    "loan repayment": "loan_repayment",
    "investment return": "investment_return",
    "credit card payoff": "credit_card_payoff",
    "emergency fund": "emergency_fund",
    "income tax": "income_tax",
    "salary after tax": "salary_after_tax",
    "capital gains": "capital_gains",
    "vat": "vat_calculator",
    "profit margin": "profit_margin",
    "break even": "break_even",
    "roi": "roi_calculator",
    "markup": "markup_calculator",
    "bmi": "bmi_calculator",
    "calorie": "calorie_calculator",
    "currency converter": "currency_converter",
    "temperature converter": "temperature_converter",
    "self employment tax": "self_employment_tax",
}


def get_calculator_for_topic(topic):
    """Get the calculator type for a topic, if any."""
    topic_lower = topic.lower()
    return CALCULATOR_TOPICS.get(topic_lower)


# =============================================================================
# CALCULATOR TEMPLATES (Self-contained HTML/CSS/JS)
# =============================================================================

CALCULATORS = {

    # =========================================================================
    # COMPOUND INTEREST CALCULATOR
    # =========================================================================
    "compound_interest": """
<div class="calculator" id="compound-calc">
    <h3>Compound Interest Calculator</h3>
    <div class="calc-grid">
        <label>Initial Amount ($)
            <input type="number" id="ci-principal" value="1000" min="0">
        </label>
        <label>Annual Interest Rate (%)
            <input type="number" id="ci-rate" value="5" min="0" max="100" step="0.1">
        </label>
        <label>Time (years)
            <input type="number" id="ci-time" value="10" min="1" max="50">
        </label>
        <label>Compound Frequency
            <select id="ci-frequency">
                <option value="1">Annually</option>
                <option value="4">Quarterly</option>
                <option value="12" selected>Monthly</option>
                <option value="365">Daily</option>
            </select>
        </label>
    </div>
    <button onclick="calculateCompound()">Calculate</button>
    <div class="calc-result" id="ci-result"></div>
</div>
<script>
function calculateCompound() {
    const P = parseFloat(document.getElementById('ci-principal').value);
    const r = parseFloat(document.getElementById('ci-rate').value) / 100;
    const t = parseFloat(document.getElementById('ci-time').value);
    const n = parseFloat(document.getElementById('ci-frequency').value);

    const A = P * Math.pow((1 + r/n), n*t);
    const interest = A - P;

    document.getElementById('ci-result').innerHTML = `
        <p><strong>Future Value:</strong> $${A.toFixed(2)}</p>
        <p><strong>Total Interest Earned:</strong> $${interest.toFixed(2)}</p>
        <p><strong>Growth:</strong> ${((A/P - 1) * 100).toFixed(1)}%</p>
    `;
}
calculateCompound();
</script>
""",

    # =========================================================================
    # MORTGAGE/LOAN CALCULATOR
    # =========================================================================
    "mortgage": """
<div class="calculator" id="mortgage-calc">
    <h3>Loan/Mortgage Calculator</h3>
    <div class="calc-grid">
        <label>Loan Amount ($)
            <input type="number" id="loan-amount" value="250000" min="0">
        </label>
        <label>Annual Interest Rate (%)
            <input type="number" id="loan-rate" value="6.5" min="0" max="30" step="0.125">
        </label>
        <label>Loan Term (years)
            <input type="number" id="loan-term" value="30" min="1" max="50">
        </label>
    </div>
    <button onclick="calculateMortgage()">Calculate</button>
    <div class="calc-result" id="mortgage-result"></div>
</div>
<script>
function calculateMortgage() {
    const P = parseFloat(document.getElementById('loan-amount').value);
    const r = parseFloat(document.getElementById('loan-rate').value) / 100 / 12;
    const n = parseFloat(document.getElementById('loan-term').value) * 12;

    const M = P * (r * Math.pow(1+r, n)) / (Math.pow(1+r, n) - 1);
    const totalPaid = M * n;
    const totalInterest = totalPaid - P;

    document.getElementById('mortgage-result').innerHTML = `
        <p><strong>Monthly Payment:</strong> $${M.toFixed(2)}</p>
        <p><strong>Total Interest:</strong> $${totalInterest.toFixed(2)}</p>
        <p><strong>Total Cost:</strong> $${totalPaid.toFixed(2)}</p>
    `;
}
calculateMortgage();
</script>
""",

    # =========================================================================
    # PERCENTAGE CALCULATOR
    # =========================================================================
    "percentage": """
<div class="calculator" id="percent-calc">
    <h3>Percentage Calculator</h3>
    <div class="calc-tabs">
        <button class="tab-btn active" onclick="showTab('pct-of')">% of Number</button>
        <button class="tab-btn" onclick="showTab('pct-change')">% Change</button>
        <button class="tab-btn" onclick="showTab('pct-is')">X is what % of Y</button>
    </div>
    <div id="pct-of" class="tab-content active">
        <label>What is <input type="number" id="pct1-percent" value="25" style="width:60px">% of
        <input type="number" id="pct1-number" value="200" style="width:80px">?</label>
        <button onclick="calcPctOf()">Calculate</button>
        <div class="calc-result" id="pct1-result"></div>
    </div>
    <div id="pct-change" class="tab-content">
        <label>From <input type="number" id="pct2-from" value="100" style="width:80px"> to
        <input type="number" id="pct2-to" value="150" style="width:80px"></label>
        <button onclick="calcPctChange()">Calculate</button>
        <div class="calc-result" id="pct2-result"></div>
    </div>
    <div id="pct-is" class="tab-content">
        <label><input type="number" id="pct3-x" value="25" style="width:80px"> is what % of
        <input type="number" id="pct3-y" value="200" style="width:80px">?</label>
        <button onclick="calcPctIs()">Calculate</button>
        <div class="calc-result" id="pct3-result"></div>
    </div>
</div>
<script>
function showTab(id) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}
function calcPctOf() {
    const pct = parseFloat(document.getElementById('pct1-percent').value);
    const num = parseFloat(document.getElementById('pct1-number').value);
    document.getElementById('pct1-result').innerHTML = `<p><strong>Result:</strong> ${(pct/100 * num).toFixed(2)}</p>`;
}
function calcPctChange() {
    const from = parseFloat(document.getElementById('pct2-from').value);
    const to = parseFloat(document.getElementById('pct2-to').value);
    const change = ((to - from) / from * 100).toFixed(2);
    document.getElementById('pct2-result').innerHTML = `<p><strong>Change:</strong> ${change}%</p>`;
}
function calcPctIs() {
    const x = parseFloat(document.getElementById('pct3-x').value);
    const y = parseFloat(document.getElementById('pct3-y').value);
    document.getElementById('pct3-result').innerHTML = `<p><strong>Result:</strong> ${(x/y*100).toFixed(2)}%</p>`;
}
calcPctOf();
</script>
""",

    # =========================================================================
    # STATISTICS CALCULATOR (Mean, Median, Mode)
    # =========================================================================
    "statistics": """
<div class="calculator" id="stats-calc">
    <h3>Statistics Calculator</h3>
    <label>Enter numbers (comma-separated):
        <input type="text" id="stats-input" value="5, 10, 15, 20, 20, 25, 30" style="width:100%">
    </label>
    <button onclick="calculateStats()">Calculate</button>
    <div class="calc-result" id="stats-result"></div>
</div>
<script>
function calculateStats() {
    const input = document.getElementById('stats-input').value;
    const nums = input.split(',').map(n => parseFloat(n.trim())).filter(n => !isNaN(n)).sort((a,b) => a-b);

    if (nums.length === 0) {
        document.getElementById('stats-result').innerHTML = '<p>Please enter valid numbers</p>';
        return;
    }

    // Mean
    const mean = nums.reduce((a,b) => a+b, 0) / nums.length;

    // Median
    const mid = Math.floor(nums.length / 2);
    const median = nums.length % 2 ? nums[mid] : (nums[mid-1] + nums[mid]) / 2;

    // Mode
    const freq = {};
    nums.forEach(n => freq[n] = (freq[n] || 0) + 1);
    const maxFreq = Math.max(...Object.values(freq));
    const modes = Object.keys(freq).filter(k => freq[k] === maxFreq);
    const modeStr = maxFreq === 1 ? 'No mode' : modes.join(', ');

    // Range
    const range = nums[nums.length-1] - nums[0];

    document.getElementById('stats-result').innerHTML = `
        <p><strong>Mean (Average):</strong> ${mean.toFixed(2)}</p>
        <p><strong>Median (Middle):</strong> ${median.toFixed(2)}</p>
        <p><strong>Mode (Most Frequent):</strong> ${modeStr}</p>
        <p><strong>Range:</strong> ${range.toFixed(2)}</p>
        <p><strong>Count:</strong> ${nums.length} numbers</p>
    `;
}
calculateStats();
</script>
""",

    # =========================================================================
    # STANDARD DEVIATION CALCULATOR
    # =========================================================================
    "std_dev": """
<div class="calculator" id="stddev-calc">
    <h3>Standard Deviation Calculator</h3>
    <label>Enter numbers (comma-separated):
        <input type="text" id="stddev-input" value="10, 12, 23, 23, 16, 23, 21, 16" style="width:100%">
    </label>
    <button onclick="calculateStdDev()">Calculate</button>
    <div class="calc-result" id="stddev-result"></div>
</div>
<script>
function calculateStdDev() {
    const input = document.getElementById('stddev-input').value;
    const nums = input.split(',').map(n => parseFloat(n.trim())).filter(n => !isNaN(n));

    if (nums.length < 2) {
        document.getElementById('stddev-result').innerHTML = '<p>Enter at least 2 numbers</p>';
        return;
    }

    const mean = nums.reduce((a,b) => a+b, 0) / nums.length;
    const squaredDiffs = nums.map(n => Math.pow(n - mean, 2));
    const variance = squaredDiffs.reduce((a,b) => a+b, 0) / nums.length;
    const stdDev = Math.sqrt(variance);
    const sampleStdDev = Math.sqrt(squaredDiffs.reduce((a,b) => a+b, 0) / (nums.length - 1));

    document.getElementById('stddev-result').innerHTML = `
        <p><strong>Mean:</strong> ${mean.toFixed(4)}</p>
        <p><strong>Variance:</strong> ${variance.toFixed(4)}</p>
        <p><strong>Std Deviation (Population):</strong> ${stdDev.toFixed(4)}</p>
        <p><strong>Std Deviation (Sample):</strong> ${sampleStdDev.toFixed(4)}</p>
    `;
}
calculateStdDev();
</script>
""",

    # =========================================================================
    # PYTHAGOREAN THEOREM CALCULATOR
    # =========================================================================
    "pythagorean": """
<div class="calculator" id="pyth-calc">
    <h3>Pythagorean Theorem Calculator</h3>
    <p>a² + b² = c² (find any missing side)</p>
    <div class="calc-grid">
        <label>Side a: <input type="number" id="pyth-a" placeholder="Leave blank to solve"></label>
        <label>Side b: <input type="number" id="pyth-b" placeholder="Leave blank to solve"></label>
        <label>Side c (hypotenuse): <input type="number" id="pyth-c" placeholder="Leave blank to solve"></label>
    </div>
    <button onclick="calculatePyth()">Calculate</button>
    <div class="calc-result" id="pyth-result"></div>
</div>
<script>
function calculatePyth() {
    const a = document.getElementById('pyth-a').value ? parseFloat(document.getElementById('pyth-a').value) : null;
    const b = document.getElementById('pyth-b').value ? parseFloat(document.getElementById('pyth-b').value) : null;
    const c = document.getElementById('pyth-c').value ? parseFloat(document.getElementById('pyth-c').value) : null;

    let result = '';
    if (a && b && !c) {
        const cVal = Math.sqrt(a*a + b*b);
        result = `<p><strong>c (hypotenuse) = </strong> ${cVal.toFixed(4)}</p>`;
    } else if (a && c && !b) {
        const bVal = Math.sqrt(c*c - a*a);
        result = `<p><strong>b = </strong> ${bVal.toFixed(4)}</p>`;
    } else if (b && c && !a) {
        const aVal = Math.sqrt(c*c - b*b);
        result = `<p><strong>a = </strong> ${aVal.toFixed(4)}</p>`;
    } else {
        result = '<p>Enter exactly 2 values to find the third</p>';
    }
    document.getElementById('pyth-result').innerHTML = result;
}
</script>
""",

    # =========================================================================
    # CIRCLE AREA CALCULATOR
    # =========================================================================
    "circle_area": """
<div class="calculator" id="circle-calc">
    <h3>Circle Calculator</h3>
    <label>Radius: <input type="number" id="circle-r" value="5" min="0" step="0.1"></label>
    <button onclick="calculateCircle()">Calculate</button>
    <div class="calc-result" id="circle-result"></div>
</div>
<script>
function calculateCircle() {
    const r = parseFloat(document.getElementById('circle-r').value);
    const area = Math.PI * r * r;
    const circumference = 2 * Math.PI * r;
    const diameter = 2 * r;

    document.getElementById('circle-result').innerHTML = `
        <p><strong>Area:</strong> ${area.toFixed(4)} square units</p>
        <p><strong>Circumference:</strong> ${circumference.toFixed(4)} units</p>
        <p><strong>Diameter:</strong> ${diameter.toFixed(4)} units</p>
    `;
}
calculateCircle();
</script>
""",

    # =========================================================================
    # INFLATION CALCULATOR
    # =========================================================================
    "inflation": """
<div class="calculator" id="inflation-calc">
    <h3>Inflation Calculator</h3>
    <div class="calc-grid">
        <label>Amount ($): <input type="number" id="inf-amount" value="100" min="0"></label>
        <label>Annual Inflation Rate (%): <input type="number" id="inf-rate" value="3" min="0" step="0.1"></label>
        <label>Years: <input type="number" id="inf-years" value="10" min="1" max="100"></label>
    </div>
    <button onclick="calculateInflation()">Calculate</button>
    <div class="calc-result" id="inflation-result"></div>
</div>
<script>
function calculateInflation() {
    const amount = parseFloat(document.getElementById('inf-amount').value);
    const rate = parseFloat(document.getElementById('inf-rate').value) / 100;
    const years = parseFloat(document.getElementById('inf-years').value);

    const futureValue = amount * Math.pow(1 + rate, years);
    const purchasingPower = amount / Math.pow(1 + rate, years);
    const totalInflation = ((futureValue / amount) - 1) * 100;

    document.getElementById('inflation-result').innerHTML = `
        <p><strong>$${amount} today will cost:</strong> $${futureValue.toFixed(2)} in ${years} years</p>
        <p><strong>$${amount} in ${years} years equals:</strong> $${purchasingPower.toFixed(2)} in today's dollars</p>
        <p><strong>Total inflation:</strong> ${totalInflation.toFixed(1)}%</p>
    `;
}
calculateInflation();
</script>
""",

    # =========================================================================
    # RETIREMENT CALCULATOR
    # =========================================================================
    "retirement": """
<div class="calculator" id="retire-calc">
    <h3>Retirement Savings Calculator</h3>
    <div class="calc-grid">
        <label>Current Age: <input type="number" id="ret-age" value="30" min="18" max="80"></label>
        <label>Retirement Age: <input type="number" id="ret-retire-age" value="65" min="30" max="90"></label>
        <label>Current Savings ($): <input type="number" id="ret-current" value="50000" min="0"></label>
        <label>Monthly Contribution ($): <input type="number" id="ret-monthly" value="500" min="0"></label>
        <label>Expected Return (%): <input type="number" id="ret-return" value="7" min="0" max="20" step="0.5"></label>
    </div>
    <button onclick="calculateRetirement()">Calculate</button>
    <div class="calc-result" id="retire-result"></div>
</div>
<script>
function calculateRetirement() {
    const currentAge = parseInt(document.getElementById('ret-age').value);
    const retireAge = parseInt(document.getElementById('ret-retire-age').value);
    const current = parseFloat(document.getElementById('ret-current').value);
    const monthly = parseFloat(document.getElementById('ret-monthly').value);
    const rate = parseFloat(document.getElementById('ret-return').value) / 100;

    const years = retireAge - currentAge;
    const months = years * 12;
    const monthlyRate = rate / 12;

    // Future value of current savings
    const fvCurrent = current * Math.pow(1 + rate, years);

    // Future value of monthly contributions
    const fvContributions = monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);

    const total = fvCurrent + fvContributions;
    const totalContributed = current + (monthly * months);
    const totalGrowth = total - totalContributed;

    document.getElementById('retire-result').innerHTML = `
        <p><strong>Years until retirement:</strong> ${years}</p>
        <p><strong>Total at retirement:</strong> $${total.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Total contributed:</strong> $${totalContributed.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Investment growth:</strong> $${totalGrowth.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
    `;
}
calculateRetirement();
</script>
""",

    # =========================================================================
    # PROBABILITY CALCULATOR
    # =========================================================================
    "probability": """
<div class="calculator" id="prob-calc">
    <h3>Basic Probability Calculator</h3>
    <div class="calc-grid">
        <label>Favorable Outcomes: <input type="number" id="prob-favorable" value="3" min="0"></label>
        <label>Total Possible Outcomes: <input type="number" id="prob-total" value="10" min="1"></label>
    </div>
    <button onclick="calculateProbability()">Calculate</button>
    <div class="calc-result" id="prob-result"></div>
</div>
<script>
function calculateProbability() {
    const favorable = parseInt(document.getElementById('prob-favorable').value);
    const total = parseInt(document.getElementById('prob-total').value);

    const prob = favorable / total;
    const pct = prob * 100;
    const odds = favorable + ':' + (total - favorable);

    document.getElementById('prob-result').innerHTML = `
        <p><strong>Probability:</strong> ${prob.toFixed(4)} (${pct.toFixed(2)}%)</p>
        <p><strong>Odds in favor:</strong> ${odds}</p>
        <p><strong>Odds against:</strong> ${(total-favorable)}:${favorable}</p>
    `;
}
calculateProbability();
</script>
""",

    # =========================================================================
    # NET WORTH CALCULATOR
    # =========================================================================
    "net_worth": """
<div class="calculator" id="nw-calc">
    <h3>Net Worth Calculator</h3>
    <p style="font-size:14px;color:#555;margin-bottom:12px">Add up your assets and subtract your liabilities.</p>
    <div class="calc-grid">
        <label>Cash & Savings ($)
            <input type="number" id="nw-cash" value="15000" min="0">
        </label>
        <label>Investments ($)
            <input type="number" id="nw-invest" value="50000" min="0">
        </label>
        <label>Retirement Accounts ($)
            <input type="number" id="nw-retire" value="80000" min="0">
        </label>
        <label>Property Value ($)
            <input type="number" id="nw-property" value="250000" min="0">
        </label>
        <label>Other Assets ($)
            <input type="number" id="nw-other-a" value="10000" min="0">
        </label>
        <label>Mortgage Balance ($)
            <input type="number" id="nw-mortgage" value="180000" min="0">
        </label>
        <label>Student Loans ($)
            <input type="number" id="nw-student" value="25000" min="0">
        </label>
        <label>Credit Card Debt ($)
            <input type="number" id="nw-cc" value="3000" min="0">
        </label>
        <label>Other Debts ($)
            <input type="number" id="nw-other-d" value="5000" min="0">
        </label>
    </div>
    <button onclick="calculateNetWorth()">Calculate</button>
    <div class="calc-result" id="nw-result"></div>
</div>
<script>
function calculateNetWorth() {
    const assets = ['nw-cash','nw-invest','nw-retire','nw-property','nw-other-a'].reduce((s,id) => s + (parseFloat(document.getElementById(id).value) || 0), 0);
    const liabilities = ['nw-mortgage','nw-student','nw-cc','nw-other-d'].reduce((s,id) => s + (parseFloat(document.getElementById(id).value) || 0), 0);
    const netWorth = assets - liabilities;
    const fmt = (n) => n.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
    document.getElementById('nw-result').innerHTML = `
        <p><strong>Total Assets:</strong> $${fmt(assets)}</p>
        <p><strong>Total Liabilities:</strong> $${fmt(liabilities)}</p>
        <hr style="margin:10px 0;border:none;border-top:1px solid #ddd">
        <p style="font-size:18px"><strong>Net Worth:</strong> <span style="color:${netWorth >= 0 ? '#059669' : '#DC2626'}">$${fmt(netWorth)}</span></p>
        <p><strong>Debt-to-Asset Ratio:</strong> ${assets > 0 ? (liabilities / assets * 100).toFixed(1) : 0}%</p>
    `;
}
calculateNetWorth();
</script>
""",

    # =========================================================================
    # DOLLAR COST AVERAGING CALCULATOR
    # =========================================================================
    "dca": """
<div class="calculator" id="dca-calc">
    <h3>Dollar Cost Averaging Calculator</h3>
    <div class="calc-grid">
        <label>Monthly Investment ($)
            <input type="number" id="dca-monthly" value="500" min="0">
        </label>
        <label>Time Period (years)
            <input type="number" id="dca-years" value="10" min="1" max="50">
        </label>
        <label>Expected Annual Return (%)
            <input type="number" id="dca-return" value="8" min="0" max="30" step="0.5">
        </label>
        <label>Lump Sum Alternative ($)
            <input type="number" id="dca-lump" value="60000" min="0">
        </label>
    </div>
    <button onclick="calculateDCA()">Calculate</button>
    <div class="calc-result" id="dca-result"></div>
</div>
<script>
function calculateDCA() {
    const monthly = parseFloat(document.getElementById('dca-monthly').value);
    const years = parseFloat(document.getElementById('dca-years').value);
    const rate = parseFloat(document.getElementById('dca-return').value) / 100;
    const lump = parseFloat(document.getElementById('dca-lump').value);
    const monthlyRate = rate / 12;
    const months = years * 12;
    const dcaFV = monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
    const totalInvested = monthly * months;
    const dcaGain = dcaFV - totalInvested;
    const lumpFV = lump * Math.pow(1 + rate, years);
    const lumpGain = lumpFV - lump;
    const fmt = (n) => n.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",");
    document.getElementById('dca-result').innerHTML = `
        <p><strong>DCA Final Value:</strong> $${fmt(dcaFV)}</p>
        <p><strong>Total Invested (DCA):</strong> $${fmt(totalInvested)}</p>
        <p><strong>DCA Growth:</strong> $${fmt(dcaGain)} (${(dcaGain/totalInvested*100).toFixed(1)}%)</p>
        <hr style="margin:12px 0;border:none;border-top:1px solid #ddd">
        <p><strong>Lump Sum Final Value:</strong> $${fmt(lumpFV)}</p>
        <p><strong>Lump Sum Growth:</strong> $${fmt(lumpGain)} (${(lumpGain/lump*100).toFixed(1)}%)</p>
        <p style="font-size:13px;color:#666;margin-top:8px">Lump sum typically wins in rising markets. DCA reduces timing risk.</p>
    `;
}
calculateDCA();
</script>
""",

    # =========================================================================
    # APR / APY CALCULATOR
    # =========================================================================
    "apr": """
<div class="calculator" id="apr-calc">
    <h3>APR / APY Calculator</h3>
    <div class="calc-tabs">
        <button class="tab-btn active" onclick="showAprTab('apr-to-apy')">APR &rarr; APY</button>
        <button class="tab-btn" onclick="showAprTab('apy-to-apr')">APY &rarr; APR</button>
    </div>
    <div id="apr-to-apy" class="tab-content active">
        <div class="calc-grid">
            <label>APR (%) <input type="number" id="apr-rate" value="5" min="0" max="100" step="0.01"></label>
            <label>Compounding
                <select id="apr-comp">
                    <option value="365">Daily</option>
                    <option value="12" selected>Monthly</option>
                    <option value="4">Quarterly</option>
                    <option value="2">Semi-annually</option>
                    <option value="1">Annually</option>
                </select>
            </label>
        </div>
        <button onclick="calcAPRtoAPY()">Calculate</button>
        <div class="calc-result" id="apr-apy-result"></div>
    </div>
    <div id="apy-to-apr" class="tab-content">
        <div class="calc-grid">
            <label>APY (%) <input type="number" id="apy-rate" value="5.12" min="0" max="100" step="0.01"></label>
            <label>Compounding
                <select id="apy-comp">
                    <option value="365">Daily</option>
                    <option value="12" selected>Monthly</option>
                    <option value="4">Quarterly</option>
                    <option value="2">Semi-annually</option>
                    <option value="1">Annually</option>
                </select>
            </label>
        </div>
        <button onclick="calcAPYtoAPR()">Calculate</button>
        <div class="calc-result" id="apy-apr-result"></div>
    </div>
</div>
<script>
function showAprTab(id) {
    document.querySelectorAll('#apr-calc .tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('#apr-calc .tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}
function calcAPRtoAPY() {
    const apr = parseFloat(document.getElementById('apr-rate').value) / 100;
    const n = parseFloat(document.getElementById('apr-comp').value);
    const apy = (Math.pow(1 + apr/n, n) - 1) * 100;
    document.getElementById('apr-apy-result').innerHTML = `
        <p><strong>APR:</strong> ${(apr*100).toFixed(2)}%</p>
        <p><strong>APY:</strong> ${apy.toFixed(4)}%</p>
        <p style="font-size:13px;color:#666">Compounded ${n}x per year. APY is the true annual cost/yield.</p>
    `;
}
function calcAPYtoAPR() {
    const apy = parseFloat(document.getElementById('apy-rate').value) / 100;
    const n = parseFloat(document.getElementById('apy-comp').value);
    const apr = n * (Math.pow(1 + apy, 1/n) - 1) * 100;
    document.getElementById('apy-apr-result').innerHTML = `
        <p><strong>APY:</strong> ${(apy*100).toFixed(2)}%</p>
        <p><strong>APR:</strong> ${apr.toFixed(4)}%</p>
    `;
}
calcAPRtoAPY();
</script>
""",

    # =========================================================================
    # VOLUME CALCULATOR
    # =========================================================================
    "volume": """
<div class="calculator" id="vol-calc">
    <h3>Volume Calculator</h3>
    <div class="calc-grid">
        <label>Shape
            <select id="vol-shape" onchange="updateVolFields()">
                <option value="cube">Cube</option>
                <option value="box" selected>Rectangular Prism</option>
                <option value="sphere">Sphere</option>
                <option value="cylinder">Cylinder</option>
                <option value="cone">Cone</option>
            </select>
        </label>
        <label id="vol-a-label">Length <input type="number" id="vol-a" value="5" min="0" step="0.1"></label>
        <label id="vol-b-label">Width <input type="number" id="vol-b" value="3" min="0" step="0.1"></label>
        <label id="vol-c-label">Height <input type="number" id="vol-c" value="4" min="0" step="0.1"></label>
    </div>
    <button onclick="calculateVolume()">Calculate</button>
    <div class="calc-result" id="vol-result"></div>
</div>
<script>
function updateVolFields() {
    const shape = document.getElementById('vol-shape').value;
    const bLabel = document.getElementById('vol-b-label');
    const cLabel = document.getElementById('vol-c-label');
    if (shape === 'cube') {
        document.getElementById('vol-a-label').firstChild.textContent = 'Side Length';
        bLabel.style.display = 'none'; cLabel.style.display = 'none';
    } else if (shape === 'box') {
        document.getElementById('vol-a-label').firstChild.textContent = 'Length';
        bLabel.firstChild.textContent = 'Width'; bLabel.style.display = '';
        cLabel.firstChild.textContent = 'Height'; cLabel.style.display = '';
    } else if (shape === 'sphere') {
        document.getElementById('vol-a-label').firstChild.textContent = 'Radius';
        bLabel.style.display = 'none'; cLabel.style.display = 'none';
    } else if (shape === 'cylinder') {
        document.getElementById('vol-a-label').firstChild.textContent = 'Radius';
        bLabel.firstChild.textContent = 'Height'; bLabel.style.display = '';
        cLabel.style.display = 'none';
    } else if (shape === 'cone') {
        document.getElementById('vol-a-label').firstChild.textContent = 'Radius';
        bLabel.firstChild.textContent = 'Height'; bLabel.style.display = '';
        cLabel.style.display = 'none';
    }
}
function calculateVolume() {
    const shape = document.getElementById('vol-shape').value;
    const a = parseFloat(document.getElementById('vol-a').value);
    const b = parseFloat(document.getElementById('vol-b').value);
    const c = parseFloat(document.getElementById('vol-c').value);
    let vol, formula;
    if (shape === 'cube') { vol = Math.pow(a, 3); formula = 'V = s&sup3;'; }
    else if (shape === 'box') { vol = a * b * c; formula = 'V = l &times; w &times; h'; }
    else if (shape === 'sphere') { vol = (4/3) * Math.PI * Math.pow(a, 3); formula = 'V = (4/3)&pi;r&sup3;'; }
    else if (shape === 'cylinder') { vol = Math.PI * a * a * b; formula = 'V = &pi;r&sup2;h'; }
    else if (shape === 'cone') { vol = (1/3) * Math.PI * a * a * b; formula = 'V = (1/3)&pi;r&sup2;h'; }
    document.getElementById('vol-result').innerHTML = `
        <p><strong>Volume:</strong> ${vol.toFixed(4)} cubic units</p>
        <p style="font-size:13px;color:#666">Formula: ${formula}</p>
    `;
}
calculateVolume();
</script>
""",

    # =========================================================================
    # UNIT CONVERTER
    # =========================================================================
    "unit_converter": """
<div class="calculator" id="unit-calc">
    <h3>Unit Converter</h3>
    <div class="calc-grid">
        <label>Category
            <select id="unit-cat" onchange="updateUnitOptions()">
                <option value="length">Length</option>
                <option value="weight">Weight</option>
                <option value="volume">Volume</option>
            </select>
        </label>
        <label>Value <input type="number" id="unit-val" value="1" step="any"></label>
        <label>From <select id="unit-from"></select></label>
        <label>To <select id="unit-to"></select></label>
    </div>
    <button onclick="convertUnit()">Convert</button>
    <div class="calc-result" id="unit-result"></div>
</div>
<script>
const unitData = {
    length: {meter:1, kilometer:1000, centimeter:0.01, millimeter:0.001, mile:1609.344, yard:0.9144, foot:0.3048, inch:0.0254},
    weight: {kilogram:1, gram:0.001, milligram:0.000001, pound:0.453592, ounce:0.0283495, ton:1000, 'stone':6.35029},
    volume: {liter:1, milliliter:0.001, gallon:3.78541, quart:0.946353, pint:0.473176, cup:0.236588, 'fluid ounce':0.0295735}
};
function updateUnitOptions() {
    const cat = document.getElementById('unit-cat').value;
    const units = Object.keys(unitData[cat]);
    ['unit-from','unit-to'].forEach((id,i) => {
        const sel = document.getElementById(id);
        sel.innerHTML = units.map((u,j) => '<option value="'+u+'"'+(j===i?' selected':'')+'>'+u+'</option>').join('');
    });
}
function convertUnit() {
    const cat = document.getElementById('unit-cat').value;
    const val = parseFloat(document.getElementById('unit-val').value);
    const from = document.getElementById('unit-from').value;
    const to = document.getElementById('unit-to').value;
    const base = val * unitData[cat][from];
    const result = base / unitData[cat][to];
    document.getElementById('unit-result').innerHTML = `
        <p style="font-size:20px"><strong>${val} ${from}</strong> = <strong style="color:#1a73e8">${result.toFixed(6)} ${to}</strong></p>
    `;
}
updateUnitOptions();
convertUnit();
</script>
""",

    # =========================================================================
    # LOAN REPAYMENT CALCULATOR
    # =========================================================================
    "loan_repayment": """
<div class="calculator" id="loan-repay-calc">
    <h3>Loan Repayment Calculator</h3>
    <div class="calc-grid">
        <label>Loan Amount ($)
            <input type="number" id="lr-amount" value="25000" min="0">
        </label>
        <label>Annual Interest Rate (%)
            <input type="number" id="lr-rate" value="7" min="0" max="50" step="0.1">
        </label>
        <label>Loan Term (years)
            <input type="number" id="lr-term" value="5" min="1" max="30">
        </label>
    </div>
    <button onclick="calculateLoanRepay()">Calculate</button>
    <div class="calc-result" id="lr-result"></div>
</div>
<script>
function calculateLoanRepay() {
    const P = parseFloat(document.getElementById('lr-amount').value);
    const annualRate = parseFloat(document.getElementById('lr-rate').value) / 100;
    const years = parseFloat(document.getElementById('lr-term').value);
    const r = annualRate / 12;
    const n = years * 12;

    if (r === 0) {
        const monthly = P / n;
        document.getElementById('lr-result').innerHTML = `
            <p><strong>Monthly Payment:</strong> $${monthly.toFixed(2)}</p>
            <p><strong>Total Paid:</strong> $${P.toFixed(2)}</p>
            <p><strong>Total Interest:</strong> $0.00</p>`;
        return;
    }

    const M = P * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1);
    const totalPaid = M * n;
    const totalInterest = totalPaid - P;

    let schedule = '<table style="width:100%;border-collapse:collapse;margin-top:12px;font-size:13px"><tr><th style="text-align:left;padding:6px;border-bottom:2px solid #ddd">Year</th><th style="text-align:right;padding:6px;border-bottom:2px solid #ddd">Principal</th><th style="text-align:right;padding:6px;border-bottom:2px solid #ddd">Interest</th><th style="text-align:right;padding:6px;border-bottom:2px solid #ddd">Balance</th></tr>';

    let balance = P;
    for (let y = 1; y <= years; y++) {
        let yearPrincipal = 0, yearInterest = 0;
        for (let m = 0; m < 12; m++) {
            const intPayment = balance * r;
            const princPayment = M - intPayment;
            yearInterest += intPayment;
            yearPrincipal += princPayment;
            balance -= princPayment;
        }
        if (balance < 0) balance = 0;
        schedule += `<tr><td style="padding:4px 6px;border-bottom:1px solid #eee">${y}</td><td style="text-align:right;padding:4px 6px;border-bottom:1px solid #eee">$${yearPrincipal.toFixed(2)}</td><td style="text-align:right;padding:4px 6px;border-bottom:1px solid #eee">$${yearInterest.toFixed(2)}</td><td style="text-align:right;padding:4px 6px;border-bottom:1px solid #eee">$${balance.toFixed(2)}</td></tr>`;
    }
    schedule += '</table>';

    document.getElementById('lr-result').innerHTML = `
        <p><strong>Monthly Payment:</strong> $${M.toFixed(2)}</p>
        <p><strong>Total Interest:</strong> $${totalInterest.toFixed(2)}</p>
        <p><strong>Total Cost:</strong> $${totalPaid.toFixed(2)}</p>
        <details style="margin-top:12px"><summary style="cursor:pointer;font-weight:600;color:#1a73e8">Amortization Schedule</summary>${schedule}</details>
    `;
}
calculateLoanRepay();
</script>
""",

    # =========================================================================
    # INVESTMENT RETURN CALCULATOR
    # =========================================================================
    "investment_return": """
<div class="calculator" id="invest-calc">
    <h3>Investment Return Calculator</h3>
    <div class="calc-grid">
        <label>Initial Investment ($)
            <input type="number" id="inv-initial" value="10000" min="0">
        </label>
        <label>Monthly Contribution ($)
            <input type="number" id="inv-monthly" value="500" min="0">
        </label>
        <label>Expected Annual Return (%)
            <input type="number" id="inv-return" value="8" min="0" max="50" step="0.5">
        </label>
        <label>Time Period (years)
            <input type="number" id="inv-years" value="20" min="1" max="50">
        </label>
    </div>
    <button onclick="calculateInvestReturn()">Calculate</button>
    <div class="calc-result" id="invest-result"></div>
</div>
<script>
function calculateInvestReturn() {
    const initial = parseFloat(document.getElementById('inv-initial').value);
    const monthly = parseFloat(document.getElementById('inv-monthly').value);
    const rate = parseFloat(document.getElementById('inv-return').value) / 100;
    const years = parseFloat(document.getElementById('inv-years').value);
    const monthlyRate = rate / 12;
    const months = years * 12;

    const fvInitial = initial * Math.pow(1 + monthlyRate, months);
    const fvContributions = monthly * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate);
    const total = fvInitial + fvContributions;
    const totalContributed = initial + (monthly * months);
    const totalGrowth = total - totalContributed;

    document.getElementById('invest-result').innerHTML = `
        <p><strong>Final Value:</strong> $${total.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Total Contributed:</strong> $${totalContributed.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Investment Growth:</strong> $${totalGrowth.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Return on Investment:</strong> ${((total / totalContributed - 1) * 100).toFixed(1)}%</p>
    `;
}
calculateInvestReturn();
</script>
""",

    # =========================================================================
    # CREDIT CARD PAYOFF CALCULATOR
    # =========================================================================
    "credit_card_payoff": """
<div class="calculator" id="cc-calc">
    <h3>Credit Card Payoff Calculator</h3>
    <div class="calc-grid">
        <label>Current Balance ($)
            <input type="number" id="cc-balance" value="5000" min="0">
        </label>
        <label>Annual Interest Rate (APR %)
            <input type="number" id="cc-apr" value="22" min="0" max="50" step="0.1">
        </label>
        <label>Monthly Payment ($)
            <input type="number" id="cc-payment" value="200" min="0">
        </label>
    </div>
    <button onclick="calculateCCPayoff()">Calculate</button>
    <div class="calc-result" id="cc-result"></div>
</div>
<script>
function calculateCCPayoff() {
    let balance = parseFloat(document.getElementById('cc-balance').value);
    const apr = parseFloat(document.getElementById('cc-apr').value) / 100;
    const payment = parseFloat(document.getElementById('cc-payment').value);
    const monthlyRate = apr / 12;

    if (payment <= balance * monthlyRate) {
        document.getElementById('cc-result').innerHTML = '<p style="color:#dc2626"><strong>Payment too low.</strong> Your monthly payment must exceed the monthly interest charge of $' + (balance * monthlyRate).toFixed(2) + ' to make progress.</p>';
        return;
    }

    let months = 0;
    let totalInterest = 0;
    let bal = balance;

    while (bal > 0 && months < 600) {
        const interest = bal * monthlyRate;
        totalInterest += interest;
        bal = bal + interest - payment;
        months++;
        if (bal < 0) bal = 0;
    }

    const totalPaid = balance + totalInterest;
    const yearsMonths = Math.floor(months / 12) + ' years, ' + (months % 12) + ' months';

    document.getElementById('cc-result').innerHTML = `
        <p><strong>Time to Pay Off:</strong> ${months} months (${yearsMonths})</p>
        <p><strong>Total Interest Paid:</strong> $${totalInterest.toFixed(2)}</p>
        <p><strong>Total Amount Paid:</strong> $${totalPaid.toFixed(2)}</p>
    `;
}
calculateCCPayoff();
</script>
""",

    # =========================================================================
    # EMERGENCY FUND CALCULATOR
    # =========================================================================
    "emergency_fund": """
<div class="calculator" id="ef-calc">
    <h3>Emergency Fund Calculator</h3>
    <div class="calc-grid">
        <label>Monthly Rent/Mortgage ($)
            <input type="number" id="ef-housing" value="1500" min="0">
        </label>
        <label>Monthly Utilities ($)
            <input type="number" id="ef-utilities" value="200" min="0">
        </label>
        <label>Monthly Food ($)
            <input type="number" id="ef-food" value="400" min="0">
        </label>
        <label>Monthly Transportation ($)
            <input type="number" id="ef-transport" value="300" min="0">
        </label>
        <label>Monthly Insurance ($)
            <input type="number" id="ef-insurance" value="200" min="0">
        </label>
        <label>Other Monthly Expenses ($)
            <input type="number" id="ef-other" value="200" min="0">
        </label>
        <label>Target Months
            <select id="ef-months">
                <option value="3">3 months (minimum)</option>
                <option value="6" selected>6 months (recommended)</option>
                <option value="9">9 months (conservative)</option>
                <option value="12">12 months (very conservative)</option>
            </select>
        </label>
    </div>
    <button onclick="calculateEmergencyFund()">Calculate</button>
    <div class="calc-result" id="ef-result"></div>
</div>
<script>
function calculateEmergencyFund() {
    const housing = parseFloat(document.getElementById('ef-housing').value) || 0;
    const utilities = parseFloat(document.getElementById('ef-utilities').value) || 0;
    const food = parseFloat(document.getElementById('ef-food').value) || 0;
    const transport = parseFloat(document.getElementById('ef-transport').value) || 0;
    const insurance = parseFloat(document.getElementById('ef-insurance').value) || 0;
    const other = parseFloat(document.getElementById('ef-other').value) || 0;
    const months = parseInt(document.getElementById('ef-months').value);

    const monthlyTotal = housing + utilities + food + transport + insurance + other;
    const target = monthlyTotal * months;

    document.getElementById('ef-result').innerHTML = `
        <p><strong>Monthly Essential Expenses:</strong> $${monthlyTotal.toFixed(2)}</p>
        <p><strong>Emergency Fund Target (${months} months):</strong> $${target.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <div style="margin-top:12px;font-size:13px">
            <p><strong>Breakdown:</strong></p>
            <p>Housing: $${housing.toFixed(2)} (${(housing/monthlyTotal*100).toFixed(0)}%)</p>
            <p>Utilities: $${utilities.toFixed(2)} (${(utilities/monthlyTotal*100).toFixed(0)}%)</p>
            <p>Food: $${food.toFixed(2)} (${(food/monthlyTotal*100).toFixed(0)}%)</p>
            <p>Transportation: $${transport.toFixed(2)} (${(transport/monthlyTotal*100).toFixed(0)}%)</p>
            <p>Insurance: $${insurance.toFixed(2)} (${(insurance/monthlyTotal*100).toFixed(0)}%)</p>
            <p>Other: $${other.toFixed(2)} (${(other/monthlyTotal*100).toFixed(0)}%)</p>
        </div>
    `;
}
calculateEmergencyFund();
</script>
""",

    # =========================================================================
    # INCOME TAX CALCULATOR (parameterized by country)
    # =========================================================================
    "income_tax": """
<div class="calculator" id="tax-calc">
    <h3>Income Tax Calculator</h3>
    <div class="calc-grid">
        <label>Annual Gross Income ($)
            <input type="number" id="tax-income" value="75000" min="0">
        </label>
        <label>Filing Status
            <select id="tax-status">
                <option value="single">Single</option>
                <option value="married">Married Filing Jointly</option>
                <option value="head">Head of Household</option>
            </select>
        </label>
        <label>Standard Deduction ($)
            <input type="number" id="tax-deduction" value="14600" min="0">
        </label>
    </div>
    <button onclick="calculateIncomeTax()">Calculate</button>
    <div class="calc-result" id="tax-result"></div>
</div>
<script>
function calculateIncomeTax() {
    const income = parseFloat(document.getElementById('tax-income').value);
    const deduction = parseFloat(document.getElementById('tax-deduction').value);
    const status = document.getElementById('tax-status').value;

    const taxableIncome = Math.max(0, income - deduction);

    // US 2024 brackets (simplified)
    const brackets = {
        single: [[11600, 0.10], [47150, 0.12], [100525, 0.22], [191950, 0.24], [243725, 0.32], [609350, 0.35], [Infinity, 0.37]],
        married: [[23200, 0.10], [94300, 0.12], [201050, 0.22], [383900, 0.24], [487450, 0.32], [731200, 0.35], [Infinity, 0.37]],
        head: [[16550, 0.10], [63100, 0.12], [100500, 0.22], [191950, 0.24], [243700, 0.32], [609350, 0.35], [Infinity, 0.37]]
    };

    const rates = brackets[status];
    let tax = 0;
    let prev = 0;
    let breakdownHtml = '';

    for (const [limit, rate] of rates) {
        if (taxableIncome <= prev) break;
        const taxable = Math.min(taxableIncome, limit) - prev;
        const bracketTax = taxable * rate;
        tax += bracketTax;
        if (taxable > 0) {
            breakdownHtml += '<p style="font-size:13px">' + (rate * 100).toFixed(0) + '% bracket: $' + taxable.toFixed(2) + ' = $' + bracketTax.toFixed(2) + '</p>';
        }
        prev = limit;
    }

    const effectiveRate = (tax / income * 100).toFixed(2);
    const marginalRate = rates.find(([limit]) => taxableIncome <= limit)?.[1] * 100 || 37;
    const afterTax = income - tax;

    document.getElementById('tax-result').innerHTML = `
        <p><strong>Taxable Income:</strong> $${taxableIncome.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Estimated Federal Tax:</strong> $${tax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Effective Tax Rate:</strong> ${effectiveRate}%</p>
        <p><strong>Marginal Tax Rate:</strong> ${marginalRate}%</p>
        <p><strong>After-Tax Income:</strong> $${afterTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <details style="margin-top:12px"><summary style="cursor:pointer;font-weight:600;color:#1a73e8">Tax Bracket Breakdown</summary>${breakdownHtml}</details>
    `;
}
calculateIncomeTax();
</script>
""",

    # =========================================================================
    # SALARY AFTER TAX CALCULATOR
    # =========================================================================
    "salary_after_tax": """
<div class="calculator" id="salary-calc">
    <h3>Salary After Tax Calculator</h3>
    <div class="calc-grid">
        <label>Annual Gross Salary ($)
            <input type="number" id="sal-gross" value="65000" min="0">
        </label>
        <label>Federal Tax Rate (%)
            <input type="number" id="sal-fed" value="22" min="0" max="50" step="0.5">
        </label>
        <label>State/Local Tax Rate (%)
            <input type="number" id="sal-state" value="5" min="0" max="15" step="0.5">
        </label>
        <label>Social Security (%)
            <input type="number" id="sal-ss" value="6.2" min="0" max="15" step="0.1">
        </label>
        <label>Medicare (%)
            <input type="number" id="sal-med" value="1.45" min="0" max="5" step="0.05">
        </label>
        <label>Other Deductions ($/month)
            <input type="number" id="sal-other" value="0" min="0">
        </label>
    </div>
    <button onclick="calculateSalaryNet()">Calculate</button>
    <div class="calc-result" id="salary-result"></div>
</div>
<script>
function calculateSalaryNet() {
    const gross = parseFloat(document.getElementById('sal-gross').value);
    const fedRate = parseFloat(document.getElementById('sal-fed').value) / 100;
    const stateRate = parseFloat(document.getElementById('sal-state').value) / 100;
    const ssRate = parseFloat(document.getElementById('sal-ss').value) / 100;
    const medRate = parseFloat(document.getElementById('sal-med').value) / 100;
    const otherMonthly = parseFloat(document.getElementById('sal-other').value);

    const fedTax = gross * fedRate;
    const stateTax = gross * stateRate;
    const ssTax = Math.min(gross, 168600) * ssRate;
    const medTax = gross * medRate;
    const otherAnnual = otherMonthly * 12;
    const totalDeductions = fedTax + stateTax + ssTax + medTax + otherAnnual;
    const net = gross - totalDeductions;

    document.getElementById('salary-result').innerHTML = `
        <p><strong>Annual Gross:</strong> $${gross.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Federal Tax:</strong> -$${fedTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>State/Local Tax:</strong> -$${stateTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Social Security:</strong> -$${ssTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Medicare:</strong> -$${medTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        ${otherAnnual > 0 ? '<p><strong>Other Deductions:</strong> -$' + otherAnnual.toFixed(2) + '</p>' : ''}
        <hr style="margin:12px 0;border:none;border-top:1px solid #ddd">
        <p><strong>Annual Take-Home:</strong> $${net.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Monthly Take-Home:</strong> $${(net/12).toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Effective Tax Rate:</strong> ${(totalDeductions/gross*100).toFixed(1)}%</p>
    `;
}
calculateSalaryNet();
</script>
""",

    # =========================================================================
    # CAPITAL GAINS TAX CALCULATOR
    # =========================================================================
    "capital_gains": """
<div class="calculator" id="capgains-calc">
    <h3>Capital Gains Tax Calculator</h3>
    <div class="calc-grid">
        <label>Purchase Price ($)
            <input type="number" id="cg-buy" value="10000" min="0">
        </label>
        <label>Sale Price ($)
            <input type="number" id="cg-sell" value="15000" min="0">
        </label>
        <label>Holding Period
            <select id="cg-period">
                <option value="short">Short-term (under 1 year)</option>
                <option value="long" selected>Long-term (over 1 year)</option>
            </select>
        </label>
        <label>Tax Bracket Rate (%)
            <input type="number" id="cg-rate" value="15" min="0" max="40" step="0.5">
        </label>
    </div>
    <button onclick="calculateCapGains()">Calculate</button>
    <div class="calc-result" id="capgains-result"></div>
</div>
<script>
function calculateCapGains() {
    const buyPrice = parseFloat(document.getElementById('cg-buy').value);
    const sellPrice = parseFloat(document.getElementById('cg-sell').value);
    const period = document.getElementById('cg-period').value;
    const rate = parseFloat(document.getElementById('cg-rate').value) / 100;

    const gain = sellPrice - buyPrice;
    const tax = Math.max(0, gain * rate);
    const netProfit = gain - tax;
    const returnPct = ((gain / buyPrice) * 100).toFixed(2);

    document.getElementById('capgains-result').innerHTML = `
        <p><strong>Capital Gain:</strong> $${gain.toFixed(2)}</p>
        <p><strong>Holding Period:</strong> ${period === 'long' ? 'Long-term' : 'Short-term'}</p>
        <p><strong>Estimated Tax (${(rate*100).toFixed(0)}%):</strong> $${tax.toFixed(2)}</p>
        <p><strong>Net Profit After Tax:</strong> $${netProfit.toFixed(2)}</p>
        <p><strong>Return on Investment:</strong> ${returnPct}%</p>
    `;
}
calculateCapGains();
</script>
""",

    # =========================================================================
    # VAT CALCULATOR
    # =========================================================================
    "vat_calculator": """
<div class="calculator" id="vat-calc">
    <h3>VAT / Sales Tax Calculator</h3>
    <div class="calc-grid">
        <label>Amount ($)
            <input type="number" id="vat-amount" value="100" min="0" step="0.01">
        </label>
        <label>Tax Rate (%)
            <input type="number" id="vat-rate" value="20" min="0" max="50" step="0.5">
        </label>
        <label>Direction
            <select id="vat-direction">
                <option value="add">Add tax to price</option>
                <option value="remove">Remove tax from price</option>
            </select>
        </label>
    </div>
    <button onclick="calculateVAT()">Calculate</button>
    <div class="calc-result" id="vat-result"></div>
</div>
<script>
function calculateVAT() {
    const amount = parseFloat(document.getElementById('vat-amount').value);
    const rate = parseFloat(document.getElementById('vat-rate').value) / 100;
    const direction = document.getElementById('vat-direction').value;

    if (direction === 'add') {
        const tax = amount * rate;
        const total = amount + tax;
        document.getElementById('vat-result').innerHTML = `
            <p><strong>Net Price:</strong> $${amount.toFixed(2)}</p>
            <p><strong>Tax (${(rate*100).toFixed(1)}%):</strong> $${tax.toFixed(2)}</p>
            <p><strong>Gross Price:</strong> $${total.toFixed(2)}</p>
        `;
    } else {
        const net = amount / (1 + rate);
        const tax = amount - net;
        document.getElementById('vat-result').innerHTML = `
            <p><strong>Gross Price:</strong> $${amount.toFixed(2)}</p>
            <p><strong>Tax (${(rate*100).toFixed(1)}%):</strong> $${tax.toFixed(2)}</p>
            <p><strong>Net Price:</strong> $${net.toFixed(2)}</p>
        `;
    }
}
calculateVAT();
</script>
""",

    # =========================================================================
    # PROFIT MARGIN CALCULATOR
    # =========================================================================
    "profit_margin": """
<div class="calculator" id="margin-calc">
    <h3>Profit Margin Calculator</h3>
    <div class="calc-grid">
        <label>Cost ($)
            <input type="number" id="pm-cost" value="40" min="0" step="0.01">
        </label>
        <label>Revenue / Selling Price ($)
            <input type="number" id="pm-revenue" value="100" min="0" step="0.01">
        </label>
    </div>
    <button onclick="calculateMargin()">Calculate</button>
    <div class="calc-result" id="margin-result"></div>
</div>
<script>
function calculateMargin() {
    const cost = parseFloat(document.getElementById('pm-cost').value);
    const revenue = parseFloat(document.getElementById('pm-revenue').value);

    const profit = revenue - cost;
    const marginPct = (profit / revenue * 100).toFixed(2);
    const markupPct = (profit / cost * 100).toFixed(2);

    document.getElementById('margin-result').innerHTML = `
        <p><strong>Profit:</strong> $${profit.toFixed(2)}</p>
        <p><strong>Profit Margin:</strong> ${marginPct}%</p>
        <p><strong>Markup:</strong> ${markupPct}%</p>
        <p style="font-size:13px;color:#666;margin-top:8px">Margin = Profit &divide; Revenue. Markup = Profit &divide; Cost.</p>
    `;
}
calculateMargin();
</script>
""",

    # =========================================================================
    # BREAK-EVEN CALCULATOR
    # =========================================================================
    "break_even": """
<div class="calculator" id="be-calc">
    <h3>Break-Even Calculator</h3>
    <div class="calc-grid">
        <label>Fixed Costs ($)
            <input type="number" id="be-fixed" value="10000" min="0">
        </label>
        <label>Variable Cost per Unit ($)
            <input type="number" id="be-variable" value="25" min="0" step="0.01">
        </label>
        <label>Selling Price per Unit ($)
            <input type="number" id="be-price" value="50" min="0" step="0.01">
        </label>
    </div>
    <button onclick="calculateBreakEven()">Calculate</button>
    <div class="calc-result" id="be-result"></div>
</div>
<script>
function calculateBreakEven() {
    const fixed = parseFloat(document.getElementById('be-fixed').value);
    const variable = parseFloat(document.getElementById('be-variable').value);
    const price = parseFloat(document.getElementById('be-price').value);

    if (price <= variable) {
        document.getElementById('be-result').innerHTML = '<p style="color:#dc2626"><strong>Price must exceed variable cost per unit to break even.</strong></p>';
        return;
    }

    const contribution = price - variable;
    const breakEvenUnits = Math.ceil(fixed / contribution);
    const breakEvenRevenue = breakEvenUnits * price;

    document.getElementById('be-result').innerHTML = `
        <p><strong>Contribution Margin per Unit:</strong> $${contribution.toFixed(2)}</p>
        <p><strong>Break-Even Units:</strong> ${breakEvenUnits.toLocaleString()}</p>
        <p><strong>Break-Even Revenue:</strong> $${breakEvenRevenue.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Contribution Margin Ratio:</strong> ${(contribution / price * 100).toFixed(1)}%</p>
    `;
}
calculateBreakEven();
</script>
""",

    # =========================================================================
    # ROI CALCULATOR
    # =========================================================================
    "roi_calculator": """
<div class="calculator" id="roi-calc">
    <h3>ROI Calculator</h3>
    <div class="calc-grid">
        <label>Investment Cost ($)
            <input type="number" id="roi-cost" value="10000" min="0">
        </label>
        <label>Final Value / Return ($)
            <input type="number" id="roi-return" value="13000" min="0">
        </label>
        <label>Time Period (years, optional)
            <input type="number" id="roi-years" value="3" min="0" max="100" step="0.5">
        </label>
    </div>
    <button onclick="calculateROI()">Calculate</button>
    <div class="calc-result" id="roi-result"></div>
</div>
<script>
function calculateROI() {
    const cost = parseFloat(document.getElementById('roi-cost').value);
    const finalVal = parseFloat(document.getElementById('roi-return').value);
    const years = parseFloat(document.getElementById('roi-years').value);

    const gain = finalVal - cost;
    const roi = (gain / cost * 100).toFixed(2);
    let annualized = '';

    if (years > 0) {
        const annualizedROI = (Math.pow(finalVal / cost, 1 / years) - 1) * 100;
        annualized = `<p><strong>Annualized ROI:</strong> ${annualizedROI.toFixed(2)}%</p>`;
    }

    document.getElementById('roi-result').innerHTML = `
        <p><strong>Net Gain/Loss:</strong> $${gain.toFixed(2)}</p>
        <p><strong>ROI:</strong> ${roi}%</p>
        ${annualized}
    `;
}
calculateROI();
</script>
""",

    # =========================================================================
    # MARKUP CALCULATOR
    # =========================================================================
    "markup_calculator": """
<div class="calculator" id="markup-calc">
    <h3>Markup Calculator</h3>
    <div class="calc-tabs">
        <button class="tab-btn active" onclick="showMarkupTab('mu-forward')">Cost + Markup</button>
        <button class="tab-btn" onclick="showMarkupTab('mu-reverse')">Find Markup</button>
    </div>
    <div id="mu-forward" class="tab-content active">
        <div class="calc-grid">
            <label>Cost ($) <input type="number" id="mu-cost" value="50" min="0" step="0.01"></label>
            <label>Markup (%) <input type="number" id="mu-pct" value="60" min="0" step="0.5"></label>
        </div>
        <button onclick="calcMarkupForward()">Calculate</button>
        <div class="calc-result" id="mu-fwd-result"></div>
    </div>
    <div id="mu-reverse" class="tab-content">
        <div class="calc-grid">
            <label>Cost ($) <input type="number" id="mu-rev-cost" value="50" min="0" step="0.01"></label>
            <label>Selling Price ($) <input type="number" id="mu-rev-price" value="80" min="0" step="0.01"></label>
        </div>
        <button onclick="calcMarkupReverse()">Calculate</button>
        <div class="calc-result" id="mu-rev-result"></div>
    </div>
</div>
<script>
function showMarkupTab(id) {
    document.querySelectorAll('#markup-calc .tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('#markup-calc .tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
}
function calcMarkupForward() {
    const cost = parseFloat(document.getElementById('mu-cost').value);
    const pct = parseFloat(document.getElementById('mu-pct').value) / 100;
    const price = cost * (1 + pct);
    const profit = price - cost;
    const margin = (profit / price * 100).toFixed(2);
    document.getElementById('mu-fwd-result').innerHTML = `
        <p><strong>Selling Price:</strong> $${price.toFixed(2)}</p>
        <p><strong>Profit:</strong> $${profit.toFixed(2)}</p>
        <p><strong>Profit Margin:</strong> ${margin}%</p>
    `;
}
function calcMarkupReverse() {
    const cost = parseFloat(document.getElementById('mu-rev-cost').value);
    const price = parseFloat(document.getElementById('mu-rev-price').value);
    const markup = ((price - cost) / cost * 100).toFixed(2);
    const margin = ((price - cost) / price * 100).toFixed(2);
    document.getElementById('mu-rev-result').innerHTML = `
        <p><strong>Markup:</strong> ${markup}%</p>
        <p><strong>Profit Margin:</strong> ${margin}%</p>
        <p><strong>Profit:</strong> $${(price - cost).toFixed(2)}</p>
    `;
}
calcMarkupForward();
</script>
""",

    # =========================================================================
    # BMI CALCULATOR
    # =========================================================================
    "bmi_calculator": """
<div class="calculator" id="bmi-calc">
    <h3>BMI Calculator</h3>
    <div class="calc-grid">
        <label>Unit System
            <select id="bmi-unit" onchange="toggleBMIUnits()">
                <option value="imperial">Imperial (lbs, ft/in)</option>
                <option value="metric">Metric (kg, cm)</option>
            </select>
        </label>
        <label id="bmi-weight-label">Weight (lbs)
            <input type="number" id="bmi-weight" value="170" min="0">
        </label>
        <label id="bmi-height-label">Height (inches)
            <input type="number" id="bmi-height" value="70" min="0" step="0.5">
        </label>
    </div>
    <button onclick="calculateBMI()">Calculate</button>
    <div class="calc-result" id="bmi-result"></div>
</div>
<script>
function toggleBMIUnits() {
    const unit = document.getElementById('bmi-unit').value;
    if (unit === 'metric') {
        document.getElementById('bmi-weight-label').firstChild.textContent = 'Weight (kg)';
        document.getElementById('bmi-height-label').firstChild.textContent = 'Height (cm)';
        document.getElementById('bmi-weight').value = '77';
        document.getElementById('bmi-height').value = '178';
    } else {
        document.getElementById('bmi-weight-label').firstChild.textContent = 'Weight (lbs)';
        document.getElementById('bmi-height-label').firstChild.textContent = 'Height (inches)';
        document.getElementById('bmi-weight').value = '170';
        document.getElementById('bmi-height').value = '70';
    }
}
function calculateBMI() {
    const unit = document.getElementById('bmi-unit').value;
    let weight = parseFloat(document.getElementById('bmi-weight').value);
    let height = parseFloat(document.getElementById('bmi-height').value);

    let bmi;
    if (unit === 'imperial') {
        bmi = (weight / (height * height)) * 703;
    } else {
        bmi = weight / Math.pow(height / 100, 2);
    }

    let category, color;
    if (bmi < 18.5) { category = 'Underweight'; color = '#2563EB'; }
    else if (bmi < 25) { category = 'Normal weight'; color = '#059669'; }
    else if (bmi < 30) { category = 'Overweight'; color = '#D97706'; }
    else { category = 'Obese'; color = '#DC2626'; }

    document.getElementById('bmi-result').innerHTML = `
        <p><strong>Your BMI:</strong> ${bmi.toFixed(1)}</p>
        <p><strong>Category:</strong> <span style="color:${color};font-weight:600">${category}</span></p>
        <div style="margin-top:12px;font-size:13px;color:#666">
            <p>Underweight: below 18.5 | Normal: 18.5 &ndash; 24.9 | Overweight: 25 &ndash; 29.9 | Obese: 30+</p>
        </div>
    `;
}
calculateBMI();
</script>
""",

    # =========================================================================
    # CALORIE CALCULATOR (Mifflin-St Jeor)
    # =========================================================================
    "calorie_calculator": """
<div class="calculator" id="cal-calc">
    <h3>Daily Calorie Calculator</h3>
    <div class="calc-grid">
        <label>Gender
            <select id="cal-gender">
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>
        </label>
        <label>Age (years)
            <input type="number" id="cal-age" value="30" min="15" max="100">
        </label>
        <label>Weight (kg)
            <input type="number" id="cal-weight" value="75" min="30" max="300">
        </label>
        <label>Height (cm)
            <input type="number" id="cal-height" value="175" min="100" max="250">
        </label>
        <label>Activity Level
            <select id="cal-activity">
                <option value="1.2">Sedentary (office job)</option>
                <option value="1.375">Light (1-3 days/week)</option>
                <option value="1.55" selected>Moderate (3-5 days/week)</option>
                <option value="1.725">Active (6-7 days/week)</option>
                <option value="1.9">Very Active (physical job + exercise)</option>
            </select>
        </label>
    </div>
    <button onclick="calculateCalories()">Calculate</button>
    <div class="calc-result" id="cal-result"></div>
</div>
<script>
function calculateCalories() {
    const gender = document.getElementById('cal-gender').value;
    const age = parseFloat(document.getElementById('cal-age').value);
    const weight = parseFloat(document.getElementById('cal-weight').value);
    const height = parseFloat(document.getElementById('cal-height').value);
    const activity = parseFloat(document.getElementById('cal-activity').value);

    let bmr;
    if (gender === 'male') {
        bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
        bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }

    const maintenance = bmr * activity;
    const lose = maintenance - 500;
    const gain = maintenance + 500;

    document.getElementById('cal-result').innerHTML = `
        <p><strong>Basal Metabolic Rate (BMR):</strong> ${Math.round(bmr)} cal/day</p>
        <p><strong>Maintenance Calories:</strong> ${Math.round(maintenance)} cal/day</p>
        <p><strong>Weight Loss (~0.5 kg/week):</strong> ${Math.round(lose)} cal/day</p>
        <p><strong>Weight Gain (~0.5 kg/week):</strong> ${Math.round(gain)} cal/day</p>
        <p style="font-size:13px;color:#666;margin-top:8px">Based on the Mifflin-St Jeor equation.</p>
    `;
}
calculateCalories();
</script>
""",

    # =========================================================================
    # CURRENCY CONVERTER (static reference rates)
    # =========================================================================
    "currency_converter": """
<div class="calculator" id="fx-calc">
    <h3>Currency Converter</h3>
    <p style="font-size:13px;color:#666;margin-bottom:12px">Reference rates for estimation. Not live market rates.</p>
    <div class="calc-grid">
        <label>Amount
            <input type="number" id="fx-amount" value="1000" min="0" step="0.01">
        </label>
        <label>From
            <select id="fx-from">
                <option value="USD">USD — US Dollar</option>
                <option value="EUR">EUR — Euro</option>
                <option value="GBP">GBP — British Pound</option>
                <option value="JPY">JPY — Japanese Yen</option>
                <option value="CAD">CAD — Canadian Dollar</option>
                <option value="AUD">AUD — Australian Dollar</option>
                <option value="INR">INR — Indian Rupee</option>
                <option value="BRL">BRL — Brazilian Real</option>
                <option value="NGN">NGN — Nigerian Naira</option>
                <option value="KES">KES — Kenyan Shilling</option>
                <option value="ZAR">ZAR — South African Rand</option>
                <option value="CNY">CNY — Chinese Yuan</option>
            </select>
        </label>
        <label>To
            <select id="fx-to">
                <option value="USD">USD — US Dollar</option>
                <option value="EUR" selected>EUR — Euro</option>
                <option value="GBP">GBP — British Pound</option>
                <option value="JPY">JPY — Japanese Yen</option>
                <option value="CAD">CAD — Canadian Dollar</option>
                <option value="AUD">AUD — Australian Dollar</option>
                <option value="INR">INR — Indian Rupee</option>
                <option value="BRL">BRL — Brazilian Real</option>
                <option value="NGN">NGN — Nigerian Naira</option>
                <option value="KES">KES — Kenyan Shilling</option>
                <option value="ZAR">ZAR — South African Rand</option>
                <option value="CNY">CNY — Chinese Yuan</option>
            </select>
        </label>
    </div>
    <button onclick="convertCurrency()">Convert</button>
    <div class="calc-result" id="fx-result"></div>
</div>
<script>
function convertCurrency() {
    // Reference rates vs USD (approximate)
    const rates = {USD:1, EUR:0.92, GBP:0.79, JPY:149.5, CAD:1.36, AUD:1.53, INR:83.1, BRL:4.97, NGN:1550, KES:153, ZAR:18.6, CNY:7.24};
    const amount = parseFloat(document.getElementById('fx-amount').value);
    const from = document.getElementById('fx-from').value;
    const to = document.getElementById('fx-to').value;

    const inUSD = amount / rates[from];
    const result = inUSD * rates[to];
    const rate = rates[to] / rates[from];

    document.getElementById('fx-result').innerHTML = `
        <p><strong>${amount.toFixed(2)} ${from} =</strong></p>
        <p style="font-size:24px;font-weight:700;color:#1a73e8">${result.toFixed(2)} ${to}</p>
        <p style="font-size:13px;color:#666">Rate: 1 ${from} = ${rate.toFixed(4)} ${to}</p>
    `;
}
convertCurrency();
</script>
""",

    # =========================================================================
    # TEMPERATURE CONVERTER
    # =========================================================================
    "temperature_converter": """
<div class="calculator" id="temp-calc">
    <h3>Temperature Converter</h3>
    <div class="calc-grid">
        <label>Temperature
            <input type="number" id="temp-val" value="100" step="0.1">
        </label>
        <label>From
            <select id="temp-from">
                <option value="C">Celsius (°C)</option>
                <option value="F">Fahrenheit (°F)</option>
                <option value="K">Kelvin (K)</option>
            </select>
        </label>
    </div>
    <button onclick="convertTemp()">Convert</button>
    <div class="calc-result" id="temp-result"></div>
</div>
<script>
function convertTemp() {
    const val = parseFloat(document.getElementById('temp-val').value);
    const from = document.getElementById('temp-from').value;

    let c, f, k;
    if (from === 'C') { c = val; f = val * 9/5 + 32; k = val + 273.15; }
    else if (from === 'F') { c = (val - 32) * 5/9; f = val; k = (val - 32) * 5/9 + 273.15; }
    else { c = val - 273.15; f = (val - 273.15) * 9/5 + 32; k = val; }

    document.getElementById('temp-result').innerHTML = `
        <p><strong>Celsius:</strong> ${c.toFixed(2)} °C</p>
        <p><strong>Fahrenheit:</strong> ${f.toFixed(2)} °F</p>
        <p><strong>Kelvin:</strong> ${k.toFixed(2)} K</p>
        <div style="margin-top:12px;font-size:13px;color:#666">
            <p>°F = °C × 9/5 + 32</p>
            <p>°C = (°F − 32) × 5/9</p>
            <p>K = °C + 273.15</p>
        </div>
    `;
}
convertTemp();
</script>
""",

    # =========================================================================
    # SELF-EMPLOYMENT TAX CALCULATOR
    # =========================================================================
    "self_employment_tax": """
<div class="calculator" id="se-calc">
    <h3>Self-Employment Tax Calculator</h3>
    <div class="calc-grid">
        <label>Net Self-Employment Income ($)
            <input type="number" id="se-income" value="80000" min="0">
        </label>
        <label>Social Security Rate (%)
            <input type="number" id="se-ss" value="12.4" min="0" max="20" step="0.1">
        </label>
        <label>Medicare Rate (%)
            <input type="number" id="se-med" value="2.9" min="0" max="10" step="0.1">
        </label>
        <label>SS Wage Base ($)
            <input type="number" id="se-base" value="168600" min="0">
        </label>
    </div>
    <button onclick="calculateSETax()">Calculate</button>
    <div class="calc-result" id="se-result"></div>
</div>
<script>
function calculateSETax() {
    const income = parseFloat(document.getElementById('se-income').value);
    const ssRate = parseFloat(document.getElementById('se-ss').value) / 100;
    const medRate = parseFloat(document.getElementById('se-med').value) / 100;
    const ssBase = parseFloat(document.getElementById('se-base').value);

    const taxableBase = income * 0.9235;
    const ssTax = Math.min(taxableBase, ssBase) * ssRate;
    const medTax = taxableBase * medRate;
    const additionalMed = taxableBase > 200000 ? (taxableBase - 200000) * 0.009 : 0;
    const totalSE = ssTax + medTax + additionalMed;
    const deduction = totalSE / 2;

    document.getElementById('se-result').innerHTML = `
        <p><strong>Taxable SE Base (92.35%):</strong> $${taxableBase.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Social Security Tax:</strong> $${ssTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Medicare Tax:</strong> $${medTax.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        ${additionalMed > 0 ? '<p><strong>Additional Medicare:</strong> $' + additionalMed.toFixed(2) + '</p>' : ''}
        <p><strong>Total SE Tax:</strong> $${totalSE.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
        <p><strong>Deductible Portion (50%):</strong> $${deduction.toFixed(2).replace(/\\B(?=(\\d{3})+(?!\\d))/g, ",")}</p>
    `;
}
calculateSETax();
</script>
""",

}


# =============================================================================
# SHARED CALCULATOR STYLES
# =============================================================================

CALCULATOR_STYLES = """
<style>
.calculator {
    background: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin: 24px 0;
}
.calculator h3 {
    margin-top: 0;
    color: #1a73e8;
}
.calc-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}
.calculator label {
    display: block;
    font-size: 14px;
    color: #555;
}
.calculator input, .calculator select {
    width: 100%;
    padding: 8px;
    margin-top: 4px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}
.calculator button {
    background: #1a73e8;
    color: white;
    border: none;
    padding: 10px 24px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}
.calculator button:hover {
    background: #1557b0;
}
.calc-result {
    margin-top: 16px;
    padding: 12px;
    background: white;
    border-radius: 4px;
    border-left: 4px solid #1a73e8;
}
.calc-result p {
    margin: 8px 0;
}
.calc-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
}
.tab-btn {
    background: #e0e0e0;
    color: #333;
}
.tab-btn.active {
    background: #1a73e8;
    color: white;
}
.tab-content {
    display: none;
}
.tab-content.active {
    display: block;
}
</style>
"""


def get_calculator_html(topic):
    """
    Get the calculator HTML for a topic, if applicable.
    Returns None if no calculator is needed.
    """
    calc_type = get_calculator_for_topic(topic)

    if calc_type and calc_type in CALCULATORS:
        return CALCULATOR_STYLES + CALCULATORS[calc_type]

    return None


def get_calculator_by_key(key):
    """Get calculator HTML by its direct key (for tool pages).
    Returns (styles, html) tuple or (None, None) if not found."""
    if key in CALCULATORS:
        return CALCULATOR_STYLES, CALCULATORS[key]
    return None, None


def get_all_calculator_topics():
    """Get list of all topics that have calculators."""
    return [topic for topic, calc in CALCULATOR_TOPICS.items() if calc is not None]


if __name__ == "__main__":
    print("Topics with calculators:")
    print("=" * 40)
    for topic in get_all_calculator_topics():
        print(f"  - {topic}")
    print(f"\nTotal: {len(get_all_calculator_topics())} topics")
