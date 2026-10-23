import json
import sqlite3
import random
import os
from models import init_db, get_db, DB_PATH

STUDENTS = [
    {
        "roll_no": "2024CS001",
        "name": "Amulya Srivastava",
        "handle": "amulyap",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&auto=format&fit=crop&q=80",
        "department": "Computer Science",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.96,
        "dorm": "Kirkland Hall #204",
        "hometown": "Bengaluru, IN",
        "relationship_status": "In a relationship with coding",
        "bio": "Building autonomous systems, AI agents & campus tools. Night coffee addict. Founder of the unofficial college network. ☕💻",
        "quote": "Move fast and compile things without errors.",
        "canteen_fav": "Masala Dosa + Filter Coffee",
        "karma": 980,
        "projects_count": 14,
        "badges": ["Dean's List", "Hackathon Winner", "Code Club Lead", "Network Founder"],
        "socials": {"github": "github.com/amulya", "linkedin": "linkedin.com/in/amulya", "instagram": "@amulya.codes"}
    },
    {
        "roll_no": "2023CS042",
        "name": "Mark Zuckerberg",
        "handle": "zuck",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&auto=format&fit=crop&q=80",
        "department": "Computer Science",
        "batch_year": 2026,
        "batch_title": "Junior",
        "gpa": 3.92,
        "dorm": "Kirkland House H-33",
        "hometown": "Dobbs Ferry, NY",
        "relationship_status": "In an open relationship",
        "bio": "An online directory connecting colleges. PHP, C++, algorithms. Wire updates, campus graphs. Let's connect everyone. 🌐",
        "quote": "You don't get to 500 million friends without making a few enemies.",
        "canteen_fav": "Hot Pockets & Red Bull",
        "karma": 965,
        "projects_count": 18,
        "badges": ["Campus Legend", "SysAdmin", "Algo God"],
        "socials": {"github": "github.com/zuck", "linkedin": "linkedin.com/in/zuck", "instagram": "@zuck"}
    },
    {
        "roll_no": "2023DS019",
        "name": "Sarah Jenkins",
        "handle": "sarahj_art",
        "avatar": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=1200&auto=format&fit=crop&q=80",
        "department": "Design & Arts",
        "batch_year": 2025,
        "batch_title": "Senior",
        "gpa": 3.88,
        "dorm": "Eliot House #12",
        "hometown": "San Francisco, CA",
        "relationship_status": "Taken by typography",
        "bio": "Visual designer, poster artist for campus fests, and Figma wizard. Coffee in one hand, sketchbook in the other. 🎨✨",
        "quote": "Good design is invisible, great design is unforgettable.",
        "canteen_fav": "Iced Oat Latte + Blueberry Muffin",
        "karma": 940,
        "projects_count": 21,
        "badges": ["Design Lead", "Fest Creative Head", "Merit Scholar"],
        "socials": {"github": "github.com/sarahj", "linkedin": "linkedin.com/in/sarahj", "instagram": "@sarah.design"}
    },
    {
        "roll_no": "2024ME088",
        "name": "Rohan Sharma",
        "handle": "rohan_torque",
        "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1486006920555-c77dce18193b?w=1200&auto=format&fit=crop&q=80",
        "department": "Mechanical Engineering",
        "batch_year": 2028,
        "batch_title": "Sophomore",
        "gpa": 3.84,
        "dorm": "Winthrop Tower #3B",
        "hometown": "Pune, IN",
        "relationship_status": "Single",
        "bio": "Formula Student racecar driver & suspension specialist. 3D printing titanium brackets at 3 AM in the workshop. 🏎️🔧",
        "quote": "If in doubt, add more downforce.",
        "canteen_fav": "Maggi double egg + Cutting Chai",
        "karma": 895,
        "projects_count": 9,
        "badges": ["Formula Student", "Robotics Club", "CAD Wizard"],
        "socials": {"github": "github.com/rohans", "linkedin": "linkedin.com/in/rohans", "instagram": "@rohan_racing"}
    },
    {
        "roll_no": "2024EE015",
        "name": "Maya Lin",
        "handle": "mayacircuits",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&auto=format&fit=crop&q=80",
        "department": "Electrical Engineering",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.95,
        "dorm": "Adams House #402",
        "hometown": "Austin, TX",
        "relationship_status": "Single",
        "bio": "FPGA nerd, custom drone builder, and PCB soldering fanatic. If it emits photons or RF signals, I'm analyzing it. ⚡📡",
        "quote": "Hardware is where the magic becomes physics.",
        "canteen_fav": "Double Espresso + Bagel",
        "karma": 930,
        "projects_count": 12,
        "badges": ["Hardware Guru", "Dean's List", "Maker Lab Lead"],
        "socials": {"github": "github.com/mayalin", "linkedin": "linkedin.com/in/mayalin", "instagram": "@maya.circuits"}
    },
    {
        "roll_no": "2023BA007",
        "name": "Chloe Bennett",
        "handle": "chloe_b",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&auto=format&fit=crop&q=80",
        "department": "Business Administration",
        "batch_year": 2025,
        "batch_title": "Senior",
        "gpa": 3.89,
        "dorm": "Lowell House #21",
        "hometown": "Chicago, IL",
        "relationship_status": "It's complicated with Wall St",
        "bio": "Consulting club president, early-stage venture scout, and campus coffee critic. Let's talk pitch decks & unit economics. 📈💼",
        "quote": "Capital follows conviction and execution.",
        "canteen_fav": "Matcha Latte + Avocado Toast",
        "karma": 915,
        "projects_count": 16,
        "badges": ["Consulting Lead", "Venture Fellow", "Valedictorian Nominee"],
        "socials": {"github": "github.com/chloeb", "linkedin": "linkedin.com/in/chloeb", "instagram": "@chloe_bennett"}
    },
    {
        "roll_no": "2024BT032",
        "name": "David O'Connor",
        "handle": "david_dna",
        "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=1200&auto=format&fit=crop&q=80",
        "department": "Biotechnology",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.91,
        "dorm": "Currier Quad #108",
        "hometown": "Boston, MA",
        "relationship_status": "Single",
        "bio": "CRISPR gene editing research & computational proteomics. Also captain of the campus badminton team. 🧬🏸",
        "quote": "Life is just chemistry with an ambition.",
        "canteen_fav": "Protein Shake + Peanut Butter Toast",
        "karma": 885,
        "projects_count": 11,
        "badges": ["Bio Lab Lead", "Sports Captain", "Dean's List"],
        "socials": {"github": "github.com/davido", "linkedin": "linkedin.com/in/davido", "instagram": "@david_oc"}
    },
    {
        "roll_no": "2024CS099",
        "name": "Aisha Khan",
        "handle": "aisha_rust",
        "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1200&auto=format&fit=crop&q=80",
        "department": "Computer Science",
        "batch_year": 2028,
        "batch_title": "Sophomore",
        "gpa": 3.86,
        "dorm": "Mather Tower #501",
        "hometown": "Hyderabad, IN",
        "relationship_status": "Single",
        "bio": "Competitive programmer & Rust contributor. Distributed databases and zero-copy parsers. 🦀💻",
        "quote": "Memory safety is the highest form of self-care.",
        "canteen_fav": "Chai + Samosa Pav",
        "karma": 875,
        "projects_count": 10,
        "badges": ["Competitive Coder", "Rustacean", "Freshers Mentor"],
        "socials": {"github": "github.com/aishak", "linkedin": "linkedin.com/in/aishak", "instagram": "@aisha.dev"}
    },
    {
        "roll_no": "2023ME022",
        "name": "Liam Vance",
        "handle": "liam_aero",
        "avatar": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1517976487502-d280b18f020a?w=1200&auto=format&fit=crop&q=80",
        "department": "Mechanical Engineering",
        "batch_year": 2025,
        "batch_title": "Senior",
        "gpa": 3.79,
        "dorm": "Dunster House #14",
        "hometown": "Denver, CO",
        "relationship_status": "In a relationship",
        "bio": "Rocket propulsion, supersonic nozzles, and fluid dynamics simulations. Launching things into the stratosphere. 🚀",
        "quote": "Velocity is relative, thrust is absolute.",
        "canteen_fav": "Black Coffee + Grilled Cheese",
        "karma": 860,
        "projects_count": 15,
        "badges": ["Rocketry Club", "Aero Star", "Workshop Veteran"],
        "socials": {"github": "github.com/liamv", "linkedin": "linkedin.com/in/liamv", "instagram": "@liam.vance"}
    },
    {
        "roll_no": "2023EE002",
        "name": "Elena Rostova",
        "handle": "elena_quantum",
        "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=1200&auto=format&fit=crop&q=80",
        "department": "Electrical Engineering",
        "batch_year": 2025,
        "batch_title": "Senior",
        "gpa": 3.98,
        "dorm": "Cabot Hall #312",
        "hometown": "Toronto, CA",
        "relationship_status": "Single",
        "bio": "Quantum photonics, superconducting circuits & RF electronics. Classical pianist performing at campus concert hall. 🎹🔬",
        "quote": "Superposition is just being intellectually humble.",
        "canteen_fav": "Earl Grey Tea + Lemon Tart",
        "karma": 970,
        "projects_count": 19,
        "badges": ["Dean's List", "IEEE Chair", "Quantum Fellow"],
        "socials": {"github": "github.com/elenar", "linkedin": "linkedin.com/in/elenar", "instagram": "@elena.quantum"}
    },
    {
        "roll_no": "2024BA045",
        "name": "Dev Mehta",
        "handle": "dev_fin",
        "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&auto=format&fit=crop&q=80",
        "department": "Business Administration",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.75,
        "dorm": "Quincy House #309",
        "hometown": "Mumbai, IN",
        "relationship_status": "Bullish on coffee",
        "bio": "Algorithmic market making, DeFi protocols, and late night campus poker. Midnight pizza deliveries sponsor. 🍕📊",
        "quote": "Risk is the tariff on exponential returns.",
        "canteen_fav": "Paneer Tikka Roll + Thums Up",
        "karma": 840,
        "projects_count": 8,
        "badges": ["FinTech Lead", "Trading Society", "Hostel Rep"],
        "socials": {"github": "github.com/devm", "linkedin": "linkedin.com/in/devm", "instagram": "@devmehta.fin"}
    },
    {
        "roll_no": "2024DS055",
        "name": "Priya Nambiar",
        "handle": "priya_lens",
        "avatar": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1200&auto=format&fit=crop&q=80",
        "department": "Design & Arts",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.84,
        "dorm": "Leverett Towers #201",
        "hometown": "Kochi, IN",
        "relationship_status": "In a relationship",
        "bio": "Editor-in-Chief of Campus Chronicle. 35mm film photographer capturing the unofficial soul of college life. 📸🎞️",
        "quote": "Every darkroom print tells a secret.",
        "canteen_fav": "Cold Coffee + Chicken Puff",
        "karma": 865,
        "projects_count": 13,
        "badges": ["Chronicle Editor", "Photo Club Lead", "Storyteller"],
        "socials": {"github": "github.com/priyan", "linkedin": "linkedin.com/in/priyan", "instagram": "@priya.captures"}
    },
    {
        "roll_no": "2023BT011",
        "name": "Marcus Bell",
        "handle": "marcus_eco",
        "avatar": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80",
        "department": "Biotechnology",
        "batch_year": 2025,
        "batch_title": "Senior",
        "gpa": 3.82,
        "dorm": "Pforzheimer House #45",
        "hometown": "Atlanta, GA",
        "relationship_status": "Single",
        "bio": "Synthetic biology, vertical farming & hydroponics systems. Turning dorm balconies into oxygen farms. 🌿🌱",
        "quote": "Nature already wrote the code, we are just compiling it.",
        "canteen_fav": "Green Smoothie + Falafel Wrap",
        "karma": 850,
        "projects_count": 14,
        "badges": ["Eco Council", "Lab Scholar", "Green Campus Lead"],
        "socials": {"github": "github.com/marcusb", "linkedin": "linkedin.com/in/marcusb", "instagram": "@marcus_green"}
    },
    {
        "roll_no": "2025CS105",
        "name": "Samira Al-Mansoor",
        "handle": "samira_codes",
        "avatar": "https://images.unsplash.com/photo-1534751516642-a171edd25218?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=1200&auto=format&fit=crop&q=80",
        "department": "Computer Science",
        "batch_year": 2028,
        "batch_title": "Freshman",
        "gpa": 3.98,
        "dorm": "Weld Hall #12",
        "hometown": "Dubai, UAE",
        "relationship_status": "Single",
        "bio": "Freshman hacking on web dev, competitive math, and finding the quietest spots in the library. 🚀📚",
        "quote": "Hello world, I'm just getting started.",
        "canteen_fav": "Caramel Macchiato + Croissant",
        "karma": 810,
        "projects_count": 6,
        "badges": ["Top Freshman", "Hackathon Rising Star", "Math Olympiad"],
        "socials": {"github": "github.com/samira", "linkedin": "linkedin.com/in/samira", "instagram": "@samira.codes"}
    },
    {
        "roll_no": "2024ME044",
        "name": "Tyler Brooks",
        "handle": "tyler_wrench",
        "avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?w=1200&auto=format&fit=crop&q=80",
        "department": "Mechanical Engineering",
        "batch_year": 2027,
        "batch_title": "Junior",
        "gpa": 3.73,
        "dorm": "Matthews Hall #08",
        "hometown": "Detroit, MI",
        "relationship_status": "Single",
        "bio": "Off-road buggy suspension engineering, CNC milling, and welding master. Mud on my boots, CAD on my screen. ⚙️🚜",
        "quote": "Steel bends, determination doesn't.",
        "canteen_fav": "Cheeseburger + Loaded Fries",
        "karma": 825,
        "projects_count": 10,
        "badges": ["Baja SAE", "Workshop Manager"],
        "socials": {"github": "github.com/tylerb", "linkedin": "linkedin.com/in/tylerb", "instagram": "@tyler_wrench"}
    },
    {
        "roll_no": "2024DS089",
        "name": "Jessica Taylor",
        "handle": "jess_render",
        "avatar": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
        "banner": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200&auto=format&fit=crop&q=80",
        "department": "Design & Arts",
        "batch_year": 2028,
        "batch_title": "Sophomore",
        "gpa": 3.79,
        "dorm": "Straus Hall #23",
        "hometown": "London, UK",
        "relationship_status": "Single",
        "bio": "3D Blender artist, procedural textures, motion design for campus EDM nights. Exploring generative art! 🎞️✨",
        "quote": "Render times build character.",
        "canteen_fav": "Bubble Tea + Cinnamon Roll",
        "karma": 815,
        "projects_count": 8,
        "badges": ["Animation Club", "Creative Fellow"],
        "socials": {"github": "github.com/jesstaylor", "linkedin": "linkedin.com/in/jesstaylor", "instagram": "@jess_render"}
    }
]

