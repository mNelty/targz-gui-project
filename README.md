⚠️ Important note: This project is currently in development, some features might not work as expected. It's not recommended for normal use, as long as this warning is present. Unless you want to contribute or try new things, it's not recommended.

# 📚 LibRARy: Linux Source Code Installation Automation
**(Meaning: Library of RAndom Repository "y")**
​LibRARy is a Graphical User Interface (GUI) application designed to automate, simplify, and secure the process of installing software from source code (.tar.gz files) on Linux distributions, especially for new users. Say goodbye to complex, manual terminal commands like ./configure, make, and hunting down dependencies!
- ​The project is developed using Python and PyQt5.
### 🌟 Key Features
​LibRARy tackles the three most challenging steps of source code installation within a single interface:

​1. Smart Installation Automation (LibRARy Core)
​Standard Detection: The application automatically detects the underlying installation standard (e.g., ./configure from Autotools, CMakeLists.txt, or setup.py) within the dropped .tar.gz file.
​Compilation Flow: It sequentially executes the commands appropriate for the detected standard (configure, make) without requiring manual intervention.
​Secure File Tracking (DESTDIR): It utilizes the DESTDIR environment variable to safely redirect the make install process to a temporary, isolated directory. This allows the system to accurately track and record the list of installed files without requiring root (sudo) permissions during the critical installation phase.

​2. Intelligent Dependency Management
​Error Trapping: The application captures and analyzes compilation errors (e.g., missing header file x.h) from the build output.
​Interactive Approval: When a missing dependency is detected, the user is presented with the required apt package name and an interactive prompt to explicitly approve running the necessary command (sudo apt install [package-name]) to continue the installation.

​3. Package Inspection and Security (LibRARx)
​Visual Review: Before installation begins, a dedicated dialog window (LibRARx) presents the file and folder structure of the archive in a tree view.
​Script Highlighting: Potentially dangerous executable scripts (.sh, .py, .pl) are automatically highlighted in bold to draw the user's attention.
​Transparency: Users can view the content of any file, including risky scripts, with a single click.

​4. Post-Installation Management
​File Registry: All file paths installed by a package (e.g., /usr/bin, /usr/local/lib, etc.) are meticulously recorded in a local SQLite database (~/.config/library/library.db).
​Future Uninstallation: This registry is the foundation for a future feature to completely and cleanly remove (uninstall) installed software from the system.
### ​🛠️ Setup and Running
​Follow these steps to get LibRARy running on your system:
​Prerequisites
​Python 3.x
​A Debian or Ubuntu-based Linux distribution (Dependency detection relies on the apt system).

​1. Clone the Repository
> git clone [https://github.com/](https://github.com/mNelty/LibRARy.git)

> cd LibRARy

2. Install Dependencies
​Install the necessary Python packages required for the application to run:

> pip install PyQt5

3. Launch the Application
​To start the main window:

> python run.py

#### 🚀 How to Use
- ​Launch: Start the application using the command above.
- ​Drag-and-Drop: Drag and drop your desired .tar.gz file onto the main window.
- ​Inspection (LibRARx): Review the files and scripts in the security dialog. Click "Proceed" to continue.
- Automation: LibRARy will automatically begin the extraction, configuration, and compilation steps.
- Interaction: When a dependency is missing, approve the installation command in the pop-up window.
- Completion: The application will notify you when the installation is successfully completed.
#### ​🤝 Contributing
​LibRARy is an open-source project aimed at serving the Linux user community. We welcome bug reports, feature suggestions, and code contributions.
​Open an Issue for bugs or suggestions.
​Develop new features or fixes on a separate branch.
​Submit a Pull Request to merge your changes into the main branch.
#### ​⚖️ License
​This project is licensed under the MIT License. See the LICENSE file for more details.