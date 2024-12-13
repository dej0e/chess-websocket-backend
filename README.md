Step-by-Step Guide to Run the FastAPI Backend and React Frontend

If you have Python and Node.js already installed, skip to step 3.
----------------------------------------------------------------------------------

1. Installing Python
For Windows:
-- 1. Download Python from the official website: https://www.python.org/downloads/
-- 2. Run the installer and check "Add Python to PATH" during installation.
-- 3. Verify the installation:
   ```
   python --version
   ```
For Linux/Mac:
-- 1. Open a terminal and install Python:
   - Linux:
     ```
     sudo apt update
     sudo apt install python3 python3-pip
     ```
   - Mac (using Homebrew):
     ```
     brew install python
     ```
-- 2. Verify the installation:
   ```
   python3 --version
   ```

----------------------------------------------------------------------------------


2. Installing Node.js

For Windows:
-- 1. Download Node.js from the official website: https://nodejs.org/
-- 2. Choose the LTS version and follow the installation steps.
-- 3. Verify the installation:
   ```
   node --version
   npm --version
   ```

For Linux/Mac:
-- 1. Install Node.js:
   - **Linux**:
     ```
     sudo apt update
     sudo apt install nodejs npm
     ```
   - Mac (using Homebrew):
     ```
     brew install node
     ```
-- 2. Verify the installation:
   ```
   node --version
   npm --version
   ```

----------------------------------------------------------------------------------

3. Setting Up the FastAPI Backend

-- 1. Navigate to the backend directory:
   ```
   cd /path/to/chess-websocket-backend-master
   ```

-- 2. Create a virtual environment:
   ```
   python -m venv venv
   ```

-- 3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source venv/bin/activate
     ```

-- 4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

-- 5. Start the FastAPI server:
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

----------------------------------------------------------------------------------

4. Setting Up the React Frontend

-- 1. Navigate to the frontend directory:
   ```
   cd /path/to/chess-frontend-master
   ```

-- 2. Install dependencies:
   ```
   npm install
   ```

-- 3. Start the development server:
   ```
   npm start
   ```

----------------------------------------------------------------------------------

5. Verifying the Setup
-- Open your browser and navigate to:
   `http://localhost:3000`
-- Interact with the frontend and test its communication with the backend.

----------------------------------------------------------------------------------

6. Troubleshooting
-- Node.js or Python Not Found:
   Ensure both are installed and added to your system's PATH.

-- Permission Errors:
   Use `sudo` (Linux/Mac) or run your terminal as Administrator (Windows).
