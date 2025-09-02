# Personal Portfolio Website (Flask)

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create necessary directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

class PortfolioData:
    def __init__(self):
        self.data_file = 'portfolio_data.json'
        self.load_data()
    
    def load_data(self):
        """Load portfolio data from JSON file"""
        default_data = {
            "personal_info": {
                "name": "John Doe",
                "title": "Full Stack Developer",
                "email": "john.doe@example.com",
                "phone": "+1 (555) 123-4567",
                "location": "New York, NY",
                "linkedin": "https://linkedin.com/in/johndoe",
                "github": "https://github.com/johndoe",
                "website": "https://johndoe.dev",
                "bio": "Passionate full-stack developer with 5+ years of experience in building scalable web applications. I love creating efficient solutions and learning new technologies."
            },
            "skills": [
                {"name": "Python", "level": 90, "category": "Backend"},
                {"name": "JavaScript", "level": 85, "category": "Frontend"},
                {"name": "React", "level": 80, "category": "Frontend"},
                {"name": "Flask/Django", "level": 88, "category": "Backend"},
                {"name": "HTML/CSS", "level": 92, "category": "Frontend"},
                {"name": "SQL", "level": 85, "category": "Database"},
                {"name": "Git", "level": 90, "category": "Tools"},
                {"name": "Docker", "level": 75, "category": "DevOps"}
            ],
            "projects": [
                {
                    "id": 1,
                    "title": "E-commerce Platform",
                    "description": "A full-stack e-commerce platform built with Python Flask and React",
                    "technologies": ["Python", "Flask", "React", "PostgreSQL", "Redis"],
                    "github_url": "https://github.com/johndoe/ecommerce",
                    "demo_url": "https://demo-ecommerce.johndoe.dev",
                    "image": "project1.jpg",
                    "featured": True,
                    "date": "2023-06-15"
                },
                {
                    "id": 2,
                    "title": "Weather Dashboard",
                    "description": "Real-time weather dashboard with data visualization",
                    "technologies": ["Python", "Django", "Chart.js", "API Integration"],
                    "github_url": "https://github.com/johndoe/weather-dashboard",
                    "demo_url": "https://weather.johndoe.dev",
                    "image": "project2.jpg",
                    "featured": True,
                    "date": "2023-04-20"
                },
                {
                    "id": 3,
                    "title": "Task Management App",
                    "description": "Collaborative task management application with real-time updates",
                    "technologies": ["Python", "FastAPI", "Vue.js", "WebSocket", "MongoDB"],
                    "github_url": "https://github.com/johndoe/task-manager",
                    "demo_url": "https://tasks.johndoe.dev",
                    "image": "project3.jpg",
                    "featured": False,
                    "date": "2023-02-10"
                }
            ],
            "experience": [
                {
                    "position": "Senior Full Stack Developer",
                    "company": "Tech Solutions Inc.",
                    "location": "New York, NY",
                    "start_date": "2022-01-15",
                    "end_date": null,
                    "current": True,
                    "description": "Led development of scalable web applications serving 100K+ users. Mentored junior developers and implemented DevOps best practices."
                },
                {
                    "position": "Full Stack Developer",
                    "company": "StartupXYZ",
                    "location": "San Francisco, CA",
                    "start_date": "2020-06-01",
                    "end_date": "2021-12-31",
                    "current": False,
                    "description": "Developed and maintained multiple web applications using Python, JavaScript, and cloud technologies."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of Technology",
                    "location": "New York, NY",
                    "graduation_date": "2020-05-15",
                    "gpa": "3.8/4.0"
                }
            ],
            "certifications": [
                "AWS Certified Developer - Associate",
                "Google Cloud Professional Developer",
                "MongoDB Certified Developer"
            ],
            "testimonials": [
                {
                    "name": "Sarah Johnson",
                    "position": "Project Manager at Tech Solutions Inc.",
                    "content": "John is an exceptional developer who consistently delivers high-quality work. His attention to detail and problem-solving skills are outstanding.",
                    "image": "testimonial1.jpg"
                },
                {
                    "name": "Mike Chen",
                    "position": "CTO at StartupXYZ",
                    "content": "Working with John was a pleasure. He's reliable, creative, and always goes the extra mile to ensure project success.",
                    "image": "testimonial2.jpg"
                }
            ]
        }
        
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                self.data = default_data
        else:
            self.data = default_data
            self.save_data()
    
    def save_data(self):
        """Save portfolio data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_project(self, project_data):
        """Add a new project"""
        new_id = max([p['id'] for p in self.data['projects']], default=0) + 1
        project_data['id'] = new_id
        project_data['date'] = datetime.now().strftime('%Y-%m-%d')
        self.data['projects'].append(project_data)
        self.save_data()
        return new_id

# Initialize portfolio data
portfolio_data = PortfolioData()

def create_templates():
    """Create HTML templates"""
    
    # Base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{{ personal_info.name }} - {{ personal_info.title }}{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{{ url_for('index') }}">{{ personal_info.name }}</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="#home">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
                    <li class="nav-item"><a class="nav-link" href="#skills">Skills</a></li>
                    <li class="nav-item"><a class="nav-link" href="#projects">Projects</a></li>
                    <li class="nav-item"><a class="nav-link" href="#experience">Experience</a></li>
                    <li class="nav-item"><a class="nav-link" href="#contact">Contact</a></li>
                </ul>
            </div>
        </div>
    </nav>

    {% block content %}{% endblock %}

    <!-- Footer -->
    <footer class="bg-dark text-light py-4">
        <div class="container text-center">
            <div class="row">
                <div class="col-md-6">
                    <p>&copy; 2023 {{ personal_info.name }}. All rights reserved.</p>
                </div>
                <div class="col-md-6">
                    <div class="social-links">
                        <a href="{{ personal_info.linkedin }}" target="_blank" class="text-light me-3">
                            <i class="fab fa-linkedin fa-lg"></i>
                        </a>
                        <a href="{{ personal_info.github }}" target="_blank" class="text-light me-3">
                            <i class="fab fa-github fa-lg"></i>
                        </a>
                        <a href="mailto:{{ personal_info.email }}" class="text-light">
                            <i class="fas fa-envelope fa-lg"></i>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>'''

    # Index template
    index_template = '''{% extends "base.html" %}

{% block content %}
<!-- Hero Section -->
<section id="home" class="hero-section">
    <div class="container">
        <div class="row align-items-center min-vh-100">
            <div class="col-lg-6">
                <h1 class="display-4 fw-bold mb-3">Hi, I'm {{ personal_info.name }}</h1>
                <h2 class="h3 text-primary mb-4">{{ personal_info.title }}</h2>
                <p class="lead mb-4">{{ personal_info.bio }}</p>
                <div class="hero-buttons">
                    <a href="#projects" class="btn btn-primary btn-lg me-3">View My Work</a>
                    <a href="#contact" class="btn btn-outline-primary btn-lg">Get In Touch</a>
                </div>
            </div>
            <div class="col-lg-6 text-center">
                <div class="hero-image">
                    <img src="{{ url_for('static', filename='images/profile.jpg') }}" 
                         alt="{{ personal_info.name }}" class="img-fluid rounded-circle profile-img">
                </div>
            </div>
        </div>
    </div>
</section>

<!-- About Section -->
<section id="about" class="py-5 bg-light">
    <div class="container">
        <div class="row">
            <div class="col-lg-8 mx-auto text-center">
                <h2 class="section-title">About Me</h2>
                <p class="lead">{{ personal_info.bio }}</p>
                <div class="row mt-4">
                    <div class="col-md-6">
                        <div class="info-item">
                            <i class="fas fa-envelope text-primary"></i>
                            <span>{{ personal_info.email }}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-item">
                            <i class="fas fa-phone text-primary"></i>
                            <span>{{ personal_info.phone }}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-item">
                            <i class="fas fa-map-marker-alt text-primary"></i>
                            <span>{{ personal_info.location }}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="info-item">
                            <i class="fas fa-globe text-primary"></i>
                            <span>{{ personal_info.website }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<!-- Skills Section -->
<section id="skills" class="py-5">
    <div class="container">
        <h2 class="section-title text-center">Skills & Technologies</h2>
        <div class="row">
            {% for skill in skills %}
            <div class="col-lg-6 mb-3">
                <div class="skill-item">
                    <div class="d-flex justify-content-between mb-1">
                        <span class="fw-semibold">{{ skill.name }}</span>
                        <span class="text-muted">{{ skill.level }}%</span>
                    </div>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" 
                             style="width: {{ skill.level }}%" 
                             aria-valuenow="{{ skill.level }}" 
                             aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Projects Section -->
<section id="projects" class="py-5 bg-light">
    <div class="container">
        <h2 class="section-title text-center">Featured Projects</h2>
        <div class="row">
            {% for project in projects %}
            {% if project.featured %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card project-card h-100">
                    <img src="{{ url_for('static', filename='images/' + project.image) }}" 
                         class="card-img-top" alt="{{ project.title }}">
                    <div class="card-body">
                        <h5 class="card-title">{{ project.title }}</h5>
                        <p class="card-text">{{ project.description }}</p>
                        <div class="technologies mb-3">
                            {% for tech in project.technologies %}
                            <span class="badge bg-secondary me-1">{{ tech }}</span>
                            {% endfor %}
                        </div>
                        <div class="project-links">
                            <a href="{{ project.github_url }}" target="_blank" class="btn btn-outline-primary btn-sm me-2">
                                <i class="fab fa-github"></i> Code
                            </a>
                            <a href="{{ project.demo_url }}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt"></i> Demo
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
            {% endfor %}
        </div>
        <div class="text-center mt-4">
            <a href="{{ url_for('projects') }}" class="btn btn-outline-primary">View All Projects</a>
        </div>
    </div>
</section>

<!-- Experience Section -->
<section id="experience" class="py-5">
    <div class="container">
        <h2 class="section-title text-center">Experience</h2>
        <div class="row">
            <div class="col-lg-8 mx-auto">
                {% for exp in experience %}
                <div class="experience-item mb-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ exp.position }}</h5>
                            <h6 class="card-subtitle mb-2 text-primary">{{ exp.company }}</h6>
                            <p class="text-muted mb-2">
                                <i class="fas fa-calendar"></i> 
                                {{ exp.start_date }} - 
                                {% if exp.current %}Present{% else %}{{ exp.end_date }}{% endif %}
                                | <i class="fas fa-map-marker-alt"></i> {{ exp.location }}
                            </p>
                            <p class="card-text">{{ exp.description }}</p>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</section>

<!-- Contact Section -->
<section id="contact" class="py-5 bg-light">
    <div class="container">
        <h2 class="section-title text-center">Get In Touch</h2>
        <div class="row">
            <div class="col-lg-8 mx-auto">
                <form id="contactForm" action="{{ url_for('contact') }}" method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <input type="text" class="form-control" name="name" placeholder="Your Name" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <input type="email" class="form-control" name="email" placeholder="Your Email" required>
                        </div>
                    </div>
                    <div class="mb-3">
                        <input type="text" class="form-control" name="subject" placeholder="Subject" required>
                    </div>
                    <div class="mb-3">
                        <textarea class="form-control" name="message" rows="5" placeholder="Your Message" required></textarea>
                    </div>
                    <div class="text-center">
                        <button type="submit" class="btn btn-primary btn-lg">Send Message</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</section>
{% endblock %}'''

    # Projects template
    projects_template = '''{% extends "base.html" %}

{% block title %}Projects - {{ personal_info.name }}{% endblock %}

{% block content %}
<section class="py-5" style="margin-top: 70px;">
    <div class="container">
        <h2 class="section-title text-center">All Projects</h2>
        <div class="row">
            {% for project in projects %}
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card project-card h-100">
                    <img src="{{ url_for('static', filename='images/' + project.image) }}" 
                         class="card-img-top" alt="{{ project.title }}">
                    <div class="card-body">
                        <h5 class="card-title">{{ project.title }}</h5>
                        <p class="card-text">{{ project.description }}</p>
                        <div class="technologies mb-3">
                            {% for tech in project.technologies %}
                            <span class="badge bg-secondary me-1">{{ tech }}</span>
                            {% endfor %}
                        </div>
                        <div class="project-links">
                            <a href="{{ project.github_url }}" target="_blank" class="btn btn-outline-primary btn-sm me-2">
                                <i class="fab fa-github"></i> Code
                            </a>
                            <a href="{{ project.demo_url }}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt"></i> Demo
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>
{% endblock %}'''

    # Write templates to files
    with open('templates/base.html', 'w') as f:
        f.write(base_template)
    
    with open('templates/index.html', 'w') as f:
        f.write(index_template)
    
    with open('templates/projects.html', 'w') as f:
        f.write(projects_template)

def create_static_files():
    """Create CSS and JavaScript files"""
    
    # CSS
    css_content = '''/* Custom Styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --dark-color: #343a40;
    --light-color: #f8f9fa;
}

body {
    padding-top: 70px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.section-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 3rem;
    color: var(--dark-color);
}

.hero-section {
    background: linear-gradient(135deg, var(--primary-color) 0%, #0056b3 100%);
    color: white;
    min-height: 100vh;
    display: flex;
    align-items: center;
}

.profile-img {
    width: 300px;
    height: 300px;
    object-fit: cover;
    border: 5px solid white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.hero-buttons .btn {
    padding: 12px 30px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.info-item i {
    width: 30px;
    margin-right: 15px;
}

.skill-item {
    margin-bottom: 1.5rem;
}

.progress {
    height: 8px;
    border-radius: 10px;
    background-color: #e9ecef;
}

.progress-bar {
    border-radius: 10px;
    background: linear-gradient(90deg, var(--primary-color), #0056b3);
}

.project-card {
    border: none;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.project-card .card-img-top {
    height: 200px;
    object-fit: cover;
}

.technologies .badge {
    font-size: 0.7rem;
    padding: 0.4rem 0.6rem;
}

.experience-item .card {
    border-left: 4px solid var(--primary-color);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.social-links a {
    transition: color 0.3s ease;
}

.social-links a:hover {
    color: var(--primary-color) !important;
}

#contactForm .form-control {
    border-radius: 10px;
    border: 2px solid #e9ecef;
    padding: 12px 15px;
    font-size: 1rem;
}

#contactForm .form-control:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,0.25);
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Responsive design */
@media (max-width: 768px) {
    .section-title {
        font-size: 2rem;
    }
    
    .profile-img {
        width: 200px;
        height: 200px;
    }
    
    .hero-buttons .btn {
        display: block;
        width: 100%;
        margin-bottom: 1rem;
    }
}'''

    # JavaScript
    js_content = '''// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 70; // Account for fixed navbar
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Update active navigation link based on scroll position
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    function updateActiveLink() {
        const scrollPos = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    window.addEventListener('scroll', updateActiveLink);
    
    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            // Add loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            // Reset button after form submission (handled by Flask)
            setTimeout(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 3000);
        });
    }
    
    // Animate skill bars on scroll
    const skillBars = document.querySelectorAll('.progress-bar');
    const animateSkillBars = () => {
        skillBars.forEach(bar => {
            const barTop = bar.getBoundingClientRect().top;
            const triggerPoint = window.innerHeight * 0.8;
            
            if (barTop < triggerPoint) {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                    bar.style.transition = 'width 1.5s ease-in-out';
                }, 100);
            }
        });
    };
    
    window.addEventListener('scroll', animateSkillBars);
    animateSkillBars(); // Initial check
});'''

    # Write static files
    with open('static/css/style.css', 'w') as f:
        f.write(css_content)
    
    with open('static/js/script.js', 'w') as f:
        f.write(js_content)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', **portfolio_data.data)

@app.route('/projects')
def projects():
    return render_template('projects.html', **portfolio_data.data)

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email
        # For demo purposes, we'll just save to a file
        contact_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save contact message
        contacts_file = 'contacts.json'
        contacts = []
        
        if os.path.exists(contacts_file):
            try:
                with open(contacts_file, 'r') as f:
                    contacts = json.load(f)
            except:
                contacts = []
        
        contacts.append(contact_data)
        
        with open(contacts_file, 'w') as f:
            json.dump(contacts, f, indent=2)
        
        flash('Thank you for your message! I\'ll get back to you soon.', 'success')
        return redirect(url_for('index') + '#contact')

@app.route('/admin')
def admin():
    """Simple admin interface to view contacts"""
    contacts = []
    if os.path.exists('contacts.json'):
        try:
            with open('contacts.json', 'r') as f:
                contacts = json.load(f)
        except:
            contacts = []
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - Contact Messages</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Contact Messages</h2>
            <div class="row">
    '''
    
    for contact in reversed(contacts):
        html += f'''
        <div class="col-12 mb-3">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{contact['subject']}</h5>
                    <h6 class="card-subtitle mb-2 text-muted">From: {contact['name']} ({contact['email']})</h6>
                    <p class="card-text">{contact['message']}</p>
                    <small class="text-muted">Received: {contact['timestamp']}</small>
                </div>
            </div>
        </div>
        '''
    
    html += '''
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

def main():
    """Main function to run the portfolio website"""
    print("Setting up Personal Portfolio Website...")
    
    # Create templates and static files
    create_templates()
    create_static_files()
    
    print("Portfolio website setup complete!")
    print("\nFeatures:")
    print("- Responsive design with Bootstrap")
    print("- Hero section with personal info")
    print("- Skills section with progress bars")
    print("- Projects showcase")
    print("- Experience timeline")
    print("- Contact form")
    print("- Admin interface for viewing messages")
    
    print(f"\nTo run the website:")
    print(f"1. Make sure Flask is installed: pip install flask")
    print(f"2. Run: python {__file__}")
    print(f"3. Open http://localhost:5000 in your browser")
    print(f"4. Admin interface: http://localhost:5000/admin")
    
    # Run the Flask app
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()
