# 📸 copyright-free-image-viewer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Copyright-free-image-viewer** is a robust, open-source media procurement and curation platform. It unifies search, review, and asset management processes into a single, elegant interface, connecting seamlessly to major stock image providers (Pexels, Pixabay, Unsplash, Flickr) to streamline your creative workflow.

## 🚀 Key Features

### 🔍 Unified Search & Curation
- **Multi-API Support**: Fetch high-quality images simultaneously from **Pexels**, **Pixabay**, **Unsplash**, and **Flickr**.
- **Smart Queue**: Automatic deduplication and session management ensure you never review the same image twice.
- **Tinder-Style Review**: Rapidly build your collection with a "Yes/No" swipe interface designed for speed.

### 📂 Advanced Asset Explorer
- **Visual File System**: Browse your project's physical directory structure directly from the web interface.
- **Maintenance Actions**:
  - **WebP Conversion**: Batch convert your entire library to optimized WebP format with one click.
  - **Refetch**: Automatically replenish your queue for specific terms from any API source.
  - **Data Export**: Export your entire database metadata to **JSON** or **CSV** formats for external analysis.

### 🖼️ Dynamic Gallery
- **Filtering**: Powerful search bar to filter assets by image ID, source API, or keyword tags.
- **Management**: Delete individual images or bulk-clear entire categories.
- **Download**: One-click **ZIP** export of your curated selection for immediate use in projects.

### 🛠️ Production Ready
- **Dockerized**: specific `docker-compose` setup for instant, reproducible deployments.
- **Robust Logging**: Detailed logging system tracks every API call, download, and error for total transparency.
- **Database Persistence**: SQLite integration ensures your curation decisions and metadata are safely stored.

---

## 🛠 Installation & Setup

### Option 1: Docker (Recommended)
The fastest way to get started. ensuring a clean environment.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AtaCanYmc/copyright-free-image-viewer.git
   cd copyright-free-image-viewer
   ```

2. **Configure Environment:**
   Create a `.env` file in the root directory (use `.env.example` as a template):
   ```env
   # API Keys (Get these from respective developer portals)
   PEXELS_API_KEY=your_key_here
   PIXABAY_API_KEY=your_key_here
   UNSPLASH_ACCESS_KEY=your_key_here
   FLICKR_API_KEY=your_key_here

   # Configuration
   APP_PORT=8080
   DEBUG=True
   ```

3. **Launch:**
   ```bash
   docker-compose up --build <project_name>
   ```
   Visit **http://localhost:8080** to start curating.

### Option 2: Local Python Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application:**
   ```bash
   python app.py <project_name>
   ```

---

## 📖 Usage Workflow

### 1. Project Setup
- Open the app and navigate to **Step 1: Setup**.
- Enter your desired search terms (e.g., "mountain landscape", "cyberpunk city"). These terms drive the initial image fetching process.

### 2. Curation (Review)
- Go to **Step 2: Review**.
- You will see images fetched from your configured APIs.
- **Approve (Green)** to download high-res version to your local library.
- **Reject (Red)** to skip.
- **Switch API**: Use the buttons to toggle between Pexels, Pixabay, etc., to find the best variety.

### 3. Management (Explorer)
- Navigate to the **Explorer** tab to manage your assets.
- View the folder structure of downloaded images.
- **Actions Menu**:
  - **Convert to WebP**: optimize storage space.
  - **Export Data**: Generate `images.csv` or `images.json` from your curation database.
  - **Maintenance**: Clear database or delete specific file groups.

### 4. Final Review & Export (Gallery)
- The **Gallery** shows all your approved assets.
- Use the **Search Bar** to verify specific images.
- Click **"Download Project as ZIP"** in the header to bundle everything for your creative work.

---

## 🤝 Contributing

We welcome contributions to make Copyright-free-image-viewer even better!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Built with ❤️ by Open Source Contributors
</p>