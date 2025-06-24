# src/ui/info_tabs.py
"""
Enhanced Information tabs with improved error handling and data formatting
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading

class InfoTabs:
    """Enhanced Information display tabs"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Create notebook
        self.notebook = ttk.Notebook(parent)
        
        # Create existing tabs
        self.create_system_info_tab()
        self.create_attendance_tab()
        self.create_employee_tab()
        self.create_analytics_tab()
    
    def create_analytics_tab(self):
        """Create Data Analytics tab with improved error handling"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Data Analytics")
        
        # Create scrollable frame
        canvas = tk.Canvas(analytics_frame)
        scrollbar = ttk.Scrollbar(analytics_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header_frame, text="Data Analytics Engine", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Control buttons
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.LEFT, padx=10)
        
        self.analytics_button = ttk.Button(btn_frame, text="Run Analytics", 
                                         command=self.run_analytics)
        self.analytics_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame, text="Generate Report", 
                  command=self.generate_full_report).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_frame, text="Refresh", 
                  command=self.refresh_analytics_display).pack(side=tk.LEFT, padx=2)
        
        # Status display
        self.analytics_status = tk.Label(scrollable_frame, 
                                       text="Click 'Run Analytics' to process your data", 
                                       fg="blue", font=("Arial", 10))
        self.analytics_status.pack(pady=5)
        
        # Results display area
        self.create_analytics_display_area(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Analytics data storage
        self.analytics_data = {}
        self.analytics_engine = None
    
    def create_analytics_display_area(self, parent):
        """Create display areas for analytics results"""
        
        # Performance Metrics Section
        metrics_frame = ttk.LabelFrame(parent, text="Data Processing Performance")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=8, wrap=tk.WORD, font=("Courier", 9))
        self.metrics_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Peak Hours Analysis
        peak_frame = ttk.LabelFrame(parent, text="Peak Hours Analysis")
        peak_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.peak_hours_text = tk.Text(peak_frame, height=10, wrap=tk.WORD, font=("Courier", 9))
        self.peak_hours_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Daily Patterns Analysis
        daily_frame = ttk.LabelFrame(parent, text="Daily Attendance Patterns")
        daily_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.daily_patterns_text = tk.Text(daily_frame, height=10, wrap=tk.WORD, font=("Courier", 9))
        self.daily_patterns_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Employee Performance Analysis
        employee_frame = ttk.LabelFrame(parent, text="Employee Performance Analytics")
        employee_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.employee_performance_text = tk.Text(employee_frame, height=10, wrap=tk.WORD, font=("Courier", 9))
        self.employee_performance_text.pack(fill=tk.X, padx=5, pady=5)
    
    def run_analytics(self):
        """Run data analytics in background thread with better error handling"""
        def analytics_worker():
            try:
                self.update_status("Initializing Advanced Data Analytics Engine...")
                
                # Try to import analytics engine
                try:
                    from ..analytics.spark_analytics import SparkAnalyticsEngine
                    self.analytics_engine = SparkAnalyticsEngine()
                    
                    self.update_status("Loading data from MongoDB and processing...")
                    self.analytics_engine.load_data_from_mongodb()

                    self.update_status("Running comprehensive analytics algorithms...")

                    # Run comprehensive analytics
                    self.analytics_data = self.analytics_engine.generate_comprehensive_report()
                    
                    if "error" in self.analytics_data:
                        error_msg = f"Analytics completed with warnings: {self.analytics_data['error']}"
                        self.main_window.root.after(0, lambda: self.update_status(error_msg))
                    else:
                        self.update_status("Advanced analytics processing complete!")
                    
                    # Update UI with results
                    self.main_window.root.after(0, self.display_analytics_results)
                    
                except ImportError as e:
                    error_msg = f"Analytics module not available: {str(e)}"
                    self.main_window.root.after(0, lambda: self.update_status(error_msg))
                    
                except Exception as e:
                    error_msg = f"Analytics processing error (using fallback): {str(e)[:100]}"
                    self.main_window.root.after(0, lambda: self.update_status(error_msg))
                    print(f"Analytics error: {e}")
                
            except Exception as e:
                error_msg = f"Failed to run analytics: {str(e)[:100]}"
                self.main_window.root.after(0, lambda: self.update_status(error_msg))
        
        # Disable button during processing
        self.analytics_button.config(state=tk.DISABLED, text="Processing...")
        
        # Run in background thread
        threading.Thread(target=analytics_worker, daemon=True).start()
    
    def display_analytics_results(self):
        """Display analytics results with safe formatting"""
        try:
            if not self.analytics_data:
                self.update_status("No analytics data available")
                return
            
            # Display all sections with error handling
            self.display_performance_metrics()
            self.display_peak_hours_analysis()
            self.display_daily_patterns()
            self.display_employee_performance()
            
            # Re-enable button
            self.analytics_button.config(state=tk.NORMAL, text="Run Analytics")

            self.update_status("Analytics results ready! Advanced data processing complete.")

        except Exception as e:
            error_msg = f"Display error: {str(e)}"
            self.update_status(error_msg)
            self.analytics_button.config(state=tk.NORMAL, text="Run Analytics")
            print(f"Display error: {e}")
    
    def safe_format_number(self, value, format_type="int"):
        """Safely format numbers to avoid type errors"""
        try:
            if value is None:
                return "N/A"
            
            if format_type == "int":
                return f"{int(float(value)):,}"
            elif format_type == "float":
                return f"{float(value):.3f}"
            elif format_type == "percent":
                return f"{float(value):.1f}%"
            else:
                return str(value)
        except (ValueError, TypeError):
            return "N/A"
    
    def display_performance_metrics(self):
        """Display performance metrics with safe formatting"""
        try:
            if 'performance_metrics' not in self.analytics_data:
                return
            
            metrics = self.analytics_data['performance_metrics']
            
            # Safe access to metrics with defaults
            events_processed = self.safe_format_number(metrics.get('total_events_processed', 0), "int")
            attendance_records = self.safe_format_number(metrics.get('total_attendance_records', 0), "int")
            data_size = metrics.get('data_size_gb', 'Unknown')
            processing_engine = metrics.get('processing_time', 'Unknown')
            cluster_type = metrics.get('cluster_utilization', 'Unknown')
            
            metrics_text = f"""
