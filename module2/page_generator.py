# ============================================================
# MODULE 2: PROGRAMMATIC SEO PAGE GENERATOR
# ============================================================
# What this file does:
# 1. Reads your CSV data (cities + services)
# 2. For each row, fills in the HTML template
# 3. Saves a complete HTML page
# 4. Creates a sitemap.xml for Google
# 5. Shows a summary of what was generated
# ============================================================

# --- IMPORTS (Tools we're borrowing) ---
# Think of imports like getting tools from a toolbox

import os           # Lets Python talk to your computer's files/folders
import json         # Handles JSON data (like a dictionary format)
import pandas as pd # Reads CSV/Excel files like a spreadsheet
from jinja2 import Environment, FileSystemLoader  # Our template filler
from datetime import datetime  # Gets current date and time
import re           # Regular expressions - for cleaning text

# ============================================================
# CONFIGURATION - Change these settings to customize
# ============================================================
# This is like the "settings menu" of our program

CONFIG = {
    # Where is your CSV data file?
    "data_file": "data/keywords_data.csv",
    
    # Where are your HTML templates?
    "templates_dir": "templates",
    
    # Where should generated pages be saved?
    "output_dir": "output",
    
    # What's your website URL? (change this to your real URL later)
    "base_url": "http://localhost:5000",
    
    # Your website name
    "site_name": "SEO Automation Command Center",
    
    # What template file to use?
    "template_file": "city_service_page.html"
}

# ============================================================
# FEATURE DEFINITIONS
# ============================================================
# Each service has different features to show on the page
# This is a dictionary (like a lookup table)
# KEY = service name, VALUE = list of features

