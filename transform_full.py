import re
import os

def add_lw_attributes(html):
    # h1-h6
    def h_repl(match):
        tag = match.group(1)
        attrs = match.group(2)
        content = match.group(3)
        if 'learnworlds-element' not in attrs:
            if 'class="' in attrs:
                attrs = attrs.replace('class="', 'class="learnworlds-element learnworlds-heading ')
            else:
                attrs = f' class="learnworlds-element learnworlds-heading"{attrs}'
        if 'data-node-type' not in attrs:
            attrs += ' data-node-type="text"'
        if 'contenteditable' not in attrs:
            attrs += ' contenteditable="true"'
        return f'<{tag}{attrs}>{content}</{tag}>'
    
    html = re.sub(r'<(h[1-6])\b([^>]*)>(.*?)</\1>', h_repl, html, flags=re.S)
    
    # p
    def p_repl(match):
        attrs = match.group(1)
        content = match.group(2)
        if 'learnworlds-element' not in attrs:
            if 'class="' in attrs:
                attrs = attrs.replace('class="', 'class="learnworlds-element ')
            else:
                attrs = f' class="learnworlds-element"{attrs}'
        if 'data-node-type' not in attrs:
            attrs += ' data-node-type="text"'
        if 'contenteditable' not in attrs:
            attrs += ' contenteditable="true"'
        return f'<p{attrs}>{content}</p>'
    
    html = re.sub(r'<p\b([^>]*)>(.*?)</p>', p_repl, html, flags=re.S)

    # li, td, th, span, div (if they have text and no complex children)
    def text_tag_repl(match):
        tag = match.group(1)
        attrs = match.group(2)
        content = match.group(3)
        text_only = re.sub(r'<[^>]+>', '', content).strip()
        if text_only and len(text_only) > 0 and not re.search(r'<(h[1-6]|p|section|div|ul|ol|table)\b', content):
            if 'learnworlds-element' not in attrs:
                if 'class="' in attrs:
                    attrs = attrs.replace('class="', 'class="learnworlds-element ')
                else:
                    attrs = f' class="learnworlds-element"{attrs}'
            if 'data-node-type' not in attrs:
                attrs += ' data-node-type="text"'
            if 'contenteditable' not in attrs:
                attrs += ' contenteditable="true"'
        return f'<{tag}{attrs}>{content}</{tag}>'
    
    html = re.sub(r'<(li|td|th|span|div)\b([^>]*)>(.*?)</\1>', text_tag_repl, html, flags=re.S)
    
    # a/buttons
    def a_repl(match):
        attrs = match.group(1)
        content = match.group(2)
        if 'btn' in attrs or 'nav-signin' in attrs or 'nav-links' in attrs:
            if 'learnworlds-element' not in attrs:
                if 'class="' in attrs:
                    attrs = attrs.replace('class="', 'class="learnworlds-element learnworlds-button ')
                else:
                    attrs = f' class="learnworlds-element learnworlds-button"{attrs}'
            if 'data-node-type' not in attrs:
                attrs += ' data-node-type="button"'
        return f'<a{attrs}>{content}</a>'
    
    html = re.sub(r'<a\b([^>]*)>(.*?)</a>', a_repl, html, flags=re.S)
    
    # images
    def img_repl(match):
        attrs = match.group(1)
        if 'learnworlds-element' not in attrs:
            if 'class="' in attrs:
                attrs = attrs.replace('class="', 'class="learnworlds-element learnworlds-image ')
            else:
                attrs = f' class="learnworlds-element learnworlds-image"{attrs}'
        if 'data-node-type' not in attrs:
            attrs += ' data-node-type="image"'
        return f'<img{attrs}>'
    
    html = re.sub(r'<img\b([^>]*)>', img_repl, html)
    
    return html