POSTS = [
    {
        "student_handle": "amulyap",
        "content": "Just deployed the first version of the Unofficial Campus Network! 🚀 Welcome to the new college directory. Check your course leaderboards, find your dorm mates, and vote on the midnight canteen poll! Let me know what features we should add next on the wire.",
        "image_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=900&auto=format&fit=crop&q=80",
        "tags": "#CampusNetwork #TheFacebook #CollegeVibes #LaunchDay"
    },
    {
        "student_handle": "zuck",
        "content": "Kirkland House H-33 is officially running the server cluster. If the network hiccups for 10 seconds, someone unplugged the surge protector to brew ramen again. The directory is syncing across all 6 departments.",
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=900&auto=format&fit=crop&q=80",
        "tags": "#ServerRoom #KirklandHacks #Coding"
    },
    {
        "student_handle": "sarahj_art",
        "content": "Sneak peek of the official posters for TechnoPulse 2026! 🎨 Spent 3 days tweaking the typography and color gradients in the design studio. Drop your thoughts below — should we do holographic print runs for the campus fest?",
        "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&auto=format&fit=crop&q=80",
        "tags": "#CampusFest #TechnoPulse #Design"
    },
    {
        "student_handle": "rohan_torque",
        "content": "Formula Student chassis just passed static load testing at 2.4G! Huge shoutout to the mechanical workshop crew for pulling an all-nighter. Track testing at the stadium parking lot this Saturday at 10 AM. Come watch the beast run! 🏎️💨",
        "image_url": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=900&auto=format&fit=crop&q=80",
        "tags": "#FormulaStudent #Racecar #Mechanical"
    },
    {
        "student_handle": "mayacircuits",
        "content": "Custom 4-layer PCB for our autonomous swarm drones arrived from fabrication today! Soldering SMD microcontrollers under the microscope. Who's staying late in the EE lab tonight? I brought donuts 🍩⚡",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&auto=format&fit=crop&q=80",
        "tags": "#HardwareHacking #FPGA #EE"
    },
    {
        "student_handle": "chloe_b",
        "content": "The Harvard Business Case Competition finals are locked in! Our team took 1st place in the campus qualifier analyzing green energy microgrids. Proud of the squad! 🏆 Remember: a good model is great, but a defensible moat is everything.",
        "image_url": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=900&auto=format&fit=crop&q=80",
        "tags": "#Consulting #CaseComp #Winner"
    },
    {
        "student_handle": "david_dna",
        "content": "Fluorescence microscopy from today's biotechnology lab session. Watching GFP-tagged proteins localize inside eukaryotic cells never gets old. Biology is literally microscopic art. 🧬🔬",
        "image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=900&auto=format&fit=crop&q=80",
        "tags": "#Biotech #LabLife #Microscopy"
    },
    {
        "student_handle": "priya_lens",
        "content": "Golden hour on the quad between lectures. Captured on vintage 35mm film. College isn't just about exams and GPAs; it's about these quiet afternoons on the lawn with friends. 🎞️☀️",
        "image_url": "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=900&auto=format&fit=crop&q=80",
        "tags": "#CampusLife #Photography #Quad"
    }
]