SERVICE_FEATURES = {
    "Web Design": [
        {
            "icon": "🎨",
            "title": "Custom UI/UX Design",
            "description": "Beautiful, unique designs that represent your brand perfectly. No templates!"
        },
        {
            "icon": "📱",
            "title": "Mobile-First Development",
            "description": "Your website looks perfect on phones, tablets, and desktops automatically."
        },
        {
            "icon": "⚡",
            "title": "Speed Optimization",
            "description": "Lightning-fast loading times. Google loves fast websites!"
        },
        {
            "icon": "🔒",
            "title": "SSL & Security",
            "description": "Your website is secure with HTTPS encryption included free."
        },
        {
            "icon": "🔍",
            "title": "SEO Ready",
            "description": "Built with proper structure so Google can find and rank your site."
        },
        {
            "icon": "🛠️",
            "title": "Easy Management",
            "description": "Update your website yourself with our simple admin panel."
        }
    ],
    "SEO Services": [
        {
            "icon": "📊",
            "title": "Keyword Research",
            "description": "Find exactly what your customers search for and target those words."
        },
        {
            "icon": "📝",
            "title": "Content Strategy",
            "description": "Create content that ranks on page 1 of Google consistently."
        },
        {
            "icon": "🔗",
            "title": "Link Building",
            "description": "Get high-quality backlinks from trusted websites in your industry."
        },
        {
            "icon": "🏷️",
            "title": "On-Page SEO",
            "description": "Optimize every page element - titles, tags, images, and structure."
        },
        {
            "icon": "📈",
            "title": "Monthly Reporting",
            "description": "Clear reports showing exactly how your rankings are improving."
        },
        {
            "icon": "🎯",
            "title": "Local SEO",
            "description": "Dominate Google Maps and local search results in your city."
        }
    ],
    "Digital Marketing": [
        {
            "icon": "📱",
            "title": "Social Media Marketing",
            "description": "Build your brand on Instagram, Facebook, LinkedIn and more."
        },
        {
            "icon": "💰",
            "title": "Google Ads (PPC)",
            "description": "Get immediate traffic with targeted Google ad campaigns."
        },
        {
            "icon": "📧",
            "title": "Email Marketing",
            "description": "Nurture leads and convert customers with smart email sequences."
        },
        {
            "icon": "📊",
            "title": "Analytics & Tracking",
            "description": "Know exactly what's working with detailed performance data."
        },
        {
            "icon": "🎬",
            "title": "Video Marketing",
            "description": "Engage your audience with professional video content strategy."
        },
        {
            "icon": "🤝",
            "title": "Influencer Marketing",
            "description": "Partner with the right influencers to reach your target audience."
        }
    ],
    "App Development": [
        {
            "icon": "📱",
            "title": "iOS & Android Apps",
            "description": "Native apps for both platforms or one cross-platform solution."
        },
        {
            "icon": "⚡",
            "title": "React Native Development",
            "description": "Build once, deploy everywhere. Save time and money."
        },
        {
            "icon": "🔧",
            "title": "Backend Development",
            "description": "Powerful APIs and databases that scale with your business."
        },
        {
            "icon": "☁️",
            "title": "Cloud Deployment",
            "description": "Your app hosted on AWS/Google Cloud for 99.9% uptime."
        },
        {
            "icon": "🔄",
            "title": "App Maintenance",
            "description": "Regular updates, bug fixes, and new features post-launch."
        },
        {
            "icon": "🛡️",
            "title": "Security & Testing",
            "description": "Thorough testing and security audits before launch."
        }
    ]
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
# Functions are like recipes - they do one specific job

def format_price(value):
    """
    Formats a number like 15000 into "15,000"
    
    Example:
        format_price(15000) → "15,000"
        format_price(1000000) → "10,00,000"  (Indian format)
    
    The 'value' parameter is the number coming in
    """
    # Convert to integer first (remove decimals)
    value = int(value)
    
    # Indian number format: 1,00,000 (not 100,000)
    # First, handle the last 3 digits
    if value < 1000:
        return str(value)
    
    # Get last 3 digits
    last_three = str(value % 1000).zfill(3)
    
    # Get remaining digits
    remaining = value // 1000
    
    # Group remaining in pairs of 2
    parts = []
    while remaining > 0:
        parts.append(str(remaining % 100).zfill(2) if remaining >= 100 else str(remaining % 100))
        remaining //= 100
    
    # Build the final string
    parts.reverse()
    result = ",".join(parts) + "," + last_three
    
    # Remove leading zeros in first group
    result = result.lstrip("0").lstrip(",")
    if result.startswith(","):
        result = result[1:]
    
    return result


def create_slug(service, city):
    """
    Creates a URL-friendly filename from service and city
    
    Example:
        create_slug("Web Design", "Chennai") → "web-design-chennai"
        create_slug("SEO Services", "New Delhi") → "seo-services-new-delhi"
    
    Why? File names can't have spaces or uppercase in URLs
    """
    # Combine service and city with a space
    combined = f"{service} {city}"
    
    # Convert to lowercase
    combined = combined.lower()
    
    # Replace spaces with hyphens
    combined = combined.replace(" ", "-")
    
    # Remove any special characters (only allow letters, numbers, hyphens)
    combined = re.sub(r'[^a-z0-9-]', '', combined)
    
    return combined


def get_related_cities(current_city, all_cities, count=5):
    """
    Gets a list of other cities (not the current one)
    Used to create internal links on each page
    
    Example:
        If current city is Chennai, returns [Mumbai, Delhi, Bangalore, ...]
    """
    # Filter out the current city
    related = [city for city in all_cities if city != current_city]
    
    # Return only 'count' number of cities
    return related[:count]


def format_population(population):
    """
    Formats population number nicely
    Example: 7088000 → "70.9 Lakh"
    """
    if population >= 10000000:  # 1 crore
        return f"{population/10000000:.1f} Cr"
    elif population >= 100000:  # 1 lakh
        return f"{population/100000:.1f} Lakh"
    else:
        return f"{population:,}"


# ============================================================
# MAIN PAGE GENERATOR CLASS
# ============================================================
# A CLASS is like a blueprint for a machine
# We define what the machine can DO (methods/functions)
# Then we CREATE the machine and use it

class ProgrammaticSEOGenerator:
    """
    This is our page factory machine!
    
    Steps it follows:
    1. Load data from CSV
    2. Set up the template engine
    3. For each row in CSV, generate one HTML page
    4. Create a sitemap.xml
    5. Print a summary
    """
    
    def __init__(self):
        """
        __init__ is called when we first CREATE this machine
        Think of it as "turning on the machine"
        """
        print("🚀 Starting Programmatic SEO Generator...")
        print("=" * 60)
        
        # Store configuration
        self.config = CONFIG
        
        # These will be filled in later
        self.data = None           # Will hold our CSV data
        self.template_env = None   # Will hold Jinja2 engine
        self.generated_pages = []  # Will track all pages we make
        
        # Make sure output folder exists
        # exist_ok=True means: "don't crash if folder already exists"
        os.makedirs(self.config["output_dir"], exist_ok=True)
        
        print(f"✅ Output folder ready: {self.config['output_dir']}")
    
    
    def load_data(self):
        """
        Loads the CSV file into memory
        pd.read_csv() reads the file like Excel opens a spreadsheet
        """
        print("\n📊 Loading keyword data...")
        
        # Read the CSV file
        # pd is pandas - our spreadsheet tool
        self.data = pd.read_csv(self.config["data_file"])
        
        # Print info about what we loaded
        print(f"✅ Loaded {len(self.data)} rows of data")
        print(f"   Columns found: {list(self.data.columns)}")
        print(f"   Services: {self.data['service'].unique()}")
        print(f"   Cities: {list(self.data['city'].unique())}")
        
        return self  # Return self so we can "chain" methods
    
    
    def setup_template_engine(self):
        """
        Sets up Jinja2 - our template filling system
        
        Think of Jinja2 like:
        - You have a letter template
        - Jinja2 fills in the [NAME] and [CITY] parts
        """
        print("\n🎨 Setting up template engine...")
        
        # Create Jinja2 environment
        # FileSystemLoader tells Jinja2 WHERE to find template files
        self.template_env = Environment(
            loader=FileSystemLoader(self.config["templates_dir"])
        )
        
        # Add our custom format_price function to Jinja2
        # This lets us use {{ price | format_price }} in templates
        # 'filters' are like plugins for Jinja2
        self.template_env.filters['format_price'] = format_price
        
        print(f"✅ Template engine ready")
        print(f"   Templates folder: {self.config['templates_dir']}")
        
        return self
    
    
    def generate_single_page(self, row, all_cities):
        """
        Generates ONE HTML page for one row of data
        
        'row' is one row from the CSV - like one line in Excel
        'all_cities' is the full list of cities (for related links)
        
        This function:
        1. Prepares all the data variables
        2. Loads the template
        3. Fills in all the {{ variables }}
        4. Saves the file
        """
        
        # Extract values from the CSV row
        # row['service'] gets the value in the 'service' column
        service = row['service']
        city = row['city']
        state = row['state']
        population = row['population']
        avg_price = row['avg_price']
        competition_level = row['competition_level']
        
        # Create the URL slug (filename)
        # Example: "web-design-chennai"
        slug = create_slug(service, city)
        
        # Create the full filename
        # Example: "output/web-design-chennai.html"
        filename = f"{slug}.html"
        filepath = os.path.join(self.config["output_dir"], filename)
        
        # Get features for this specific service
        # .get() means: "get this key, or use empty list if not found"
        features = SERVICE_FEATURES.get(service, [])
        
        # Get related cities for internal linking
        related = get_related_cities(city, all_cities)
        
        # Format population for display
        city_pop_formatted = format_population(population)
        
        # Get today's date formatted nicely
        today = datetime.now().strftime("%B %d, %Y")
        # strftime formats the date: "%B" = month name, "%d" = day, "%Y" = year
        # Result example: "January 15, 2025"
        
        # ---- PREPARE ALL TEMPLATE VARIABLES ----
        # This dictionary is like a "data package" we send to the template
        # Every {{ variable }} in the HTML template gets its value from here
        template_data = {
            "service": service,
            "city": city,
            "state": state,
            "population": population,
            "avg_price": avg_price,
            "competition_level": competition_level,
            "features": features,
            "related_cities": related,
            "city_population": city_pop_formatted,
            "generated_date": today,
            "page_url": f"{self.config['base_url']}/{filename}",
            "site_name": self.config["site_name"]
        }
        
        # ---- LOAD AND FILL THE TEMPLATE ----
        # Get the template file
        template = self.template_env.get_template(self.config["template_file"])
        
        # Fill in all variables! This is where magic happens!
        # template.render() takes our dictionary and fills {{ }} placeholders
        html_content = template.render(**template_data)
        # The ** means "unpack dictionary as keyword arguments"
        # So template_data = {"service": "Web Design"} becomes service="Web Design"
        
        # ---- SAVE THE FILE ----
        # 'w' means "write mode" (create new or overwrite)
        # encoding='utf-8' handles special characters like Indian names
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Record this page in our tracking list
        page_info = {
            "service": service,
            "city": city,
            "slug": slug,
            "filename": filename,
            "url": f"{self.config['base_url']}/{filename}"
        }
        self.generated_pages.append(page_info)
        
        print(f"   ✅ Generated: {filename}")
        
        return page_info
    
    
    def generate_all_pages(self):
        """
        Goes through EVERY row in the CSV and generates a page
        
        This is a LOOP - it repeats generate_single_page() for each row
        """
        print(f"\n🏭 Generating {len(self.data)} pages...")
        print("-" * 40)
        
        # Get the list of all unique cities
        # We need this to create "related cities" links on each page
        all_cities = list(self.data['city'].unique())
        
        # Loop through each row in the CSV
        # iterrows() gives us each row one at a time
        # _, row means: ignore the index (_), give me the row data
        for _, row in self.data.iterrows():
            self.generate_single_page(row, all_cities)
        
        print(f"\n✅ All {len(self.generated_pages)} pages generated!")
        
        return self
    
    
    def generate_sitemap(self):
        """
        Creates sitemap.xml - a map of all your pages for Google
        
        Why? Google's bots read sitemap.xml to discover all your pages
        Without it, Google might miss some pages!
        
        Sitemap format looks like:
        <url>
            <loc>http://yoursite.com/web-design-chennai.html</loc>
            <lastmod>2025-01-15</lastmod>
            <priority>0.8</priority>
        </url>
        """
        print("\n🗺️ Creating sitemap.xml...")
        
        # Today's date in the format Google likes
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Start building the XML string
        # XML is like HTML but for data
        sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
        
        # Add each page to the sitemap
        for page in self.generated_pages:
            sitemap_content += f'''    <url>
        <loc>{page["url"]}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
'''
        
        # Close the XML
        sitemap_content += '</urlset>'
        
        # Save sitemap to output folder
        sitemap_path = os.path.join(self.config["output_dir"], "sitemap.xml")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        print(f"✅ Sitemap created: {sitemap_path}")
        print(f"   Contains {len(self.generated_pages)} URLs")
        
        return self
    
    
    def generate_index_page(self):
        """
        Creates an index.html - a homepage listing ALL generated pages
        This makes it easy to navigate and see all pages
        """
        print("\n📋 Creating index page...")
        
        # Group pages by service
        services = {}
        for page in self.generated_pages:
            service = page["service"]
            if service not in services:
                services[service] = []  # Create empty list
            services[service].append(page)
        
        # Build the HTML for the index
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Programmatic SEO Pages - All Generated Pages</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a0a; color: #fff; padding: 40px; }}
        h1 {{ color: #667eea; margin-bottom: 10px; }}
        .subtitle {{ color: #888; margin-bottom: 40px; }}
        h2 {{ color: #667eea; margin-top: 30px; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
        .card {{ background: #1a1a2e; border-radius: 10px; padding: 15px; border: 1px solid #333; }}
        .card a {{ color: #667eea; text-decoration: none; font-weight: 600; }}
        .card a:hover {{ text-decoration: underline; }}
        .card small {{ color: #888; display: block; margin-top: 5px; }}
        .stats {{ background: #1a1a2e; border-radius: 10px; padding: 20px; margin-bottom: 30px; display: flex; gap: 40px; }}
        .stat {{ text-align: center; }}
        .stat-n {{ font-size: 2em; font-weight: 700; color: #667eea; }}
    </style>
</head>
<body>
    <h1>🏭 Programmatic SEO - All Generated Pages</h1>
    <p class="subtitle">Module 2: {len(self.generated_pages)} pages auto-generated from keyword data</p>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-n">{len(self.generated_pages)}</div>
            <div>Total Pages</div>
        </div>
        <div class="stat">
            <div class="stat-n">{len(services)}</div>
            <div>Services</div>
        </div>
        <div class="stat">
            <div class="stat-n">{len(self.data['city'].unique())}</div>
            <div>Cities</div>
        </div>
    </div>
"""
        
        # Add each service group
        for service, pages in services.items():
            html += f"<h2>🔷 {service} ({len(pages)} pages)</h2>\n<div class='grid'>\n"
            for page in pages:
                html += f"""    <div class="card">
        <a href="{page['filename']}" target="_blank">{page['service']} in {page['city']}</a>
        <small>📄 {page['filename']}</small>
    </div>
"""
            html += "</div>\n"
        
        html += "</body></html>"
        
        # Save index
        index_path = os.path.join(self.config["output_dir"], "index.html")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Index page created: {index_path}")
        
        return self
    
    
    def print_summary(self):
        """
        Prints a nice summary of everything that was generated
        """
        print("\n" + "=" * 60)
        print("🎉 GENERATION COMPLETE!")
        print("=" * 60)
        print(f"📁 Output folder: {self.config['output_dir']}/")
        print(f"📄 Total pages generated: {len(self.generated_pages)}")
        print(f"🗺️ Sitemap: {self.config['output_dir']}/sitemap.xml")
        print(f"🏠 Index: {self.config['output_dir']}/index.html")
        print("\n📋 Pages by service:")
        
        # Count pages per service
        service_counts = {}
        for page in self.generated_pages:
            s = page["service"]
            service_counts[s] = service_counts.get(s, 0) + 1
        
        for service, count in service_counts.items():
            print(f"   {service}: {count} pages")
        
        print("\n🚀 Next step: Run Flask server to view pages!")
        print("   Command: python serve.py")
        print("=" * 60)


# ============================================================
# RUN THE GENERATOR
# ============================================================
# This is the "start button" of our program
# if __name__ == "__main__" means:
# "Only run this if we execute THIS file directly"
# (not if another file imports this file)

if __name__ == "__main__":
    
    # Create our generator machine
    generator = ProgrammaticSEOGenerator()
    
    # Run all steps in order
    # Each method returns 'self' so we can CHAIN them
    # This is called "method chaining" - very professional Python style
    (generator
        .load_data()           # Step 1: Read CSV
        .setup_template_engine()  # Step 2: Set up Jinja2
        .generate_all_pages()  # Step 3: Make all pages
        .generate_sitemap()    # Step 4: Create sitemap
        .generate_index_page() # Step 5: Create index
        .print_summary()       # Step 6: Show results
    )