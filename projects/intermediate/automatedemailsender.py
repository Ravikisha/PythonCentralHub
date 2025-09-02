# Automated Email Sender

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv
import json
import schedule
import time
import sqlite3
import datetime
from typing import List, Dict, Optional, Tuple
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from pathlib import Path
import re
import ssl
import socket
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmailAccount:
    """Email account configuration"""
    email: str
    password: str
    smtp_server: str
    smtp_port: int
    imap_server: str = ""
    imap_port: int = 993
    use_tls: bool = True

@dataclass
class EmailTemplate:
    """Email template"""
    name: str
    subject: str
    body: str
    is_html: bool = False
    variables: List[str] = None

class EmailDatabase:
    """Database for email management"""
    
    def __init__(self, db_path: str = "email_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Email accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    smtp_server TEXT NOT NULL,
                    smtp_port INTEGER NOT NULL,
                    imap_server TEXT,
                    imap_port INTEGER DEFAULT 993,
                    use_tls BOOLEAN DEFAULT 1,
                    created_date TEXT NOT NULL
                )
            """)
            
            # Email templates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    is_html BOOLEAN DEFAULT 0,
                    variables TEXT,
                    created_date TEXT NOT NULL,
                    last_used TEXT
                )
            """)
            
            # Recipients/contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    group_name TEXT,
                    custom_fields TEXT,
                    added_date TEXT NOT NULL,
                    UNIQUE(email, group_name)
                )
            """)
            
            # Sent emails log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sent_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    template_id INTEGER,
                    recipient_email TEXT NOT NULL,
                    recipient_name TEXT,
                    subject TEXT NOT NULL,
                    sent_date TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    FOREIGN KEY (account_id) REFERENCES email_accounts (id),
                    FOREIGN KEY (template_id) REFERENCES email_templates (id)
                )
            """)
            
            # Scheduled emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    template_id INTEGER NOT NULL,
                    recipient_group TEXT,
                    schedule_time TEXT NOT NULL,
                    repeat_type TEXT,
                    next_send_time TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_date TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES email_accounts (id),
                    FOREIGN KEY (template_id) REFERENCES email_templates (id)
                )
            """)
            
            conn.commit()
    
    def add_email_account(self, name: str, email: str, smtp_server: str, smtp_port: int,
                         imap_server: str = "", imap_port: int = 993, use_tls: bool = True) -> bool:
        """Add email account configuration"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO email_accounts (name, email, smtp_server, smtp_port, 
                                              imap_server, imap_port, use_tls, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, email, smtp_server, smtp_port, imap_server, imap_port, 
                      use_tls, datetime.datetime.now().isoformat()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_email_accounts(self) -> List[Dict]:
        """Get all email accounts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_accounts ORDER BY name")
            accounts = []
            for row in cursor.fetchall():
                accounts.append({
                    'id': row[0], 'name': row[1], 'email': row[2],
                    'smtp_server': row[3], 'smtp_port': row[4],
                    'imap_server': row[5], 'imap_port': row[6],
                    'use_tls': bool(row[7]), 'created_date': row[8]
                })
            return accounts
    
    def add_template(self, name: str, subject: str, body: str, is_html: bool = False, 
                    variables: List[str] = None) -> bool:
        """Add email template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                variables_json = json.dumps(variables) if variables else "[]"
                cursor.execute("""
                    INSERT INTO email_templates (name, subject, body, is_html, variables, created_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (name, subject, body, is_html, variables_json, 
                      datetime.datetime.now().isoformat()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_templates(self) -> List[Dict]:
        """Get all email templates"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM email_templates ORDER BY name")
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'id': row[0], 'name': row[1], 'subject': row[2],
                    'body': row[3], 'is_html': bool(row[4]),
                    'variables': json.loads(row[5]) if row[5] else [],
                    'created_date': row[6], 'last_used': row[7]
                })
            return templates
    
    def add_contact(self, name: str, email: str, group_name: str = "default", 
                   custom_fields: Dict = None) -> bool:
        """Add contact to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                custom_fields_json = json.dumps(custom_fields) if custom_fields else "{}"
                cursor.execute("""
                    INSERT INTO contacts (name, email, group_name, custom_fields, added_date)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, group_name, custom_fields_json, 
                      datetime.datetime.now().isoformat()))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_contacts(self, group_name: str = None) -> List[Dict]:
        """Get contacts from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if group_name:
                cursor.execute("SELECT * FROM contacts WHERE group_name = ? ORDER BY name", (group_name,))
            else:
                cursor.execute("SELECT * FROM contacts ORDER BY group_name, name")
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'id': row[0], 'name': row[1], 'email': row[2],
                    'group_name': row[3], 
                    'custom_fields': json.loads(row[4]) if row[4] else {},
                    'added_date': row[5]
                })
            return contacts
    
    def get_contact_groups(self) -> List[str]:
        """Get all contact groups"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT group_name FROM contacts ORDER BY group_name")
            return [row[0] for row in cursor.fetchall()]
    
    def log_sent_email(self, account_id: int, template_id: int, recipient_email: str,
                      recipient_name: str, subject: str, success: bool, 
                      error_message: str = None):
        """Log sent email"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sent_emails (account_id, template_id, recipient_email, 
                                       recipient_name, subject, sent_date, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (account_id, template_id, recipient_email, recipient_name, subject,
                  datetime.datetime.now().isoformat(), success, error_message))
            conn.commit()

class EmailSender:
    """Main email sending class"""
    
    def __init__(self, database: EmailDatabase):
        self.db = database
        self.common_providers = {
            'gmail.com': {'smtp': 'smtp.gmail.com', 'port': 587, 'imap': 'imap.gmail.com'},
            'outlook.com': {'smtp': 'smtp-mail.outlook.com', 'port': 587, 'imap': 'outlook.office365.com'},
            'hotmail.com': {'smtp': 'smtp-mail.outlook.com', 'port': 587, 'imap': 'outlook.office365.com'},
            'yahoo.com': {'smtp': 'smtp.mail.yahoo.com', 'port': 587, 'imap': 'imap.mail.yahoo.com'},
            'icloud.com': {'smtp': 'smtp.mail.me.com', 'port': 587, 'imap': 'imap.mail.me.com'},
        }
    
    def get_smtp_settings(self, email: str) -> Dict:
        """Get SMTP settings for common email providers"""
        domain = email.split('@')[1].lower()
        return self.common_providers.get(domain, {})
    
    def test_connection(self, account: EmailAccount, password: str) -> Tuple[bool, str]:
        """Test email account connection"""
        try:
            # Create SMTP connection
            if account.smtp_port == 465:
                server = smtplib.SMTP_SSL(account.smtp_server, account.smtp_port)
            else:
                server = smtplib.SMTP(account.smtp_server, account.smtp_port)
                if account.use_tls:
                    server.starttls()
            
            # Login
            server.login(account.email, password)
            server.quit()
            
            return True, "Connection successful"
            
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed - check email and password"
        except smtplib.SMTPConnectError:
            return False, f"Cannot connect to SMTP server {account.smtp_server}:{account.smtp_port}"
        except socket.gaierror:
            return False, f"Invalid SMTP server address: {account.smtp_server}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    def send_email(self, account: EmailAccount, password: str, to_email: str, 
                   subject: str, body: str, is_html: bool = False, 
                   attachments: List[str] = None, to_name: str = "") -> Tuple[bool, str]:
        """Send a single email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative' if is_html else 'mixed')
            msg['From'] = account.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {Path(file_path).name}'
                        )
                        msg.attach(part)
            
            # Create SMTP connection and send
            if account.smtp_port == 465:
                server = smtplib.SMTP_SSL(account.smtp_server, account.smtp_port)
            else:
                server = smtplib.SMTP(account.smtp_server, account.smtp_port)
                if account.use_tls:
                    server.starttls()
            
            server.login(account.email, password)
            server.send_message(msg)
            server.quit()
            
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send email: {str(e)}"
    
    def send_bulk_emails(self, account: EmailAccount, password: str, 
                        recipients: List[Dict], template: EmailTemplate,
                        attachments: List[str] = None, 
                        progress_callback=None) -> Dict:
        """Send bulk emails with template"""
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for i, recipient in enumerate(recipients):
            try:
                # Replace variables in template
                subject = self.replace_variables(template.subject, recipient)
                body = self.replace_variables(template.body, recipient)
                
                # Send email
                success, message = self.send_email(
                    account, password, recipient['email'], subject, body,
                    template.is_html, attachments, recipient.get('name', '')
                )
                
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"{recipient['email']}: {message}")
                
                # Call progress callback
                if progress_callback:
                    progress = (i + 1) / len(recipients) * 100
                    progress_callback(progress, recipient['email'], success)
                
                # Small delay to avoid being flagged as spam
                time.sleep(1)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{recipient['email']}: {str(e)}")
        
        return results
    
    def replace_variables(self, text: str, data: Dict) -> str:
        """Replace variables in template text"""
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            text = text.replace(placeholder, str(value))
        return text
    
    def parse_csv_contacts(self, csv_file_path: str) -> List[Dict]:
        """Parse contacts from CSV file"""
        contacts = []
        
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Clean up the row
                    clean_row = {k.strip(): v.strip() for k, v in row.items() if v.strip()}
                    
                    # Ensure email field exists
                    if 'email' in clean_row and clean_row['email']:
                        if 'name' not in clean_row:
                            clean_row['name'] = clean_row['email'].split('@')[0]
                        contacts.append(clean_row)
                        
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
        
        return contacts