POLLS = [
    {
        "question": "Which midnight campus food spot is undisputed king?",
        "category": "Food & Hangouts",
        "creator_handle": "amulyap",
        "options": [
            "North Gate Maggi & Chai Stall",
            "Night Canteen Butter Chicken & Rolls",
            "Hostel 4 Grilled Cheese & Sandwiches",
            "Library 24/7 Espresso Bar"
        ],
        "votes_distribution": [42, 38, 19, 12]
    },
    {
        "question": "What is mathematically the most brutal course this semester?",
        "category": "Academics",
        "creator_handle": "zuck",
        "options": [
            "CS 182: Advanced Algorithms & NP-Completeness",
            "EE 201: Signals, Systems & Fourier Nightmare",
            "ME 302: Fluid Dynamics & Navier-Stokes",
            "BT 210: Molecular Biophysics & Thermodynamics"
        ],
        "votes_distribution": [58, 35, 27, 14]
    },
    {
        "question": "What should be the headlining theme for College Spring Fest?",
        "category": "Fest Buzz",
        "creator_handle": "sarahj_art",
        "options": [
            "Cyberpunk 2099: Neon Horizon",
            "Retro Y2K: Return of 2004",
            "Arcane Odyssey: Medieval Fantasy",
            "Interstellar Cosmos: Space Rave"
        ],
        "votes_distribution": [34, 51, 16, 29]
    },
    {
        "question": "Where is the best spot to pull an uninterrupted all-nighter?",
        "category": "Campus Life",
        "creator_handle": "mayacircuits",
        "options": [
            "Main Library 4th Floor Silent Stacks",
            "Computer Science Basement Lab 007",
            "Student Lounge Couches near Canteen",
            "Dorm Common Room with Spotify on speakers"
        ],
        "votes_distribution": [47, 39, 15, 22]
    }
]