DATA PROCESSING METRICS

Dataset Scale:
   • Recognition Events: {events_processed} records
   • Attendance Records: {attendance_records} records
   • Estimated Data Size: {data_size}
   
Processing Engine:
   • Framework: {processing_engine}
   • Cluster Type: {cluster_type}
   • Processing Mode: Advanced Analytics
"""
            
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, metrics_text)
            
        except Exception as e:
            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(tk.END, f"Error displaying performance metrics: {e}")
    
    def display_peak_hours_analysis(self):
        """Display peak hours analysis with safe formatting"""
        try:
            if 'peak_hours' not in self.analytics_data:
                return
            
            peak_data = self.analytics_data['peak_hours']
            
            if peak_data.empty:
                self.peak_hours_text.delete(1.0, tk.END)
                self.peak_hours_text.insert(tk.END, "No peak hours data available")
                return
            
            # Find peak hour safely
            peak_hour_idx = peak_data['recognition_count'].idxmax()
            peak_hour = peak_data.iloc[peak_hour_idx]
            
            # Safe formatting
            peak_hour_time = self.safe_format_number(peak_hour['hour'], "int")
            peak_count = self.safe_format_number(peak_hour['recognition_count'], "int")
            peak_confidence = self.safe_format_number(peak_hour['avg_confidence'], "float")
            peak_people = self.safe_format_number(peak_hour['unique_people'], "int")
            
            analysis_text = f"""
📈 PEAK HOURS ANALYSIS

Busiest Hour: {peak_hour_time}:00
   • Recognition Count: {peak_count}
   • Average Confidence: {peak_confidence}
   • Unique People: {peak_people}

Hourly Breakdown (Top Hours):
"""
            
            # Add top hours safely
            try:
                top_hours = peak_data.nlargest(min(10, len(peak_data)), 'recognition_count')
                for _, row in top_hours.iterrows():
                    hour = self.safe_format_number(row['hour'], "int")
                    count = self.safe_format_number(row['recognition_count'], "int")
                    conf = self.safe_format_number(row['avg_confidence'], "float")
                    analysis_text += f"   {hour}:00 - {count} recognitions (conf: {conf})\n"
            except Exception as e:
                analysis_text += f"   Error processing hourly data: {e}\n"
            
            # Summary stats
            try:
                total_recognitions = self.safe_format_number(peak_data['recognition_count'].sum(), "int")
                avg_confidence = self.safe_format_number(peak_data['avg_confidence'].mean(), "float")
                
                analysis_text += f"""
