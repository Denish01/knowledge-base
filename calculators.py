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


def get_all_calculator_topics():
    """Get list of all topics that have calculators."""
    return [topic for topic, calc in CALCULATOR_TOPICS.items() if calc is not None]


if __name__ == "__main__":
    print("Topics with calculators:")
    print("=" * 40)
    for topic in get_all_calculator_topics():
        print(f"  - {topic}")
    print(f"\nTotal: {len(get_all_calculator_topics())} topics")