EVENTS = [
    {
        "title": "TechnoPulse 2026: 36-Hour National Hackathon",
        "description": "The biggest annual hackathon on campus! $10,000 in prizes, free food, energy drinks, and top tech sponsors. Form teams of 4 or find a team at the opening mixer.",
        "category": "Hackathon",
        "date_str": "Saturday, Sept 14 • 09:00 AM",
        "location": "Student Activity Center Auditorium",
        "image_url": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&auto=format&fit=crop&q=80",
        "host_handle": "amulyap"
    },
    {
        "title": "Formula Student: Racecar Unveiling & Speed Run",
        "description": "Witness our student-engineered custom racecar hit 0-100 km/h on the campus airstrip/stadium track! Meet the drivers and engineering crew.",
        "category": "Sports",
        "date_str": "Friday, Sept 20 • 04:30 PM",
        "location": "Main Stadium Parking Lot",
        "image_url": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=800&auto=format&fit=crop&q=80",
        "host_handle": "rohan_torque"
    },
    {
        "title": "Quad Acoustic Sunset & Indie Music Jam",
        "description": "Bring your guitars, drums, or just a blanket. Unofficial open jam session under the big oak trees on the Central Quad. Free cider & cookies.",
        "category": "Cultural Fest",
        "date_str": "Sunday, Sept 16 • 06:00 PM",
        "location": "Central Quad Green",
        "image_url": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800&auto=format&fit=crop&q=80",
        "host_handle": "priya_lens"
    },
    {
        "title": "Venture & Startup Pitch Night: Angel Showcase",
        "description": "7 student startups pitch to top alumni angels and venture capitalists. Networking mixer with mocktails and pizza after the demo pitches.",
        "category": "Symposium",
        "date_str": "Wednesday, Sept 25 • 07:00 PM",
        "location": "Lowell Hall Founders Lounge",
        "image_url": "https://images.unsplash.com/photo-1475721027785-f74eccf877e2?w=800&auto=format&fit=crop&q=80",
        "host_handle": "chloe_b"
    },
    {
        "title": "End-Semester Afterparty: Neon Quad Rave",
        "description": "Celebrate the end of midterms with live DJ sets from campus producers, laser shows, glowsticks, and midnight taco trucks!",
        "category": "Party",
        "date_str": "Saturday, Oct 04 • 10:00 PM",
        "location": "Hostel 7 Amphitheater",
        "image_url": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&auto=format&fit=crop&q=80",
        "host_handle": "zuck"
    }
]

