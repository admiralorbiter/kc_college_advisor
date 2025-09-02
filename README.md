# KC College Advisor

A comprehensive web application designed to help students, parents, and advisors explore and compare colleges in the Kansas City metropolitan area. Built with Flask and featuring interactive maps, detailed institution data, and graduation rate analytics.

## 🎯 Project Overview

KC College Advisor is a data-driven platform that provides comprehensive information about higher education institutions in Kansas and Missouri, with a focus on the Kansas City region. The application helps users make informed decisions about college selection by providing detailed statistics, graduation rates, program information, and geographical data.

## ✨ Key Features

### 🏫 Institution Database
- **Comprehensive Coverage**: Detailed information on colleges and universities in MO and KS
- **Rich Data**: Institution details including location, programs, control type, size, and more
- **Search & Filter**: Find institutions by name, location, or specific criteria

### 📊 Analytics & Metrics
- **Graduation Rates**: Track completion rates for different degree programs
- **IPEDS Data**: Integration with federal education statistics
- **Performance Metrics**: Compare institutions based on various success indicators

### 🗺️ Interactive Mapping
- **Geographic Visualization**: Interactive map showing institution locations
- **Location-based Search**: Find colleges near specific areas
- **Distance Calculations**: Calculate travel distances between institutions

### 🎓 Program Information
- **Degree Programs**: Browse available academic programs
- **Completion Data**: Track student success in various fields
- **Enrollment Statistics**: View current and historical enrollment data

### 🔍 Advanced Search & Comparison
- **Multi-criteria Search**: Filter by location, program type, institution size
- **Sorting Options**: Organize results by various metrics
- **Comparison Tools**: Side-by-side institution analysis

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML/CSS with responsive design
- **Mapping**: Folium (Leaflet.js integration)
- **Data Processing**: Pandas for CSV handling
- **Deployment**: Heroku-ready with Gunicorn

## 📁 Project Structure

```
kc_college_advisor/
├── app.py                 # Main Flask application
├── routes.py             # Application routes and logic
├── requirements.txt      # Python dependencies
├── Procfile             # Heroku deployment configuration
├── models/              # Database models
│   ├── institution.py           # Institution data model
│   ├── graduation.py           # Graduation rate models
│   ├── enrollment.py           # Enrollment data models
│   ├── completitions.py        # Program completion models
│   ├── institutional_attributes.py # Additional attributes
│   ├── enums.py                # Data enumeration classes
│   └── classification_codes.py # IPEDS classification codes
├── templates/           # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Landing page
│   ├── colleges.html          # Institution listing
│   ├── map/                   # Interactive map views
│   ├── institutions/          # Institution detail views
│   └── degrees/               # Degree program views
├── static/              # CSS and static assets
│   ├── css/                   # Stylesheets
│   ├── landing-page.css       # Landing page styles
│   └── about-page.css         # About page styles
└── instance/            # Database files
    └── site.db               # SQLite database
```

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kc_college_advisor.git
   cd kc_college_advisor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 📊 Data Sources

The application integrates data from multiple sources:

- **IPEDS (Integrated Postsecondary Education Data System)**: Federal education statistics
- **Institution Self-Reporting**: Direct data from colleges and universities
- **Geographic Data**: Location coordinates and mapping information
- **Classification Codes**: Standardized institution categorization

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///site.db
FLASK_ENV=development
```

### Database Configuration

The application uses SQLite by default. For production, you can modify the database URI in `app.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'your-database-url-here'
```

## 🚀 Deployment

### Heroku Deployment

1. **Install Heroku CLI**
2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

The application includes a `Procfile` for Heroku deployment and uses Gunicorn as the WSGI server.

## 📱 Features in Detail

### Institution Search
- Search by institution name or alias
- Filter by city, state, or county
- Sort results by various criteria
- View detailed institution profiles

### Interactive Map
- Geographic visualization of all institutions
- Click on markers for detailed information
- Distance calculations between locations
- Responsive design for mobile devices

### Graduation Analytics
- Completion rate tracking
- Cohort analysis
- Program-specific success metrics
- Historical trend data

### Data Import/Export
- CSV import functionality for institution data
- Data validation and error handling
- Export capabilities for analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IPEDS**: For comprehensive education data
- **Flask Community**: For the excellent web framework
- **Folium**: For interactive mapping capabilities
- **Kansas City Education Community**: For inspiration and feedback

## 📞 Support

For questions, issues, or contributions, please:

- Open an issue on GitHub
- Contact the development team
- Check the documentation for common solutions

## 🔮 Future Enhancements

- **Mobile App**: Native iOS/Android applications
- **Advanced Analytics**: Machine learning insights
- **Student Portal**: Personalized dashboards
- **Integration APIs**: Connect with other education platforms
- **Real-time Data**: Live updates from institutions

---

**Built with ❤️ for the Kansas City education community**
