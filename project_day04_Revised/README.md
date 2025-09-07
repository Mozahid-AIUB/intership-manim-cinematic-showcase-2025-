# Project CinematicStarship

A cinematic **2D space journey animation** built with [Manim](https://www.manim.community/).  
This project showcases a rocket launch from Earth, orbital refueling, interplanetary travel, and a landing on Mars — complete with a branded intro and outro.

---

## 📂 Project Structure
```
CinematicStarship/
│── assets/ # Assets folder
│ └── logo.png # Company logo
│
│── scenes/ # All scene scripts
│ ├── intro.py # Intro animation
│ ├── outro.py # Outro animation
│ └── main_scenes.py # Main cinematic scenes
│
│── venv/ # Virtual environment (not tracked in Git)
│
│── main.py # Master file that runs everything
│── README.md # Project documentation
```

## 🎥 Scenes Overview

1. **Intro Scene (`intro.py`)**  
   - Animated parallax background with stars & particles  
   - Company logo glow effect  
   - Cinematic title and tagline  

2. **Main Scenes (`main_scenes.py`)**  
   - **Scene 1 (s1_launch):** Rocket launch sequence from Earth.  
   - **Scene 2 (s2_orbit):** Rocket docks at a space station, refuels, and heads toward Mars.  
   - **Scene 3 (s3_transfer):** Rocket lands on the Martian surface with cinematic background.  

3. **Outro Scene (`outro.py`)**  
   - "Thanks for Watching" outro animation  
   - Branding with **Imran’s Lab**  

---

## ⚙️ Installation & Setup

Clone the repository:

```bash
git clone https://github.com/your-username/CinematicStarship.git
cd CinematicStarship
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
Install dependencies:

bash
Copy code
pip install manim
▶️ Running the Project
To render the full cinematic video:

bash
Copy code
manim -pqh main.py MasterScene
-p → Preview after rendering

-qh → High-quality output (you can use -pql for faster low-quality preview)

The output .mp4 file will be generated in the media/videos/ directory.