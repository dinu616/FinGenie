from .utils import AgentState

def reporter_agent(state: AgentState):
    """Consolidates all analysis outputs into professional HTML report"""
    
    # Professional HTML template with Perplexity-inspired styling
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: #1a202c;
        }}
        .report-container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
            color: white;
            padding: 2.5rem;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}
        .header p {{
            font-size: 1.1rem;
            opacity: 0.95;
        }}
        .customer-grid {{
            display: grid;
            gap: 2rem;
            padding: 2.5rem;
        }}
        .customer-card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .customer-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        .customer-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        .customer-id {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #2d3748;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .section {{
            margin-bottom: 1.5rem;
        }}
        .section-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #4a5568;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #ebf4ff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .profile-item, .reco-item {{
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 1.25rem;
            border-radius: 12px;
            border-left: 4px solid #4299e1;
        }}
        .profile-name, .reco-card {{
            font-weight: 600;
            font-size: 1.05rem;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }}
        .profile-reason, .reco-reason {{
            color: #4a5568;
            line-height: 1.6;
        }}
        .summary-text {{
            background: #f7fafc;
            padding: 1.25rem;
            border-radius: 12px;
            border-left: 4px solid #48bb78;
            line-height: 1.7;
        }}
        .no-data {{
            color: #a0aec0;
            font-style: italic;
            text-align: center;
            padding: 2rem;
        }}
        @media (max-width: 768px) {{
            .customer-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="report-container">
        <div class="header">
            <h1>🏦 Customer Wealth Management Analysis</h1>
            <p>Comprehensive profile analysis with credit card recommendations</p>
        </div>
        <div class="customer-grid">
            {customer_sections}
        </div>
    </div>
</body>
</html>
    """.strip()

    customer_sections = []
    
    # Process each customer from demographic results (primary source)
    for demo_item in state.get("demographic_results", []):
        customer_id = getattr(demo_item, "customer_id", "UNKNOWN")
        
        # Find matching data across all analyses
        def find_matching(item_list, customer_id):
            return next((item for item in item_list or [] 
                        if getattr(item, "customer_id", None) == customer_id), None)
        
        trx_analysis = find_matching(state.get("transaction_results", []), customer_id)
        income_analysis = find_matching(state.get("income_results", []), customer_id)
        cc_holdings = find_matching(state.get("cc_holding_results", []), customer_id)
        cc_recos = find_matching(state.get("cc_results", []), customer_id)
        
        # Behavioral Profiles Section
        profiles_html = '<div class="no-data">No behavioral profiles identified</div>'
        if trx_analysis and hasattr(trx_analysis, 'profiles') and trx_analysis.profiles:
            profiles_html = '<div class="profile-grid">'
            for profile in trx_analysis.profiles:
                profiles_html += f'''
                <div class="profile-item">
                    <div class="profile-name">{getattr(profile, "profile_name", "Unnamed")}</div>
                    <div class="profile-reason">{getattr(profile, "reason", "No reason provided")}</div>
                </div>
                '''
            profiles_html += '</div>'
        
        # Credit Card Recommendations
        recos_html = '<div class="no-data">No credit card recommendations</div>'
        if cc_recos and hasattr(cc_recos, 'cc_summary') and cc_recos.cc_summary:
            recos_html = '<div class="profile-grid">'
            for reco in cc_recos.cc_summary:
                recos_html += f'''
                <div class="reco-item">
                    <div class="reco-card">{getattr(reco, "cc_recommended", "Unnamed Card")}</div>
                    <div class="reco-reason">{getattr(reco, "recommended_reasons", "No reason provided")}</div>
                </div>
                '''
            recos_html += '</div>'
        
        # Build customer section
        customer_section = f'''
        <div class="customer-card">
            <div class="customer-header">
                <div class="customer-id">ID: {customer_id}</div>
            </div>
            
            <div class="section">
                <div class="section-title">📊 Demographic Summary</div>
                <div class="summary-text">{getattr(demo_item, "summary", "No demographic data")}</div>
            </div>
            
            <div class="section">
                <div class="section-title">💳 Behavioral Profiles</div>
                {profiles_html}
            </div>
            
            <div class="section">
                <div class="section-title">💰 Income Analysis</div>
                <div class="summary-text">
                    {getattr(income_analysis, "income_info", "No income data available") if income_analysis else "No income data"}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🏦 Current Credit Cards</div>
                <div class="summary-text">
                    {getattr(cc_holdings, "cc_holding_info", "No CC holdings") if cc_holdings else "No CC holdings data"}
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">🎯 Recommended Credit Cards</div>
                {recos_html}
            </div>
        </div>
        '''
        
        customer_sections.append(customer_section)
    
    # Handle empty results
    if not customer_sections:
        customer_sections.append('<div class="no-data">No customer data available for analysis</div>')
    
    final_html = html_template.format(customer_sections=''.join(customer_sections))
    
    return {
        "final_table": final_html,
        "sender": "reporter"
    }