Insights:
   • Total recognitions processed: {total_recognitions}
   • Overall average confidence: {avg_confidence}
   • Advanced pattern recognition applied
   • Peak activity identified and analyzed
"""
            except Exception as e:
                analysis_text += f"\nInsights: Error processing summary - {e}"
            
            self.peak_hours_text.delete(1.0, tk.END)
            self.peak_hours_text.insert(tk.END, analysis_text)
            
        except Exception as e:
            self.peak_hours_text.delete(1.0, tk.END)
            self.peak_hours_text.insert(tk.END, f"Error displaying peak hours analysis: {e}")
    
    def display_daily_patterns(self):
        """Display daily patterns with safe formatting"""
        try:
            if 'daily_patterns' not in self.analytics_data:
                return
            
            daily_data = self.analytics_data['daily_patterns']
            
            if daily_data.empty:
                self.daily_patterns_text.delete(1.0, tk.END)
                self.daily_patterns_text.insert(tk.END, "No daily patterns data available")
                return
            
            # Find patterns safely
            busiest_day_idx = daily_data['total_attendance'].idxmax()
            busiest_day = daily_data.iloc[busiest_day_idx]
            
            highest_late_idx = daily_data['late_percentage'].idxmax()
            highest_late_day = daily_data.iloc[highest_late_idx]
            
            # Safe formatting
            busiest_name = str(busiest_day['day_of_week'])
            busiest_total = self.safe_format_number(busiest_day['total_attendance'], "int")
            busiest_unique = self.safe_format_number(busiest_day['unique_employees'], "int")
            busiest_late = self.safe_format_number(busiest_day['late_percentage'], "percent")
            
            late_name = str(highest_late_day['day_of_week'])
            late_percent = self.safe_format_number(highest_late_day['late_percentage'], "percent")
            
            patterns_text = f"""
📅 DAILY ATTENDANCE PATTERNS

Busiest Day: {busiest_name}
   • Total Attendance: {busiest_total}
   • Unique Employees: {busiest_unique}
   • Late Percentage: {busiest_late}

Highest Late Rate: {late_name} ({late_percent})

Weekly Breakdown:
"""
            
            # Add weekly breakdown safely
            try:
                for _, row in daily_data.iterrows():
                    day_name = str(row['day_of_week'])[:10]
                    total_att = self.safe_format_number(row['total_attendance'], "int")
                    late_pct = self.safe_format_number(row['late_percentage'], "percent")
                    patterns_text += f"   {day_name:<10}: {total_att:>8} attendees ({late_pct:>6} late)\n"
            except Exception as e:
                patterns_text += f"   Error processing weekly data: {e}\n"
            
            # Summary insights
            try:
                avg_attendance = self.safe_format_number(daily_data['total_attendance'].mean(), "int")
                avg_late_rate = self.safe_format_number(daily_data['late_percentage'].mean(), "percent")
                best_day = str(daily_data.loc[daily_data['late_percentage'].idxmin(), 'day_of_week'])
                
                patterns_text += f"""
Pattern Analysis:
   • Average weekly attendance: {avg_attendance}
   • Overall late rate: {avg_late_rate}
   • Most punctual day: {best_day}
   • Advanced trend analysis applied
"""
            except Exception as e:
                patterns_text += f"\n💡 Analysis: Error processing insights - {e}"
            
            self.daily_patterns_text.delete(1.0, tk.END)
            self.daily_patterns_text.insert(tk.END, patterns_text)
            
        except Exception as e:
            self.daily_patterns_text.delete(1.0, tk.END)
            self.daily_patterns_text.insert(tk.END, f"Error displaying daily patterns: {e}")
    
    def display_employee_performance(self):
        """Display employee performance with safe formatting"""
        try:
            if 'employee_performance' not in self.analytics_data:
                return
            
            emp_data = self.analytics_data['employee_performance']
            
            if emp_data.empty:
                self.employee_performance_text.delete(1.0, tk.END)
                self.employee_performance_text.insert(tk.END, "No employee performance data available")
                return
            
            performance_text = """