CONFESSIONS = [
    {
        "content": "I accidentally took the master key to the CS server room in sophomore year and never returned it. That's why I always have the best Wi-Fi on campus.",
        "category": "Tech Secrets",
        "upvotes": 48
    },
    {
        "content": "To whoever stole my Tupperware with homemade biryani from the 3rd-floor hostel fridge: may your code forever fail with segmentation fault at 11:59 PM.",
        "category": "Dorm Drama",
        "upvotes": 76
    },
    {
        "content": "I studied for CS 182 for 18 straight hours without sleep, walked into the exam hall, and realized the exam is tomorrow. Slept on the library couch for 14 hours.",
        "category": "Exam Banter",
        "upvotes": 112
    },
    {
        "content": "The campus security guard at North Gate actually gives free chai if you know the password ('sudo make chai'). Best kept secret on the quad.",
        "category": "Campus Life",
        "upvotes": 64
    },
    {
        "content": "I told my consulting group partners that I was compiling financial models all night. In reality, I was building a custom suspension buggy in GTA.",
        "category": "Dorm Drama",
        "upvotes": 39
    },
    {
        "content": "Still can't believe the campus network was created in Kirkland House. Moving fast and connecting everyone is the real Ivy tradition.",
        "category": "Campus Life",
        "upvotes": 95
    }
]

