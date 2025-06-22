# Graph Coloring Course Scheduling System

A Flask-based web application that uses graph coloring algorithms to automatically generate course schedules while avoiding conflicts.

## Features

- **Course Management**: Add and delete courses
- **Student Management**: Add and manage students
- **Enrollment System**: Enroll students in courses
- **Conflict Detection**: Automatically detect scheduling conflicts
- **Schedule Generation**: Use DSatur graph coloring algorithm to generate optimal schedules
- **Visual Schedule Display**: View generated schedules organized by time slots

## Setup Instructions

### Prerequisites

1. **Python 3.7+**
2. **Neo4j Database** (version 4.4+ or 5.x)
3. **pip** (Python package manager)

### Installation

1. **Clone or download the project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Neo4j Database**:
   - Install Neo4j Desktop or Neo4j Community Edition
   - Create a new database
   - Note down your database URI, username, and password

4. **Configure environment variables** (optional):
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="your_password"
   ```

   Or modify the default values in `app.py`:
   ```python
   NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
   NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
   NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password")
   ```

### Running the Application

1. **Start Neo4j Database**

2. **Run the Flask application**:
   ```bash
   python app.py
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:5001
   ```

## Usage

1. **Add Courses**: Go to the "Mata Kuliah" page and add courses
2. **Add Students**: Go to the "Mahasiswa" page and add students
3. **Enroll Students**: Go to the "Enrollment" page to enroll students in courses
4. **Generate Schedule**: Go to the "Generate" page to run the graph coloring algorithm
5. **View Schedule**: Go to the "Jadwal" page to see the generated schedule

## Technical Details

### Graph Coloring Algorithm

The application uses the **DSatur (Degree of Saturation)** algorithm to color the conflict graph:

1. **Conflict Detection**: Identifies courses that have students in common
2. **Graph Construction**: Creates a graph where nodes represent courses and edges represent conflicts
3. **Coloring**: Uses DSatur to assign colors (time slots) to courses while minimizing conflicts
4. **Schedule Generation**: Converts colors to time slots for the final schedule

### Database Schema

- **Course**: `{id, name, color, time_slot}`
- **Student**: `{id, name}`
- **ENROLLED_IN**: Relationship between Student and Course
- **HAS_CONFLICT**: Relationship between conflicting Courses

## Troubleshooting

### BuildError: Could not build url for endpoint 'delete_course'

This error was fixed by:

1. **Replacing APOC UUID generation** with Python's `uuid.uuid4()`
2. **Adding null ID cleanup** to remove courses/students without proper IDs
3. **Adding template validation** to check for null IDs before building URLs

### Common Issues

1. **Neo4j Connection Error**: Make sure Neo4j is running and credentials are correct
2. **Port Already in Use**: Change the port in `app.py` if 5001 is occupied
3. **Missing Dependencies**: Run `pip install -r requirements.txt`

## API Endpoints

- `GET /` - Dashboard
- `GET/POST /courses` - Course management
- `POST /course/delete/<id>` - Delete course
- `GET/POST /students` - Student management
- `GET/POST /enroll` - Enrollment management
- `GET/POST /generate` - Schedule generation
- `GET /schedule` - View schedule
- `POST /detect-conflicts` - Detect conflicts (AJAX)

## License

This project is for educational purposes. Feel free to use and modify as needed. 