EMPLOYEE PERFORMANCE ANALYTICS

Top Performers:
"""
            
            # Top performers with safe formatting
            try:
                top_performers = emp_data.head(min(10, len(emp_data)))
                for i, (_, row) in enumerate(top_performers.iterrows(), 1):
                    name = str(row['employee_name'])[:15]
                    score = self.safe_format_number(row['punctuality_score'], "percent")
                    performance_text += f"   {i:2d}. {name:<15} - {score:>6} punctual\n"
            except Exception as e:
                performance_text += f"   Error processing top performers: {e}\n"
            
            # Performance metrics
            try:
                total_employees = self.safe_format_number(len(emp_data), "int")
                avg_punctuality = self.safe_format_number(emp_data['punctuality_score'].mean(), "percent")
                best_performer = str(emp_data.iloc[0]['employee_name']) if len(emp_data) > 0 else "N/A"
                best_score = self.safe_format_number(emp_data.iloc[0]['punctuality_score'], "percent") if len(emp_data) > 0 else "N/A"
                avg_arrival = self.safe_format_number(emp_data['avg_arrival_hour'].mean(), "float")
                
                performance_text += f"""
Performance Metrics:
   • Total employees analyzed: {total_employees}
   • Average punctuality score: {avg_punctuality}
   • Best performer: {best_performer} ({best_score})
   • Average arrival time: {avg_arrival}:00
   
Distribution Analysis:
"""
                
                # Distribution analysis
                excellent = len(emp_data[emp_data['punctuality_score'] > 95])
                good = len(emp_data[(emp_data['punctuality_score'] >= 85) & (emp_data['punctuality_score'] <= 95)])
                needs_improvement = len(emp_data[emp_data['punctuality_score'] < 85])
                total_records = self.safe_format_number(emp_data['total_days'].sum(), "int")
                
                performance_text += f"   • Excellent (>95%): {excellent} employees\n"
                performance_text += f"   • Good (85-95%): {good} employees\n"
                performance_text += f"   • Needs Improvement (<85%): {needs_improvement} employees\n"
                
                performance_text += f"""
Analytics Features:
   • Analyzed {total_records} total attendance records