def transform():
    with open('src/ClaudeCode.html', 'r') as f:
        content = f.read()

    # Extract CSS
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.S)
    css_content = "\n".join(style_blocks)
    css_content = css_content.replace(':root', '.lw-caseclinical-wrapper')
    css_content = re.sub(r'(html|body|\*)\s*\{[^}]*\}', '', css_content)
    
    overrides = """
/* LW Platform Overrides */
.lw-caseclinical-wrapper {
    width: 100vw !important;
    max-width: 100vw !important;
    position: relative !important;
    left: 50% !important;
    margin-left: -50vw !important;
    display: block !important;
    overflow: visible !important;
    min-height: 100vh !important;
    background: #ffffff !important;
    z-index: 1;
}

:is(.learnworlds-section, .learnworlds-section-content, .js-learnworlds-section):has(.lw-caseclinical-wrapper) {
    width: 100% !important;
    max-width: none !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
}

.lw-caseclinical-wrapper .navbar {
    position: fixed !important;
    width: 100% !important;
    left: 0 !important;
    top: 0 !important;
    z-index: 9999 !important;
    background: rgba(255, 255, 255, 0.95) !important;
}

/* Force visibility of all elements in the editor and on load */
.lw-caseclinical-wrapper [data-reveal] {
    opacity: 1 !important;
    transform: none !important;
    transition: opacity 0.8s ease, transform 0.8s ease !important;
}

/* Fix for mockups and graphs */
.lw-caseclinical-wrapper .segment {
    transition: stroke-dashoffset 1.2s ease-in-out !important;
}
.lw-caseclinical-wrapper .chart-line {
    stroke-dashoffset: 0 !important;
    transition: stroke-dashoffset 2.5s ease-out !important;
}
.lw-caseclinical-wrapper .chart-area {
    opacity: 0.15 !important;
    transition: opacity 1s ease-out 1.5s !important;
}

/* Ecosystem Portal Cards Hover Effect */
.lw-caseclinical-wrapper .portal-card {
    transition: border-color 0.4s ease, transform 0.4s ease, box-shadow 0.4s ease !important;
    border: 2px solid transparent !important;
}
.lw-caseclinical-wrapper .portal-card:hover {
    border-color: #2d6fe8 !important;
    transform: translateY(-8px) !important;
    box-shadow: 0 20px 40px rgba(45, 111, 232, 0.12) !important;
}

/* Fix Provider Portal Card in Ecosystem */
.lw-caseclinical-wrapper .portal-card.provider-fix {
    background: #f0f7ff !important;
    border: 2px solid #2d6fe8 !important;
    direction: ltr !important;
    box-shadow: 0 20px 40px rgba(45, 111, 232, 0.1) !important;
}
.lw-caseclinical-wrapper .portal-card.provider-fix > * {
    direction: ltr !important;
}
.lw-caseclinical-wrapper .portal-card.provider-fix .portal-badge {
    background: #2d6fe8 !important;
    color: #fff !important;
}
"""
    css_content = overrides + "\n" + css_content

    # Extract Body HTML
    body_match = re.search(r'<body>(.*?)<script>', content, re.S)
    html_content = body_match.group(1).strip() if body_match else ""

    # Fix mockups values
    html_content = re.sub(r'(<[^>]+class="[^"]*count-up[^"]*"[^>]*data-target="(\d+)"[^>]*>).*?(</[^>]+>)', 
                          r'\1\2\3', html_content)

    # Fix Provider Portal card
    html_content = html_content.replace('<!-- Provider Portal -->\n          <div class="portal-card reverse"', 
                                      '<!-- Provider Portal -->\n          <div class="portal-card provider-fix"')

    # Add LearnWorlds attributes
    html_content = add_lw_attributes(html_content)

    # Extract Script
    script_match = re.search(r'<script>(.*?)</script>', content, re.S)
    js_content = script_match.group(1).strip() if script_match else ""

    final_html = f"""
<div class="lw-caseclinical-wrapper" id="section_claudecode">
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap" rel="stylesheet" />
    
    {html_content}

    <script>
    (function() {{
        function init() {{
            console.log('CaseClinical: Initializing...');
            const wrapper = document.getElementById('section_claudecode');
            if (wrapper) wrapper.classList.add('js-initialized');
            
            // Force visibility of all reveal elements
            setTimeout(() => {{
                document.querySelectorAll('.lw-caseclinical-wrapper [data-reveal]').forEach(el => {{
                    el.classList.add('visible');
                }});
                
                // Trigger Donut animation with fixed logic
                document.querySelectorAll('.lw-caseclinical-wrapper .donut-container').forEach(container => {{
                    const circles = container.querySelectorAll('.segment');
                    const radius = 45;
                    const circumference = 2 * Math.PI * radius;
                    let currentAccumulated = 0;
                    
                    circles.forEach((circle, index) => {{
                        const percent = Number(circle.dataset.percent);
                        const dashLength = (percent / 100) * circumference;
                        const gapLength = circumference - dashLength;
                        
                        // Set the dash pattern
                        circle.style.strokeDasharray = `${{dashLength}} ${{gapLength}}`;
                        
                        // The offset shifts the dash clockwise by the accumulated amount
                        // We use negative offset to move the dash clockwise
                        const offset = -(currentAccumulated / 100) * circumference;
                        
                        // Initial state: hidden (offset 0 with transition will look weird, so we set it)
                        circle.style.strokeDashoffset = circumference;
                        
                        setTimeout(() => {{
                            circle.style.strokeDashoffset = offset;
                        }}, index * 150 + 400);
                        
                        currentAccumulated += percent;
                    }});
                }});
            }}, 500);

            {js_content}
        }}
        if (document.readyState === 'loading') {{ document.addEventListener('DOMContentLoaded', init); }}
        else {{ setTimeout(init, 200); }}
    }})();
    </script>
</div>
"""

    os.makedirs('learnWorlds/dist', exist_ok=True)
    with open('learnWorlds/dist/site_custom_code.css', 'w') as f:
        f.write(css_content)
    with open('learnWorlds/dist/section_html.html', 'w') as f:
        f.write(final_html)
    
    print("Full Transformation complete.")

if __name__ == "__main__":
    transform()