class EmailScheduler:
    """Email scheduling functionality"""
    
    def __init__(self, email_sender: EmailSender):
        self.email_sender = email_sender
        self.running = False
        self.scheduler_thread = None
    
    def start_scheduler(self):
        """Start the email scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the email scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def schedule_email(self, account_id: int, template_id: int, 
                      recipient_group: str, schedule_time: str, 
                      repeat_type: str = "none"):
        """Schedule an email"""
        # Implementation would depend on specific scheduling requirements
        pass

class EmailGUI:
    """GUI for email sender application"""
    
    def __init__(self):
        self.db = EmailDatabase()
        self.email_sender = EmailSender(self.db)
        self.scheduler = EmailScheduler(self.email_sender)
        
        self.root = tk.Tk()
        self.root.title("Automated Email Sender")
        self.root.geometry("1000x700")
        
        self.current_account = None
        self.current_password = None
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Accounts tab
        self.accounts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.accounts_frame, text="Email Accounts")
        self.setup_accounts_tab()
        
        # Templates tab
        self.templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.templates_frame, text="Templates")
        self.setup_templates_tab()
        
        # Contacts tab
        self.contacts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.contacts_frame, text="Contacts")
        self.setup_contacts_tab()
        
        # Send Email tab
        self.send_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.send_frame, text="Send Email")
        self.setup_send_tab()
        
        # History tab
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="History")
        self.setup_history_tab()
    
    def setup_accounts_tab(self):
        """Setup email accounts tab"""
        main_frame = ttk.Frame(self.accounts_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Account list
        list_frame = ttk.LabelFrame(main_frame, text="Email Accounts", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for accounts
        self.accounts_tree = ttk.Treeview(list_frame, columns=('Email', 'SMTP Server', 'Port'), 
                                         show='tree headings', height=8)
        self.accounts_tree.heading('#0', text='Account Name')
        self.accounts_tree.heading('Email', text='Email')
        self.accounts_tree.heading('SMTP Server', text='SMTP Server')
        self.accounts_tree.heading('Port', text='Port')
        
        self.accounts_tree.pack(fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Scrollbar for accounts tree
        accounts_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.accounts_tree.yview)
        accounts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.accounts_tree.configure(yscrollcommand=accounts_scrollbar.set)
        
        # Add account form
        form_frame = ttk.LabelFrame(main_frame, text="Add/Edit Account", padding="10")
        form_frame.pack(fill=tk.X)
        
        # Form fields
        ttk.Label(form_frame, text="Account Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.account_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.account_name_var, width=25).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(form_frame, text="Email:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.account_email_var = tk.StringVar()
        email_entry = ttk.Entry(form_frame, textvariable=self.account_email_var, width=30)
        email_entry.grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)
        email_entry.bind('<FocusOut>', self.auto_detect_smtp)
        
        ttk.Label(form_frame, text="SMTP Server:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.smtp_server_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.smtp_server_var, width=25).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(form_frame, text="SMTP Port:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.smtp_port_var = tk.StringVar(value="587")
        ttk.Entry(form_frame, textvariable=self.smtp_port_var, width=10).grid(row=1, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test Connection", command=self.test_account_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_account_form).pack(side=tk.LEFT, padx=5)
    
    def setup_templates_tab(self):
        """Setup email templates tab"""
        main_frame = ttk.Frame(self.templates_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Template list
        list_frame = ttk.LabelFrame(main_frame, text="Email Templates", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.templates_tree = ttk.Treeview(list_frame, columns=('Subject', 'Type'), 
                                          show='tree headings', height=6)
        self.templates_tree.heading('#0', text='Template Name')
        self.templates_tree.heading('Subject', text='Subject')
        self.templates_tree.heading('Type', text='Type')
        
        self.templates_tree.pack(fill=tk.BOTH, expand=True)
        self.templates_tree.bind('<Double-1>', self.load_template)
        
        # Template form
        form_frame = ttk.LabelFrame(main_frame, text="Create/Edit Template", padding="10")
        form_frame.pack(fill=tk.X)
        
        # Template name and subject
        top_frame = ttk.Frame(form_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(top_frame, text="Name:").pack(side=tk.LEFT)
        self.template_name_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.template_name_var, width=20).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(top_frame, text="Subject:").pack(side=tk.LEFT, padx=(20, 0))
        self.template_subject_var = tk.StringVar()
        ttk.Entry(top_frame, textvariable=self.template_subject_var, width=40).pack(side=tk.LEFT, padx=5)
        
        self.template_html_var = tk.BooleanVar()
        ttk.Checkbutton(top_frame, text="HTML", variable=self.template_html_var).pack(side=tk.LEFT, padx=10)
        
        # Template body
        ttk.Label(form_frame, text="Body:").pack(anchor=tk.W)
        self.template_body = scrolledtext.ScrolledText(form_frame, height=8, wrap=tk.WORD)
        self.template_body.pack(fill=tk.X, pady=5)
        
        # Variables info
        variables_info = "Use variables like {name}, {email}, {company} in your template"
        ttk.Label(form_frame, text=variables_info, font=("TkDefaultFont", 8)).pack(anchor=tk.W)
        
        # Template buttons
        template_buttons = ttk.Frame(form_frame)
        template_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(template_buttons, text="Save Template", command=self.save_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(template_buttons, text="Clear", command=self.clear_template_form).pack(side=tk.LEFT, padx=5)
    
    def setup_contacts_tab(self):
        """Setup contacts tab"""
        main_frame = ttk.Frame(self.contacts_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Contacts list
        list_frame = ttk.LabelFrame(main_frame, text="Contacts", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.contacts_tree = ttk.Treeview(list_frame, columns=('Email', 'Group'), 
                                         show='tree headings', height=8)
        self.contacts_tree.heading('#0', text='Name')
        self.contacts_tree.heading('Email', text='Email')
        self.contacts_tree.heading('Group', text='Group')
        
        self.contacts_tree.pack(fill=tk.BOTH, expand=True)
        
        # Contact management
        mgmt_frame = ttk.Frame(main_frame)
        mgmt_frame.pack(fill=tk.X)
        
        # Import from CSV
        import_frame = ttk.LabelFrame(mgmt_frame, text="Import Contacts", padding="5")
        import_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(import_frame, text="Import from CSV", command=self.import_contacts_csv).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(import_frame, text="Group:").pack(side=tk.LEFT, padx=(20, 5))
        self.import_group_var = tk.StringVar(value="default")
        ttk.Entry(import_frame, textvariable=self.import_group_var, width=15).pack(side=tk.LEFT)
        
        # Add contact manually
        add_frame = ttk.LabelFrame(mgmt_frame, text="Add Contact", padding="5")
        add_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        contact_fields = ttk.Frame(add_frame)
        contact_fields.pack(fill=tk.X)
        
        ttk.Label(contact_fields, text="Name:").grid(row=0, column=0, sticky=tk.W)
        self.contact_name_var = tk.StringVar()
        ttk.Entry(contact_fields, textvariable=self.contact_name_var, width=15).grid(row=0, column=1, padx=2)
        
        ttk.Label(contact_fields, text="Email:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.contact_email_var = tk.StringVar()
        ttk.Entry(contact_fields, textvariable=self.contact_email_var, width=20).grid(row=0, column=3, padx=2)
        
        ttk.Button(add_frame, text="Add Contact", command=self.add_contact).pack(pady=5)
    
    def setup_send_tab(self):
        """Setup send email tab"""
        main_frame = ttk.Frame(self.send_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Send options
        options_frame = ttk.LabelFrame(main_frame, text="Send Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Account selection
        ttk.Label(options_frame, text="From Account:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.send_account_var = tk.StringVar()
        self.send_account_combo = ttk.Combobox(options_frame, textvariable=self.send_account_var, width=30)
        self.send_account_combo.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        ttk.Button(options_frame, text="Set Password", command=self.set_account_password).grid(row=0, column=2, padx=10)
        
        # Template selection
        ttk.Label(options_frame, text="Template:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.send_template_var = tk.StringVar()
        self.send_template_combo = ttk.Combobox(options_frame, textvariable=self.send_template_var, width=30)
        self.send_template_combo.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Recipient selection
        ttk.Label(options_frame, text="Recipients:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.recipient_type_var = tk.StringVar(value="group")
        
        type_frame = ttk.Frame(options_frame)
        type_frame.grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky=tk.W)
        
        ttk.Radiobutton(type_frame, text="Group", variable=self.recipient_type_var, 
                       value="group", command=self.update_recipient_options).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="All Contacts", variable=self.recipient_type_var, 
                       value="all", command=self.update_recipient_options).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="Single Email", variable=self.recipient_type_var, 
                       value="single", command=self.update_recipient_options).pack(side=tk.LEFT, padx=10)
        
        # Recipient details
        self.recipient_frame = ttk.Frame(options_frame)
        self.recipient_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        self.recipient_group_var = tk.StringVar()
        self.recipient_email_var = tk.StringVar()
        
        self.update_recipient_options()
        
        # Attachments
        attach_frame = ttk.LabelFrame(main_frame, text="Attachments", padding="5")
        attach_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.attachments_list = tk.Listbox(attach_frame, height=3)
        self.attachments_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        attach_buttons = ttk.Frame(attach_frame)
        attach_buttons.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(attach_buttons, text="Add File", command=self.add_attachment).pack(pady=2)
        ttk.Button(attach_buttons, text="Remove", command=self.remove_attachment).pack(pady=2)
        
        # Send button and progress
        send_frame = ttk.Frame(main_frame)
        send_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(send_frame, text="Send Emails", command=self.send_emails, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.StringVar(value="Ready to send")
        ttk.Label(send_frame, textvariable=self.progress_var).pack(side=tk.LEFT, padx=20)
        
        self.progress_bar = ttk.Progressbar(send_frame, length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def setup_history_tab(self):
        """Setup email history tab"""
        main_frame = ttk.Frame(self.history_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # History list
        self.history_tree = ttk.Treeview(main_frame, columns=('Recipient', 'Subject', 'Date', 'Status'), 
                                        show='tree headings')
        self.history_tree.heading('#0', text='ID')
        self.history_tree.heading('Recipient', text='Recipient')
        self.history_tree.heading('Subject', text='Subject')
        self.history_tree.heading('Date', text='Date')
        self.history_tree.heading('Status', text='Status')
        
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(main_frame, text="Refresh History", command=self.refresh_history).pack(pady=10)
    
    def auto_detect_smtp(self, event=None):
        """Auto-detect SMTP settings based on email"""
        email = self.account_email_var.get()
        if '@' in email:
            settings = self.email_sender.get_smtp_settings(email)
            if settings:
                self.smtp_server_var.set(settings.get('smtp', ''))
                self.smtp_port_var.set(str(settings.get('port', 587)))
    
    def add_account(self):
        """Add new email account"""
        name = self.account_name_var.get().strip()
        email = self.account_email_var.get().strip()
        smtp_server = self.smtp_server_var.get().strip()
        
        try:
            smtp_port = int(self.smtp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        if not all([name, email, smtp_server]):
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if self.db.add_email_account(name, email, smtp_server, smtp_port):
            messagebox.showinfo("Success", "Email account added successfully")
            self.clear_account_form()
            self.refresh_accounts()
        else:
            messagebox.showerror("Error", "Account name already exists")
    
    def test_account_connection(self):
        """Test email account connection"""
        email = self.account_email_var.get().strip()
        smtp_server = self.smtp_server_var.get().strip()
        
        try:
            smtp_port = int(self.smtp_port_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return
        
        if not all([email, smtp_server]):
            messagebox.showerror("Error", "Please enter email and SMTP server")
            return
        
        # Get password
        password = simpledialog.askstring("Password", f"Enter password for {email}:", show='*')
        if not password:
            return
        
        account = EmailAccount(email, password, smtp_server, smtp_port)
        success, message = self.email_sender.test_connection(account, password)
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def clear_account_form(self):
        """Clear account form"""
        self.account_name_var.set("")
        self.account_email_var.set("")
        self.smtp_server_var.set("")
        self.smtp_port_var.set("587")
    
    def save_template(self):
        """Save email template"""
        name = self.template_name_var.get().strip()
        subject = self.template_subject_var.get().strip()
        body = self.template_body.get(1.0, tk.END).strip()
        is_html = self.template_html_var.get()
        
        if not all([name, subject, body]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # Extract variables from template
        variables = re.findall(r'\{(\w+)\}', subject + ' ' + body)
        variables = list(set(variables))  # Remove duplicates
        
        if self.db.add_template(name, subject, body, is_html, variables):
            messagebox.showinfo("Success", f"Template saved with variables: {', '.join(variables)}")
            self.clear_template_form()
            self.refresh_templates()
        else:
            messagebox.showerror("Error", "Template name already exists")
    
    def load_template(self, event):
        """Load selected template"""
        selection = self.templates_tree.selection()
        if selection:
            item = self.templates_tree.item(selection[0])
            template_name = item['text']
            
            templates = self.db.get_templates()
            for template in templates:
                if template['name'] == template_name:
                    self.template_name_var.set(template['name'])
                    self.template_subject_var.set(template['subject'])
                    self.template_body.delete(1.0, tk.END)
                    self.template_body.insert(1.0, template['body'])
                    self.template_html_var.set(template['is_html'])
                    break
    
    def clear_template_form(self):
        """Clear template form"""
        self.template_name_var.set("")
        self.template_subject_var.set("")
        self.template_body.delete(1.0, tk.END)
        self.template_html_var.set(False)
    
    def import_contacts_csv(self):
        """Import contacts from CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            contacts = self.email_sender.parse_csv_contacts(file_path)
            group_name = self.import_group_var.get().strip() or "default"
            
            added_count = 0
            for contact in contacts:
                if self.db.add_contact(contact.get('name', ''), contact['email'], 
                                     group_name, contact):
                    added_count += 1
            
            messagebox.showinfo("Import Complete", 
                              f"Added {added_count} contacts to group '{group_name}'")
            self.refresh_contacts()
    
    def add_contact(self):
        """Add single contact"""
        name = self.contact_name_var.get().strip()
        email = self.contact_email_var.get().strip()
        
        if not email:
            messagebox.showerror("Error", "Please enter an email address")
            return
        
        if not name:
            name = email.split('@')[0]
        
        if self.db.add_contact(name, email, "default"):
            messagebox.showinfo("Success", "Contact added successfully")
            self.contact_name_var.set("")
            self.contact_email_var.set("")
            self.refresh_contacts()
        else:
            messagebox.showerror("Error", "Contact already exists")
    
    def update_recipient_options(self):
        """Update recipient selection options"""
        for widget in self.recipient_frame.winfo_children():
            widget.destroy()
        
        if self.recipient_type_var.get() == "group":
            ttk.Label(self.recipient_frame, text="Group:").pack(side=tk.LEFT)
            group_combo = ttk.Combobox(self.recipient_frame, textvariable=self.recipient_group_var, width=20)
            group_combo.pack(side=tk.LEFT, padx=5)
            
            # Update group options
            groups = self.db.get_contact_groups()
            group_combo['values'] = groups
            if groups:
                self.recipient_group_var.set(groups[0])
        
        elif self.recipient_type_var.get() == "single":
            ttk.Label(self.recipient_frame, text="Email:").pack(side=tk.LEFT)
            ttk.Entry(self.recipient_frame, textvariable=self.recipient_email_var, width=30).pack(side=tk.LEFT, padx=5)
    
    def set_account_password(self):
        """Set password for selected account"""
        account_name = self.send_account_var.get()
        if not account_name:
            messagebox.showerror("Error", "Please select an account")
            return
        
        password = simpledialog.askstring("Password", f"Enter password for {account_name}:", show='*')
        if password:
            self.current_password = password
            messagebox.showinfo("Success", "Password set successfully")
    
    def add_attachment(self):
        """Add attachment file"""
        file_path = filedialog.askopenfilename(title="Select attachment")
        if file_path:
            self.attachments_list.insert(tk.END, file_path)
    
    def remove_attachment(self):
        """Remove selected attachment"""
        selection = self.attachments_list.curselection()
        if selection:
            self.attachments_list.delete(selection[0])
    
    def send_emails(self):
        """Send emails"""
        if not self.current_account or not self.current_password:
            messagebox.showerror("Error", "Please select account and set password")
            return
        
        template_name = self.send_template_var.get()
        if not template_name:
            messagebox.showerror("Error", "Please select a template")
            return
        
        # Get template
        templates = self.db.get_templates()
        template = None
        for t in templates:
            if t['name'] == template_name:
                template = EmailTemplate(t['name'], t['subject'], t['body'], 
                                       t['is_html'], t['variables'])
                break
        
        if not template:
            messagebox.showerror("Error", "Template not found")
            return
        
        # Get recipients
        recipients = []
        recipient_type = self.recipient_type_var.get()
        
        if recipient_type == "group":
            group_name = self.recipient_group_var.get()
            recipients = self.db.get_contacts(group_name)
        elif recipient_type == "all":
            recipients = self.db.get_contacts()
        elif recipient_type == "single":
            email = self.recipient_email_var.get().strip()
            if email:
                recipients = [{'name': email.split('@')[0], 'email': email}]
        
        if not recipients:
            messagebox.showerror("Error", "No recipients found")
            return
        
        # Get attachments
        attachments = [self.attachments_list.get(i) for i in range(self.attachments_list.size())]
        
        # Send emails in separate thread
        def send_thread():
            def progress_callback(progress, email, success):
                self.root.after(0, lambda: self.update_send_progress(progress, email, success))
            
            results = self.email_sender.send_bulk_emails(
                self.current_account, self.current_password, recipients, 
                template, attachments, progress_callback
            )
            
            self.root.after(0, lambda: self.send_complete(results))
        
        threading.Thread(target=send_thread, daemon=True).start()
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.progress_var.set("Sending emails...")
    
    def update_send_progress(self, progress, email, success):
        """Update sending progress"""
        self.progress_bar['value'] = progress
        status = "✓" if success else "✗"
        self.progress_var.set(f"Sending to {email} {status}")
        self.root.update_idletasks()
    
    def send_complete(self, results):
        """Handle send completion"""
        self.progress_bar['value'] = 100
        self.progress_var.set(f"Complete: {results['sent']} sent, {results['failed']} failed")
        
        message = f"Email sending complete:\n\nSent: {results['sent']}\nFailed: {results['failed']}"
        if results['errors']:
            message += f"\n\nErrors:\n" + "\n".join(results['errors'][:5])
            if len(results['errors']) > 5:
                message += f"\n... and {len(results['errors']) - 5} more errors"
        
        messagebox.showinfo("Send Complete", message)
        self.refresh_history()
    
    def refresh_data(self):
        """Refresh all data"""
        self.refresh_accounts()
        self.refresh_templates()
        self.refresh_contacts()
    
    def refresh_accounts(self):
        """Refresh accounts list"""
        self.accounts_tree.delete(*self.accounts_tree.get_children())
        
        accounts = self.db.get_email_accounts()
        account_names = []
        
        for account in accounts:
            self.accounts_tree.insert('', tk.END, text=account['name'],
                                    values=(account['email'], account['smtp_server'], account['smtp_port']))
            account_names.append(account['name'])
        
        # Update send account combo
        self.send_account_combo['values'] = account_names
        if account_names and not self.send_account_var.get():
            self.send_account_var.set(account_names[0])
            # Set current account
            for account in accounts:
                if account['name'] == account_names[0]:
                    self.current_account = EmailAccount(
                        account['email'], "", account['smtp_server'], 
                        account['smtp_port'], account.get('imap_server', ''),
                        account['imap_port'], account['use_tls']
                    )
                    break
    
    def refresh_templates(self):
        """Refresh templates list"""
        self.templates_tree.delete(*self.templates_tree.get_children())
        
        templates = self.db.get_templates()
        template_names = []
        
        for template in templates:
            template_type = "HTML" if template['is_html'] else "Text"
            self.templates_tree.insert('', tk.END, text=template['name'],
                                     values=(template['subject'], template_type))
            template_names.append(template['name'])
        
        # Update send template combo
        self.send_template_combo['values'] = template_names
    
    def refresh_contacts(self):
        """Refresh contacts list"""
        self.contacts_tree.delete(*self.contacts_tree.get_children())
        
        contacts = self.db.get_contacts()
        for contact in contacts:
            self.contacts_tree.insert('', tk.END, text=contact['name'],
                                    values=(contact['email'], contact['group_name']))
    
    def refresh_history(self):
        """Refresh email history"""
        # This would query the sent_emails table
        pass
    
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    """Main function"""
    app = EmailGUI()
    app.run()

if __name__ == "__main__":
    main()
