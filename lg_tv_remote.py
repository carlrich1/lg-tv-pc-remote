#!/usr/bin/env python3
"""
LG TV Remote Control - Updated Version
- Auto-connects without TV prompt (saves client key)
- Media playback controls (play, pause, stop, rewind, fast-forward)
"""

import asyncio
import json
import sys
import os
from aiowebostv import WebOsClient
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class LGTVRemote:
    def __init__(self):
        self.client = None
        self.connected = False
        self.tv_ip = ""
        self.client_key = None
        
    async def connect_to_tv(self, ip_address, client_key=None):
        """Connect to the LG TV"""
        try:
            self.client = WebOsClient(ip_address, client_key=client_key)
            await self.client.connect()
            self.connected = True
            self.tv_ip = ip_address
            # Store the client key for future use
            self.client_key = self.client.client_key
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def get_client_key(self):
        """Get the client key after successful connection"""
        return self.client_key
    
    async def disconnect(self):
        """Disconnect from TV"""
        if self.client:
            await self.client.disconnect()
            self.connected = False
    
    async def volume_up(self):
        """Increase volume"""
        if self.client:
            await self.client.volume_up()
    
    async def volume_down(self):
        """Decrease volume"""
        if self.client:
            await self.client.volume_down()
    
    async def mute_toggle(self):
        """Toggle mute"""
        if self.client:
            await self.client.set_mute(not await self.client.get_muted())
    
    async def power_off(self):
        """Turn TV off"""
        if self.client:
            await self.client.power_off()
    
    async def launch_app(self, app_id):
        """Launch specific app by ID"""
        if self.client:
            await self.client.launch_app(app_id)
    
    async def nav_up(self):
        """Navigate up"""
        if self.client:
            await self.client.button('UP')
    
    async def nav_down(self):
        """Navigate down"""
        if self.client:
            await self.client.button('DOWN')
    
    async def nav_left(self):
        """Navigate left"""
        if self.client:
            await self.client.button('LEFT')
    
    async def nav_right(self):
        """Navigate right"""
        if self.client:
            await self.client.button('RIGHT')
    
    async def nav_ok(self):
        """Press OK/Enter"""
        if self.client:
            await self.client.button('ENTER')
    
    async def nav_home(self):
        """Go to home screen"""
        if self.client:
            await self.client.button('HOME')
    
    async def nav_back(self):
        """Go back/exit"""
        if self.client:
            await self.client.button('BACK')
    
    # Media control functions
    async def media_play(self):
        """Play"""
        if self.client:
            await self.client.button('PLAY')
    
    async def media_pause(self):
        """Pause"""
        if self.client:
            await self.client.button('PAUSE')
    
    async def media_stop(self):
        """Stop"""
        if self.client:
            await self.client.button('STOP')
    
    async def media_rewind(self):
        """Rewind"""
        if self.client:
            await self.client.button('REWIND')
    
    async def media_fastforward(self):
        """Fast Forward"""
        if self.client:
            await self.client.button('FASTFORWARD')
    
    async def get_apps(self):
        """Get list of installed apps"""
        if self.client:
            apps = await self.client.get_apps()
            return apps
        return []

