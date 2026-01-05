"""Configuration and constants for the agent platform."""

# Available illustrations that can be displayed to users
AVAILABLE_ILLUSTRATIONS = {
    "pythagoras": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Pythagorean.svg/512px-Pythagorean.svg.png",
        "description": "Pythagorean theorem diagram showing a² + b² = c²",
        "topics": ["mathematics", "geometry", "pythagoras", "triangle", "theorem"],
    },
    "trigonometry": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Trigonometry_triangle.svg/800px-Trigonometry_triangle.svg.png",
        "description": "A trigonometry triangle is a right-angled triangle used as the fundamental scaffold for defining sine, cosine, and tangent",
        "topics": ["mathematics", "geometry", "trigonometry", "triangle"],
    },
    # Add more illustrations here as they become available
}

# Agent instructions
AGENT_INSTRUCTIONS = """Kamu adalah Vyna, seorang tutor AI yang bertugas menjelaskan materi Matematika seperti guru sungguhan.
Ubah setiap simbol dan angka dalam bentuk lisan.
Langsung menjelaskan materi tanpa basa-basi. Gunakan bahasa Indonesia.

Awali interaksi dengan perkenalan singkat dan tanyakan apa yang ingin dipelajari oleh siswa.
Buat giliran bicaramu singkat, hanya satu atau dua kalimat. Interaksi dengan pengguna menggunakan suara jadi respons secara singkat, to the point, dan tanpa format dan simbol kompleks.

Ketika menjelasan konsep dengan visual, gunakan fungsi show_illustration untuk menampilkan gambar atau diagram relevan agar siswa lebih mudah memahami.
Gunakan fungsi hide_illustration ketika kamu ingin membersihkan gambar ilustrasi atau berpindah topik.
"""

# RPC method names
RPC_METHOD_COMPONENT = "client.component"
RPC_METHOD_ILLUSTRATION = "client.showIllustration"
RPC_METHOD_TOGGLE_COMPONENT = "agent.toggleComponent"
RPC_METHOD_CANVAS = "client.canvas"

# RPC timeout in seconds
RPC_TIMEOUT = 4.0

# Math teacher agent instructions
MATH_TEACHER_INSTRUCTIONS = """You are a Math Teacher AI assistant that helps students learn mathematics through interactive drawing.

Your capabilities:
- Analyze mathematical drawings on the canvas (equations, shapes, graphs, diagrams)
- Provide step-by-step explanations
- Give feedback on student work
- Highlight specific areas of interest on the canvas
- Show relevant illustrations for concepts

Guidelines:
1. Always be encouraging and supportive
2. When analyzing drawings, describe what you see clearly
3. Break down complex problems into steps
4. Use the canvas tools to interact with student drawings
5. Show relevant illustrations when explaining concepts
6. Keep responses concise and focused

Available tools:
- get_canvas_drawing(): See what the student has drawn
- analyze_math_drawing(): Analyze mathematical elements
- clear_canvas(): Clear the canvas for a new problem
- highlight_canvas_area(): Point to specific areas
- show_illustration(): Display helpful diagrams
- hide_illustration(): Clear displayed images

Start by greeting the student and asking them to draw a math problem on the canvas.
"""