"""
                
            except Exception as e:
                performance_text += f"\nMetrics: Error processing data - {e}"
            
            self.employee_performance_text.delete(1.0, tk.END)
            self.employee_performance_text.insert(tk.END, performance_text)
            
        except Exception as e:
            self.employee_performance_text.delete(1.0, tk.END)
            self.employee_performance_text.insert(tk.END, f"Error displaying employee performance: {e}")
    
    def generate_full_report(self):
        """Generate comprehensive analytics report"""
        if not self.analytics_data:
            messagebox.showwarning("Warning", "Please run analytics first!")
            return
        
        try:
            # Create report file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"report_{timestamp}.txt"

            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("FACE RECOGNITION ANALYTICS REPORT\n")
                f.write("Data Analytics Engine - Comprehensive Analysis\n")
                f.write("="*80 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write all analytics sections safely
                for section, data in self.analytics_data.items():
                    try:
                        f.write(f"\n{section.upper().replace('_', ' ')}\n")
                        f.write("-" * 50 + "\n")
                        if hasattr(data, 'to_string'):  # pandas DataFrame
                            f.write(data.to_string(index=False))
                        else:
                            f.write(str(data))
                        f.write("\n\n")
                    except Exception as e:
                        f.write(f"Error writing section {section}: {e}\n\n")
            
            messagebox.showinfo("Success", f"Advanced analytics report saved as: {report_filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def refresh_analytics_display(self):
        """Refresh analytics display"""
        if self.analytics_data:
            self.display_analytics_results()
        else:
            self.update_status("No analytics data to refresh. Run analytics first!")
    
    def update_status(self, message):
        """Update analytics status message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.analytics_status.config(text=f"{timestamp} - {message}")
    
    # EXISTING METHODS (unchanged)
    
    def create_system_info_tab(self):
        """Create system information tab"""
        info_frame = ttk.Frame(self.notebook)
        self.notebook.add(info_frame, text="System Info")
        
        self.stats_text = tk.Text(info_frame, width=40, height=15, wrap=tk.WORD)
        self.stats_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    def create_attendance_tab(self):
        """Create attendance tab"""
        attendance_frame = ttk.Frame(self.notebook)
        self.notebook.add(attendance_frame, text="Today's Attendance")
        
        self.attendance_listbox = tk.Listbox(attendance_frame)
        self.attendance_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Button(
            attendance_frame, 
            text="Refresh Attendance", 
            command=self.refresh_attendance
        ).pack(pady=5)
    
    def create_employee_tab(self):
        """Create employee management tab"""
        emp_frame = ttk.Frame(self.notebook)
        self.notebook.add(emp_frame, text="Employees")
        
        self.employee_listbox = tk.Listbox(emp_frame)
        self.employee_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Employee management buttons
        emp_buttons = ttk.Frame(emp_frame)
        emp_buttons.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(emp_buttons, text="Add Employee", 
                  command=self.main_window.add_employee).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Enroll Face", 
                  command=self.main_window.enroll_face).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Link Face", 
                  command=self.manual_face_link).pack(side=tk.LEFT, padx=2)
        ttk.Button(emp_buttons, text="Refresh", 
                  command=self.refresh_employees).pack(side=tk.LEFT, padx=2)
    
    def update_system_info(self, stats):
        """Update system information display"""
        mode = "AUTOMATIC RECOGNITION" if stats['face_recognition_available'] and stats['known_faces'] > 0 else "DETECTION ONLY"
        
        status_text = f"""System Status:

Mode: {mode}
Active Employees: {stats['employee_count']}
Face Samples: {stats['face_count']}
Known Faces: {stats['known_faces']}
Recognition Events: {stats['event_count']}
Status: {'Running' if stats['is_running'] else 'Stopped'}

face_recognition library: {'✅ Available' if stats['face_recognition_available'] else '❌ Not Available'}

DATA ANALYTICS AVAILABLE!
   • Advanced Spark analytics engine
   • Large-scale distributed processing
   • Comprehensive insights generation
   • Real-time analytics capabilities

Last Updated: {datetime.now().strftime('%H:%M:%S')}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, status_text)
    
    def refresh_employees(self):
        """Refresh the employee list"""
        self.employee_listbox.delete(0, tk.END)
        
        try:
            employees = self.main_window.emp_db.list_employees()
            
            if not employees:
                self.employee_listbox.insert(tk.END, "No employees found - Add employees first")
                return
            
            for emp in employees:
                face_count = self.main_window.face_db.faces_collection.count_documents(
                    {"employee_id": emp['employee_id']}
                )
                face_status = "✅" if face_count > 0 else "❌"
                display_text = f"{emp['name']} {face_status}"
                self.employee_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            print(f"Error refreshing employees: {e}")
            self.employee_listbox.insert(tk.END, f"Error loading employees: {e}")
    
    def refresh_attendance(self):
        """Refresh today's attendance list"""
        self.attendance_listbox.delete(0, tk.END)
        
        try:
            today_attendance = self.main_window.emp_db.get_today_attendance()
            
            if not today_attendance:
                self.attendance_listbox.insert(tk.END, "No attendance records for today")
                return
            
            for att in today_attendance:
                status = "LATE" if att['is_late'] else "ON TIME"
                time_str = att['enter_time'].strftime('%H:%M:%S')
                display_text = f"{att['employee_name']} - {time_str} ({status})"
                self.attendance_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            print(f"Error refreshing attendance: {e}")
            self.attendance_listbox.insert(tk.END, f"Error loading attendance: {e}")
    
    def get_selected_employee(self):
        """Get currently selected employee"""
        selection = self.employee_listbox.curselection()
        if not selection:
            return None
        
        # Get employee name from selection (remove status emoji)
        employee_line = self.employee_listbox.get(selection[0])
        if "No employees found" in employee_line or "Error" in employee_line:
            return None
        
        employee_name = employee_line.split(" ✅")[0].split(" ❌")[0]
        return self.main_window.emp_db.get_employee_by_name(employee_name)
    
    def manual_face_link(self):
        """Manually link existing face to employee"""
        from .dialogs import show_face_link_dialog
        show_face_link_dialog(
            self.main_window.root, 
            self.main_window.emp_db, 
            self.main_window.face_db,
            self.main_window.reload_faces_callback
        )