def seed_database():
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception:
            pass
    print("Initializing SQLite database...")
    init_db()
    conn = get_db()
    cursor = conn.cursor()

    print("Inserting 16 students...")
    handle_to_id = {}
    for s in STUDENTS:
        cursor.execute('''
            INSERT INTO students (
                roll_no, name, handle, avatar, banner, department, batch_year, batch_title,
                gpa, dorm, hometown, relationship_status, bio, quote, canteen_fav,
                karma, projects_count, badges, socials
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            s["roll_no"], s["name"], s["handle"], s["avatar"], s["banner"],
            s["department"], s["batch_year"], s["batch_title"], s["gpa"],
            s["dorm"], s["hometown"], s["relationship_status"], s["bio"],
            s["quote"], s["canteen_fav"], s["karma"], s["projects_count"],
            json.dumps(s["badges"]), json.dumps(s["socials"])
        ))
        handle_to_id[s["handle"]] = cursor.lastrowid

    print("Creating friendships and follow relationships...")
    student_ids = list(handle_to_id.values())
    amulya_id = handle_to_id["amulyap"]
    zuck_id = handle_to_id["zuck"]
    sarah_id = handle_to_id["sarahj_art"]

    friend_pairs = [
        (amulya_id, zuck_id),
        (amulya_id, sarah_id),
        (amulya_id, handle_to_id["rohan_torque"]),
        (amulya_id, handle_to_id["mayacircuits"]),
        (amulya_id, handle_to_id["chloe_b"]),
        (amulya_id, handle_to_id["aisha_rust"]),
        (zuck_id, sarah_id),
        (zuck_id, handle_to_id["elena_quantum"]),
        (zuck_id, handle_to_id["dev_fin"]),
        (sarah_id, handle_to_id["priya_lens"]),
        (sarah_id, handle_to_id["jess_render"]),
        (handle_to_id["rohan_torque"], handle_to_id["liam_aero"]),
        (handle_to_id["rohan_torque"], handle_to_id["tyler_wrench"]),
        (handle_to_id["mayacircuits"], handle_to_id["elena_quantum"]),
        (handle_to_id["david_dna"], handle_to_id["marcus_eco"]),
        (handle_to_id["chloe_b"], handle_to_id["dev_fin"]),
        (handle_to_id["aisha_rust"], handle_to_id["samira_codes"]),
        (handle_to_id["priya_lens"], handle_to_id["amulyap"])
    ]

    for sid1, sid2 in friend_pairs:
        if sid1 > sid2:
            sid1, sid2 = sid2, sid1
        cursor.execute('''
            INSERT OR IGNORE INTO friendships (student_id_1, student_id_2, status)
            VALUES (?, ?, 'friends')
        ''', (sid1, sid2))

    for sid in student_ids:
        for target in [amulya_id, zuck_id, sarah_id]:
            if sid != target:
                cursor.execute('INSERT OR IGNORE INTO follows (follower_id, following_id) VALUES (?, ?)', (sid, target))
        sample_targets = random.sample([i for i in student_ids if i != sid], k=4)
        for t in sample_targets:
            cursor.execute('INSERT OR IGNORE INTO follows (follower_id, following_id) VALUES (?, ?)', (sid, t))

    print("Inserting campus posts, likes and comments...")
    for p in POSTS:
        author_id = handle_to_id[p["student_handle"]]
        cursor.execute('''
            INSERT INTO posts (student_id, content, image_url, tags)
            VALUES (?, ?, ?, ?)
        ''', (author_id, p["content"], p["image_url"], p["tags"]))
        post_id = cursor.lastrowid

        likers = random.sample(student_ids, k=random.randint(6, 14))
        for l_id in likers:
            cursor.execute('INSERT OR IGNORE INTO post_likes (post_id, student_id) VALUES (?, ?)', (post_id, l_id))

        sample_comments = [
            "This is so legendary! 🔥",
            "Count me in on this!",
            "Bro Kirkland dorm electricity is in danger haha",
            "Clean work as always! See you on the quad.",
            "Can we please add dark mode next? 💻✨"
        ]
        commenters = random.sample(student_ids, k=random.randint(2, 4))
        for idx, c_id in enumerate(commenters):
            cursor.execute('''
                INSERT INTO post_comments (post_id, student_id, content)
                VALUES (?, ?, ?)
            ''', (post_id, c_id, sample_comments[idx % len(sample_comments)]))

    print("Inserting campus polls and votes...")
    for poll_data in POLLS:
        creator_id = handle_to_id[poll_data["creator_handle"]]
        cursor.execute('''
            INSERT INTO polls (question, category, creator_id, options_json)
            VALUES (?, ?, ?, ?)
        ''', (poll_data["question"], poll_data["category"], creator_id, json.dumps(poll_data["options"])))
        poll_id = cursor.lastrowid

        for opt_idx, weight in enumerate(poll_data["votes_distribution"]):
            voters = random.sample(student_ids, k=min(weight // 3, len(student_ids)))
            for voter_id in voters:
                cursor.execute('''
                    INSERT OR IGNORE INTO poll_votes (poll_id, student_id, option_index)
                    VALUES (?, ?, ?)
                ''', (poll_id, voter_id, opt_idx))

    print("Inserting campus events and RSVPs...")
    for ev in EVENTS:
        host_id = handle_to_id[ev["host_handle"]]
        cursor.execute('''
            INSERT INTO events (title, description, category, date_str, location, image_url, host_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ev["title"], ev["description"], ev["category"], ev["date_str"], ev["location"], ev["image_url"], host_id))
        event_id = cursor.lastrowid

        going_students = random.sample(student_ids, k=random.randint(5, 10))
        for gs in going_students:
            cursor.execute('''
                INSERT OR IGNORE INTO event_rsvps (event_id, student_id, status)
                VALUES (?, ?, 'going')
            ''', (event_id, gs))

        interested_students = random.sample([s for s in student_ids if s not in going_students], k=random.randint(2, 5))
        for is_s in interested_students:
            cursor.execute('''
                INSERT OR IGNORE INTO event_rsvps (event_id, student_id, status)
                VALUES (?, ?, 'interested')
            ''', (event_id, is_s))

    print("Inserting classic 'Pokes'...")
    cursor.execute('INSERT OR IGNORE INTO pokes (sender_id, receiver_id, count) VALUES (?, ?, ?)', (zuck_id, amulya_id, 4))
    cursor.execute('INSERT OR IGNORE INTO pokes (sender_id, receiver_id, count) VALUES (?, ?, ?)', (sarah_id, amulya_id, 2))
    cursor.execute('INSERT OR IGNORE INTO pokes (sender_id, receiver_id, count) VALUES (?, ?, ?)', (handle_to_id["rohan_torque"], amulya_id, 1))

    print("Inserting direct messages...")
    starter_messages = [
        (zuck_id, amulya_id, "Hey Amulya! The new directory algorithm is running super smooth. We should connect the campus graph across all departments."),
        (amulya_id, zuck_id, "Thanks Mark! Adding the course leaderboards and live polls tonight. Are you coming to the SAC hackathon on Saturday?"),
        (zuck_id, amulya_id, "Definitely. Bringing a 4-person team from Kirkland House."),
        (sarah_id, amulya_id, "Hey! Dropped the final poster designs for TechnoPulse in the design studio. Let me know if you like the neon gradients!"),
        (amulya_id, sarah_id, "They look unbelievable Sarah! Posted them on the campus wire.")
    ]
    for sender, receiver, content in starter_messages:
        cursor.execute('INSERT INTO messages (sender_id, receiver_id, content, is_read) VALUES (?, ?, ?, 1)', (sender, receiver, content))

    print("Inserting campus confessions...")
    for conf in CONFESSIONS:
        cursor.execute('INSERT INTO confessions (content, category, upvotes) VALUES (?, ?, ?)', (conf["content"], conf["category"], conf["upvotes"]))

    conn.commit()
    conn.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