class TVRemoteGUI:
    def __init__(self):
        self.remote = LGTVRemote()
        self.loop = None
        self.config_file = "tv_remote_config.json"
        self.setup_gui()
        self.load_config()
        self.start_async_loop()
    
    def setup_gui(self):
        """Create the GUI interface"""
        self.root = tk.Tk()
        self.root.title("LG TV Remote Control")
        self.root.geometry("600x800")
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Button style
        button_style = {'font': ('Arial', 10), 'width': 12, 'height': 1}
        
        # Connection frame
        conn_frame = ttk.Frame(self.root)
        conn_frame.pack(pady=10, padx=20, fill='x')
        
        ttk.Label(conn_frame, text="TV IP Address:", font=('Arial', 12)).pack()
        self.ip_entry = ttk.Entry(conn_frame, font=('Arial', 12))
        self.ip_entry.pack(pady=5, fill='x')
        
        self.connect_btn = tk.Button(conn_frame, text="Connect to TV", 
                                   command=self.connect_tv, font=('Arial', 12), width=12, height=1)
        self.connect_btn.pack(pady=5)
        
        self.status_label = ttk.Label(conn_frame, text="Not Connected", 
                                    font=('Arial', 10), foreground='red')
        self.status_label.pack()
        
        # Navigation section
        nav_section = ttk.Frame(self.root)
        nav_section.pack(pady=10)
        
        # Left side: Home and Back
        left_nav = ttk.Frame(nav_section)
        left_nav.pack(side='left', padx=5)
        
        tk.Button(left_nav, text="Home", command=self.nav_home, bg='lightblue', **button_style).pack(pady=2)
        tk.Button(left_nav, text="Back", command=self.nav_back, bg='lightcoral', **button_style).pack(pady=2)
        
        # Center: Arrow navigation
        center_nav = ttk.Frame(nav_section)
        center_nav.pack(side='left', padx=10)
        
        # Create navigation cross
        nav_grid = ttk.Frame(center_nav)
        nav_grid.pack()
        
        tk.Button(nav_grid, text="▲", command=self.nav_up, **button_style).grid(row=0, column=1, padx=2, pady=2)
        tk.Button(nav_grid, text="◄", command=self.nav_left, **button_style).grid(row=1, column=0, padx=2, pady=2)
        tk.Button(nav_grid, text="OK", command=self.nav_ok, bg='lightgreen', **button_style).grid(row=1, column=1, padx=2, pady=2)
        tk.Button(nav_grid, text="►", command=self.nav_right, **button_style).grid(row=1, column=2, padx=2, pady=2)
        tk.Button(nav_grid, text="▼", command=self.nav_down, **button_style).grid(row=2, column=1, padx=2, pady=2)
        
        # Right side: Volume controls
        right_nav = ttk.Frame(nav_section)
        right_nav.pack(side='left', padx=5)
        
        tk.Button(right_nav, text="Vol +", command=self.volume_up, **button_style).pack(pady=2)
        tk.Button(right_nav, text="Vol -", command=self.volume_down, **button_style).pack(pady=2)
        tk.Button(right_nav, text="Mute", command=self.mute_toggle, **button_style).pack(pady=2)
        
        # Media Controls section - NEW
        media_section = ttk.Frame(self.root)
        media_section.pack(pady=10)
        
        ttk.Label(media_section, text="Media Controls", font=('Arial', 12, 'bold')).pack()
        
        media_buttons = ttk.Frame(media_section)
        media_buttons.pack(pady=5)
        
        media_button_style = {'font': ('Arial', 10), 'width': 8, 'height': 1}
        
        tk.Button(media_buttons, text="⏪", command=self.media_rewind, 
                 bg='#4a4a4a', fg='white', **media_button_style).pack(side='left', padx=3)
        tk.Button(media_buttons, text="▶", command=self.media_play, 
                 bg='#228B22', fg='white', **media_button_style).pack(side='left', padx=3)
        tk.Button(media_buttons, text="⏸", command=self.media_pause, 
                 bg='#FF8C00', fg='white', **media_button_style).pack(side='left', padx=3)
        tk.Button(media_buttons, text="⏹", command=self.media_stop, 
                 bg='#DC143C', fg='white', **media_button_style).pack(side='left', padx=3)
        tk.Button(media_buttons, text="⏩", command=self.media_fastforward, 
                 bg='#4a4a4a', fg='white', **media_button_style).pack(side='left', padx=3)
        
        # Apps section
        apps_section = ttk.Frame(self.root)
        apps_section.pack(pady=15, fill='x', padx=20)
        
        ttk.Label(apps_section, text="Quick Launch Apps", font=('Arial', 14, 'bold')).pack()
        
        # Create app buttons in simple rows
        app_button_style = {'font': ('Arial', 10), 'width': 10, 'height': 1}
        
        # Row 1
        row1 = ttk.Frame(apps_section)
        row1.pack(pady=5)
        tk.Button(row1, text="Netflix", command=lambda: self.launch_app_smart("Netflix"), 
                 bg='#E50914', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row1, text="YouTube", command=lambda: self.launch_app_smart("YouTube"), 
                 bg='#FF0000', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Row 2
        row2 = ttk.Frame(apps_section)
        row2.pack(pady=5)
        tk.Button(row2, text="Prime Video", command=lambda: self.launch_app_smart("Prime Video"), 
                 bg='#00A8E1', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row2, text="Disney+", command=lambda: self.launch_app_smart("Disney+"), 
                 bg='#113CCF', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Row 3
        row3 = ttk.Frame(apps_section)
        row3.pack(pady=5)
        tk.Button(row3, text="Hulu", command=lambda: self.launch_app_smart("Hulu"), 
                 bg='#1CE783', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row3, text="Apple TV", command=lambda: self.launch_app_smart("Apple TV"), 
                 bg='#000000', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Row 4
        row4 = ttk.Frame(apps_section)
        row4.pack(pady=5)
        tk.Button(row4, text="HBO Max", command=lambda: self.launch_app_smart("HBO Max"), 
                 bg='#673AB7', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row4, text="Peacock", command=lambda: self.launch_app_smart("Peacock"), 
                 bg='#00B4D8', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Row 5
        row5 = ttk.Frame(apps_section)
        row5.pack(pady=5)
        tk.Button(row5, text="ESPN", command=lambda: self.launch_app_smart("ESPN"), 
                 bg='#D22630', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row5, text="Food Network", command=lambda: self.launch_app_smart("Food Network"), 
                 bg='#E67E22', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Row 6
        row6 = ttk.Frame(apps_section)
        row6.pack(pady=5)
        tk.Button(row6, text="Paramount+", command=lambda: self.launch_app_smart("Paramount+"), 
                 bg='#0033A0', fg='white', **app_button_style).pack(side='left', padx=5)
        tk.Button(row6, text="Power Off", command=self.power_off, 
                 bg='red', fg='white', **app_button_style).pack(side='left', padx=5)
        
        # Bottom controls
        bottom_frame = ttk.Frame(apps_section)
        bottom_frame.pack(pady=10, fill='x')
        
        tk.Button(bottom_frame, text="Refresh App List", command=self.refresh_apps, 
                 font=('Arial', 10), width=15).pack()
        
        self.apps_listbox = tk.Listbox(bottom_frame, font=('Arial', 9), height=3)
        self.apps_listbox.pack(fill='x', pady=5)
        self.apps_listbox.bind('<Double-Button-1>', self.launch_selected_app)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
    def start_async_loop(self):
        """Start the asyncio event loop in a separate thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        thread = threading.Thread(target=run_loop, daemon=True)
        thread.start()
        time.sleep(0.1)
    
    def run_async(self, coro):
        """Run an async function from the GUI thread"""
        if self.loop:
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            try:
                return future.result(timeout=10)
            except Exception as e:
                self.update_status(f"Error: {e}")
                return None
    
    def save_config(self):
        """Save IP address and client key to config file"""
        try:
            config = {
                "tv_ip": self.ip_entry.get(),
                "client_key": self.remote.get_client_key()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def load_config(self):
        """Load IP address and client key from config file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.ip_entry.insert(0, config.get("tv_ip", "192.168.1.100"))
                self.saved_client_key = config.get("client_key", None)
        except:
            self.ip_entry.insert(0, "192.168.1.100")
            self.saved_client_key = None
    
    def connect_tv(self):
        """Connect to the TV"""
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Error", "Please enter TV IP address")
            return
        
        self.update_status("Connecting...")
        self.connect_btn.config(state='disabled')
        
        def connect():
            # Try to connect with saved client key first
            client_key = getattr(self, 'saved_client_key', None)
            success = self.run_async(self.remote.connect_to_tv(ip, client_key=client_key))
            if success:
                self.status_label.config(text=f"Connected to {ip}", foreground='green')
                self.update_status("Connected successfully")
                # Save the config with the client key
                self.save_config()
                self.refresh_apps()
            else:
                self.status_label.config(text="Connection Failed", foreground='red')
                self.update_status("Connection failed")
            self.connect_btn.config(state='normal')
        
        threading.Thread(target=connect, daemon=True).start()
    
    def launch_app_smart(self, app_name):
        """Smart app launcher - finds app in your TV's list first"""
        def smart_launcher():
            try:
                # First, get the actual app list from your TV
                apps = self.run_async(self.remote.get_apps())
                if apps:
                    # Search for the app by name
                    for app in apps:
                        app_title = app.get('title', '').lower()
                        app_id = app.get('id', '')
                        
                        # Check if the app name matches
                        if app_name.lower() in app_title or app_title in app_name.lower():
                            self.run_async(self.remote.launch_app(app_id))
                            self.update_status(f"Found and launching {app_name}: {app_id}")
                            return
                
                # If not found in list, try the fallback ID
                fallback_ids = {
                    "Netflix": ["netflix"],
                    "YouTube": ["youtube.leanback.v4", "youtube"],
                    "Prime Video": ["amazon", "primevideo"],
                    "Disney+": ["com.disney.disneyplus-prod", "disney"],
                    "Hulu": ["hulu"],
                    "Apple TV": ["com.apple.appletv", "appletv"],
                    "HBO Max": ["com.hbo.hbonow", "hbomax", "com.hbo.max"],
                    "Peacock": ["com.peacocktv.peacocktv", "peacock", "com.peacocktv"],
                    "ESPN": ["espn", "com.espn.webostv", "com.espn.app"],
                    "Food Network": ["com.scripts.foodnetwork", "foodnetwork", "com.foodnetwork"],
                    "Paramount+": ["com.cbs.app", "paramountplus", "com.paramount"]
                }
                
                if app_name in fallback_ids:
                    for app_id in fallback_ids[app_name]:
                        try:
                            self.run_async(self.remote.launch_app(app_id))
                            self.update_status(f"Trying {app_name} with ID: {app_id}")
                            time.sleep(0.5)
                        except:
                            continue
                else:
                    self.update_status(f"Could not find {app_name}")
                            
            except Exception as e:
                self.update_status(f"Error launching {app_name}: {e}")
        
        threading.Thread(target=smart_launcher, daemon=True).start()
    
    def launch_espn(self):
        """Special ESPN launcher - tries multiple IDs"""
        def try_espn():
            espn_ids = ["espn", "com.espn.webostv", "com.espn.app", "ESPN"]
            for espn_id in espn_ids:
                try:
                    self.run_async(self.remote.launch_app(espn_id))
                    self.update_status(f"Trying ESPN: {espn_id}")
                    time.sleep(0.5)
                except:
                    continue
        
        threading.Thread(target=try_espn, daemon=True).start()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    # Navigation functions
    def nav_up(self):
        self.run_async(self.remote.nav_up())
        self.update_status("Navigate up")
    
    def nav_down(self):
        self.run_async(self.remote.nav_down())
        self.update_status("Navigate down")
    
    def nav_left(self):
        self.run_async(self.remote.nav_left())
        self.update_status("Navigate left")
    
    def nav_right(self):
        self.run_async(self.remote.nav_right())
        self.update_status("Navigate right")
    
    def nav_ok(self):
        self.run_async(self.remote.nav_ok())
        self.update_status("OK pressed")
    
    def nav_home(self):
        self.run_async(self.remote.nav_home())
        self.update_status("Home pressed")
    
    def nav_back(self):
        self.run_async(self.remote.nav_back())
        self.update_status("Back pressed")
    
    # Volume functions
    def volume_up(self):
        self.run_async(self.remote.volume_up())
        self.update_status("Volume up")
    
    def volume_down(self):
        self.run_async(self.remote.volume_down())
        self.update_status("Volume down")
    
    def mute_toggle(self):
        self.run_async(self.remote.mute_toggle())
        self.update_status("Mute toggled")
    
    # Media control functions
    def media_play(self):
        self.run_async(self.remote.media_play())
        self.update_status("Play")
    
    def media_pause(self):
        self.run_async(self.remote.media_pause())
        self.update_status("Pause")
    
    def media_stop(self):
        self.run_async(self.remote.media_stop())
        self.update_status("Stop")
    
    def media_rewind(self):
        self.run_async(self.remote.media_rewind())
        self.update_status("Rewind")
    
    def media_fastforward(self):
        self.run_async(self.remote.media_fastforward())
        self.update_status("Fast Forward")
    
    def power_off(self):
        if messagebox.askyesno("Confirm", "Turn off TV?"):
            self.run_async(self.remote.power_off())
            self.update_status("TV powered off")
    
    def refresh_apps(self):
        """Refresh the list of available apps"""
        def get_apps():
            apps = self.run_async(self.remote.get_apps())
            if apps:
                self.apps_listbox.delete(0, tk.END)
                for app in apps:
                    self.apps_listbox.insert(tk.END, app.get('title', app.get('id', 'Unknown')))
                self.update_status(f"Found {len(apps)} apps")
        
        threading.Thread(target=get_apps, daemon=True).start()
    
    def launch_selected_app(self, event):
        """Launch app selected from list"""
        selection = self.apps_listbox.curselection()
        if selection:
            app_name = self.apps_listbox.get(selection[0])
            # Simple approach - just try the app name as ID
            self.launch_app(app_name.lower().replace(" ", ""))
    
    def run(self):
        """Start the GUI"""
        try:
            self.root.mainloop()
        finally:
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)

def main():
    print("LG TV Remote Control - Updated Version")
    print("======================================")
    
    app = TVRemoteGUI()
    app.run()

if __name__ == "__main__":
    main()
